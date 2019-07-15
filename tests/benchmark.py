import time
from trade_acceptance.bnp_test import main
import logging


def time_fn(fn, repeats=3, **kwargs):
    elapsed_times = []
    for _ in range(repeats):
        start_time = time.time()
        fn(**kwargs)
        elapsed_times.append(time.time() - start_time)

    return min(elapsed_times)


def benchmark():
    for no_of_trades in (100, 1000, 10000, 100000, 1000000):#, 10000000):
        input_path = f'data/input_{no_of_trades}.xml'
        fn = main
        kwargs = {'input_path': input_path, 'output_path': f'data/results_{no_of_trades}.csv'}
        best_time = time_fn(fn, repeats=1, **kwargs)
        print(f'calling {fn.__name__} for {no_of_trades} rades takes : {best_time:.6} seconds')


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    benchmark()
