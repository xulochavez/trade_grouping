
import pytest
from trade_acceptance.bnp_test import (get_records_iterator, RecordClassifier,Record, GroupStatus,
                                       sort_groups_by_corr_id, main)


@pytest.fixture
def records(shared_datadir):
    return get_records_iterator(shared_datadir / 'input.xml')


def test_get_records_iterator(shared_datadir):
    records = get_records_iterator(shared_datadir / 'input.xml')

    expected = [Record(correlation_id='234', number_of_trades=3, limit=1000, trade_id='654', value=100),
                Record(correlation_id='234', number_of_trades=3, limit=1000, trade_id='135', value=200),
                Record(correlation_id='222', number_of_trades=1, limit=500, trade_id='423', value=600),
                Record(correlation_id='234', number_of_trades=3, limit=1000, trade_id='652', value=200),
                Record(correlation_id='200', number_of_trades=2, limit=1000, trade_id='645', value=1000)]

    actual = list(records)

    assert expected == actual


def test_get_group_status_from_record():
    classifier = RecordClassifier()

    record = Record('222', 1, 500, '423', 600)
    status = classifier._get_group_status_from_record(record)
    assert 'Rejected' == status

    record = Record('222', 1, 500, '423', 400)
    status = classifier._get_group_status_from_record(record)
    assert 'Accepted' == status

    classifier.cumulative = {'222': {'count': 1, 'total': 300}}
    record = Record('222', 2, 500, '423', 200)
    status = classifier._get_group_status_from_record(record)
    assert 'Accepted' == status

    classifier.cumulative = {'222': {'count': 1, 'total': 300}}
    record = Record('222', 2, 500, '423', 300)
    status = classifier._get_group_status_from_record(record)
    assert 'Rejected' == status

    classifier.cumulative = {'222': {'count': 1, 'total': 300}}
    record = Record('222', 3, 600, '423', 200)
    status = classifier._get_group_status_from_record(record)
    assert status is None


def test_pending_groups():
    classifier = RecordClassifier()
    record = Record('222', 3, 600, '423', 200)
    _status = classifier._get_group_status_from_record(record)
    expected = [GroupStatus('222', 3, 'Pending')]
    actual = list(classifier._pending_groups())
    assert expected == actual


def test_get_trade_group_statuses(records):
    classifier = RecordClassifier()

    expected = [GroupStatus(CorrelationID='222', NumberOfTrades=1, State='Rejected'),
                GroupStatus(CorrelationID='234', NumberOfTrades=3, State='Accepted'),
                GroupStatus(CorrelationID='200', NumberOfTrades=2, State='Pending')]

    actual = list(classifier.get_trade_group_statuses(records))

    assert expected == actual


def test_sort_groups_by_corr_id():

    groups = [GroupStatus(CorrelationID='222', NumberOfTrades=1, State='Rejected'),
              GroupStatus(CorrelationID='234', NumberOfTrades=3, State='Accepted'),
              GroupStatus(CorrelationID='200', NumberOfTrades=2, State='Pending')]

    expected = [GroupStatus(CorrelationID='200', NumberOfTrades=2, State='Pending'),
                GroupStatus(CorrelationID='222', NumberOfTrades=1, State='Rejected'),
                GroupStatus(CorrelationID='234', NumberOfTrades=3, State='Accepted')]

    actual = list(sort_groups_by_corr_id(groups))

    assert expected == actual


def test_end_to_end(shared_datadir):
    input = shared_datadir / 'input.xml'
    output = shared_datadir / 'results.csv'
    main(input, output)

    with open(shared_datadir / 'results.csv') as results_fle:
        actual = results_fle.readlines()
    with open(shared_datadir / 'expected_results.csv') as expected_results_fle:
        expected = expected_results_fle.readlines()
    assert expected == actual







