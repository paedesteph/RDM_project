import re
from pygcam.error import GcamSolverError, GcamError

# Match e.g., "The following model periods did not solve: 8,"
failedPeriods = 'The following model periods did not solve:'
pattern = re.compile(f'.*{failedPeriods}(.*)')

def failedPeriodsFilter(line):
    """
    Default filter for GCAM wrapper. Return True if process should be terminated.

    :param line: (str) a single line of text emitted by GCAM to stdout.
    :return: (GcamError or None): If not None, caller raises the given error
        and terminates the GCAM process.
    """

    match = re.search(pattern, line)

    if match:
        s = match.group(1)

        # Eliminate blank after trailing comma
        periods = [period.strip() for period in s.split(',') if period]

        # N.B. we're presumably running in a sandbox's "exe" directory
        with open('failed_periods.txt', 'w') as f:
            f.write(','.join(periods))
            f.write('\n')

    # Could match other strings and abort GCAM by returning an error object, e.g.,
    # return GcamError("some message")

    return None # don't kill the GCAM process
