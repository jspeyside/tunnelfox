import sys
from contextlib import contextmanager
from datetime import datetime
from StringIO import StringIO


def total_seconds(delta):
    return (delta.microseconds +
            (delta.seconds + delta.days * 24 * 3600) * 10.0 ** 6) / 10.0 ** 6


@contextmanager
def capture_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class BaseTest(object):
    TEST_START = None

    @classmethod
    def setup_class(cls):
        cls.TEST_START = datetime.utcnow()

    @classmethod
    def teardown_class(cls):
        now = datetime.utcnow()
        seconds = total_seconds(now - cls.TEST_START)
        sys.stdout.write('\n{} took {} seconds\n'.format(cls.__name__,
                                                         seconds))
