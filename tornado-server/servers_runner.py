from multiprocessing import Pool
import os
from optparse import OptionParser
import subprocess


def run_subprocess(port):
    subprocess.call("python server.py -port=%d" % port, shell=True)


def main():
    parser = OptionParser()
    parser.add_option('--count')
    (options, args) = parser.parse_args()

    start_port = 9001
    finish_port = start_port + int(options.count)

    results = []
    for port in range(start_port, finish_port):
        pool = Pool(processes=4)
        results.append(pool.apply_async(run_subprocess, [port]))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'