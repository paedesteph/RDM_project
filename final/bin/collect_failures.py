#!/usr/bin/env python
#
# Collect failed_periods.txt files along with the name of the scenario in each case.
#
# Rich Plevin
# 29 MAR 2021
#
import argparse
from pathlib import Path
from pygcam.config import getParam

def parseArgs():
    parser = argparse.ArgumentParser(description='''Collect files written by custom GCAM wrapper into a single file 
                                     with each line containing the name of scenario generating the file.''')

    wrapper_file = './failed_periods.txt'
    parser.add_argument('-f', '--wrapper_file', default=wrapper_file,
                        help=f'''The name of the file created by the custom GCAM wrapper function.
                        Default is '{wrapper_file}'.''')

    collection_file = './collected_wrapper_output.txt'
    parser.add_argument('-o', '--collection_file', default=collection_file,
                        help=f'''The directory into which all normalized XML files are written. 
                        Default is '{collection_file}'.''')

    sandbox_dir = getParam('GCAM.SandboxDir')
    parser.add_argument('-s', '--sandbox_dir', default=None,
                        help=f'''The directory containing folders for the scenarios from which the wrapper output
                        files should be collected. Default is taken from pygcam config variable "GCAM.SandboxDir",
                        currently "{sandbox_dir}".''')

    args = parser.parse_args()
    return args


def main():
    args = parseArgs()

    collection_file = Path(args.collection_file)
    if collection_file.exists():
        collection_file.rename(collection_file.name + '~')

    wrapper_file = args.wrapper_file
    sandbox_dir = Path(args.sandbox_dir or getParam('GCAM.SandboxDir'))

    with open(collection_file, 'w') as output:
        paths = sandbox_dir.glob(f'*/exe/{wrapper_file}')
        for p in paths:
            scenario = p.parent.parent.name
            with open(p, 'r') as input:
                lines = input.readlines()
                for line in lines:
                    output.write(f'{scenario},{line}')

main()
