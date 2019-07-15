
import csv
from collections import namedtuple
import xml.etree.ElementTree as ET
import logging
import os
import psutil

Record = namedtuple('Record', 'correlation_id number_of_trades limit trade_id value')
GroupStatus = namedtuple('GroupStatus', 'CorrelationID NumberOfTrades State')


def group_status_from_record(record, status):
    return GroupStatus(record.correlation_id, record.number_of_trades, status)


def get_records_iterator(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    for el in root.findall('Trade'):
        yield Record(el.get('CorrelationId'), int(el.get('NumberOfTrades')), int(el.get('Limit')),
                     el.get('TradeID'), int(el.text))


class RecordClassifier:

    def __init__(self):
        self.cumulative = {}

    def get_trade_group_statuses(self, records):
        for record in records:
            status = self._get_group_status_from_record(record)
            #logging.info(f'cumulative: {self.cumulative}')
            if status is not None:
                yield group_status_from_record(record, status)

        yield from self._pending_groups()

    def _get_group_status_from_record(self, record):
        if record.number_of_trades == 1:
            return self._single_trade_group_status(record)
        else:
            return self._multi_trade_group_status(record)

    def _single_trade_group_status(self, record):
        if record.value <= record.limit:
            return 'Accepted'
        else:
            return 'Rejected'

    def _multi_trade_group_status(self, record):
        cumulative_values = self.cumulative.setdefault(record.correlation_id, {})
        running_count = cumulative_values.get('count', 0) + 1
        running_total = cumulative_values.get('total', 0) + record.value
        if running_total > record.limit:
            self._remove_group_from_cumulative(record)
            return 'Rejected'
        elif running_count == record.number_of_trades:
            self._remove_group_from_cumulative(record)
            return 'Accepted'
        # malformed record where one trade for a group has a different (lower) number of trades
        # TODO: case where there are more trades than number of trades not dealt with!
        # (It would create a second entry for  same corr id)
        elif running_count > record.number_of_trades:
            logging.error(f'Running count for corr id {record.correlation_id} ({running_count}) '
                          f'is greater than number of trades for record {record}.'
                          f'It will be kept as pending with previous number of trades: '
                          f'{cumulative_values.get("number_of_trades", 0)}')
            cumulative_values.update({'number_of_trades': cumulative_values.get("number_of_trades", 0),
                                      'count': running_count,
                                      'total': running_total})
            return None
        else:
            cumulative_values.update({'number_of_trades': record.number_of_trades,
                                      'count': running_count,
                                      'total': running_total})
            return None

    def _remove_group_from_cumulative(self, record):
        del self.cumulative[record.correlation_id]

    def _pending_groups(self):
        for correlation_id, cumulative_values in self.cumulative.items():
            yield GroupStatus(correlation_id, cumulative_values['number_of_trades'], 'Pending')


def sort_groups_by_corr_id(groups):
    groups_by_corr_id = {}
    for group in groups:
        groups_by_corr_id[group.CorrelationID] = group

    # numerical (rather than lexical) sorting by correlation id
    for corr_id in sorted(groups_by_corr_id, key=lambda x: int(x)):
        yield groups_by_corr_id[corr_id]


def main(input_path, output_path='results.csv'):
    logging.info(f'Processing trades from {input_path}, saving results to {output_path}')
    records = get_records_iterator(input_path)
    groups = RecordClassifier().get_trade_group_statuses(records)
    sorted_groups = sort_groups_by_corr_id(groups)

    with open(output_path, 'w') as out:
        writer = csv.writer(out)
        writer.writerow(GroupStatus._fields)
        writer.writerows(sorted_groups)

    process = psutil.Process(os.getpid())
    logging.info(f'Processing completed. Memory used: {process.memory_info()[0] / 2**10} kb')


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='xml input file path')
    args = parser.parse_args()

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler('server.log', mode='w')
    file_handler.setLevel(logging.INFO)
    log.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    log.addHandler(console_handler)

    try:
        main(args.input)
    except Exception:
        logging.exception(f"Unexpected error while processing {args.input}")






