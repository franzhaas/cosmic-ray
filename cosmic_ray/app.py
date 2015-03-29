"""cosmic-ray

Usage:
  cosmic-ray [options] <module> <test-dir>

Options:
  -h --help          Show this screen.
  --verbose          Produce verbose output
  --no-local-import  Allow importing module from the current directory
"""
import functools
import logging
import multiprocessing
import sys

import docopt

import cosmic_ray.find_modules
from cosmic_ray.mutating import create_mutants, run_with_mutant
import cosmic_ray.operators
import cosmic_ray.testing


log = logging.getLogger()


def format_response(outcome, activation_record, reason):
    """Returns a reasonably formatted string with test outcome,
    activation-record information, and reason.
    """
    return '{outcome} -> {desc} @ {filename}:{lineno}\n{reason}'.format(
        outcome=outcome,
        desc=activation_record['description'],
        filename=activation_record['filename'],
        lineno=activation_record['line_number'],
        reason=reason)


def hunt(mutation_records, test_function):
    """Call `test_function` for each mutant in `mutation_records`.

    Returns a sequence of the values returned by `test_function`.
    """
    with multiprocessing.Pool() as p:
        yield from p.map(
            functools.partial(run_with_mutant, test_function),
            mutation_records)


def main():
    arguments = docopt.docopt(__doc__, version='cosmic-ray v.2')
    if arguments['--verbose']:
        logging.basicConfig(level=logging.INFO)

    if not arguments['--no-local-import']:
        sys.path.insert(0, '')

    modules = cosmic_ray.find_modules.find_modules(arguments['<module>'])

    operators = cosmic_ray.operators.all_operators()

    test_function = functools.partial(cosmic_ray.testing.run_tests,
                                      arguments['<test-dir>'])

    results = hunt(
        create_mutants(modules, operators),
        test_function)

    for r in results:
        print(r)

if __name__ == '__main__':
    main()
