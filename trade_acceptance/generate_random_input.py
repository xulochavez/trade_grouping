import random


if __name__ == '__main__':
    for no_of_trades in [100, 1000, 10000, 100000, 1000000, 10000000]:
        with open(f'input_{no_of_trades}.xml', 'w') as fle:
            fle.write('<Trades>\n')
            correlation_ids = list(range(no_of_trades // 5))
            group_properties = {corr_id: {'limit': random.randint(0, 10) * 100,
                                          'no_of_trades': random.randint(1, 5)}
                                for corr_id in correlation_ids}

            for trade_id in range(no_of_trades):
                corr_id = random.choice(correlation_ids)
                limit = group_properties[corr_id]['limit']
                no_of_trades = group_properties[corr_id]['no_of_trades']
                value = random.choice([50, 100, 200])

                fle.write(f'<Trade CorrelationId="{corr_id}" NumberOfTrades="{no_of_trades}" Limit="{limit}" TradeID="{trade_id}">{value}</Trade>\n')

            fle.write('</Trades>\n')

