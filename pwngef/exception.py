#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools
import pdb
import sys
import traceback

import gdb

import pwngef.color.message as message
import pwngef.config
import pwngef.memoize
import pwngef.stdio

try:
    import ipdb as pdb
except ImportError:
    pass

verbose = pwngef.config.set('self.exception_verbose', False, 'whether to print a full stacktracefor exceptions raised in Pwndbg commands')
debug = pwngef.config.set('self.exception_debugger', False, 'whether to debug exceptions raised in Pwndbg commands')


@pwngef.memoize.forever
def inform_report_issue(exception_msg):
    """
    Informs user that he can report an issue.
    The use of `memoize` makes it reporting only once for a given exception message.
    """
    print(message.notice(
        "If that is an issue, you can report it on https://github.com/pwngef/pwngef/issues\n"
        "(Please don't forget to search if it hasn't been reported before)\n"
        "To generate the report and open a browser, you may run ") +
        message.hint("`bugreport --run-browser`") +
        message.notice("\nPS: Pull requests are welcome")
    )


def handle(name='Error'):
    """Displays an exception to the user, optionally displaying a full traceback
    and spawning an interactive post-moretem debugger.

    Notes:
        - ``set exception-verbose on`` enables stack traces.
        - ``set exception-debugger on`` enables the post-mortem debugger.
    """

    # This is for unit tests so they fail on exceptions instead of displaying them.
    if getattr(sys, '_pwngef_unittest_run', False) is True:
        E, V, T = sys.exc_info()
        e = E(V)
        e.__traceback__ = T
        raise e

    # Display the error
    if debug or verbose:
        exception_msg = traceback.format_exc()
        print(exception_msg)
        inform_report_issue(exception_msg)

    else:
        exc_type, exc_value, exc_traceback = sys.exc_info()

        print(message.error('Exception occured: {}: {} ({})'.format(name, exc_value, exc_type)))

        print(message.notice('For more info invoke `') +
              message.hint('gef config gef.exception_verbose True') +
              message.notice('` and rerun the command\nor debug it by yourself with `') +
              message.hint('gef config gef.exception_debugger True') +
              message.notice('`'))

    # Break into the interactive debugger
    if debug:
        with pwngef.stdio.stdio:
            pdb.post_mortem()


@functools.wraps(pdb.set_trace)
def set_trace():
    """Enable sane debugging in Pwndbg by switching to the "real" stdio.
    """
    debugger = pdb.Pdb(stdin=sys.__stdin__,
                       stdout=sys.__stdout__,
                       skip=['pwngef.stdio', 'pwngef.exception'])
    debugger.set_trace()


pdb.set_trace = set_trace


# @pwngef.config.Trigger([verbose, debug])
@pwngef.events.cont
def update(event):
    verbose = pwngef.config.get('gef.exception_verbose')
    debug = pwngef.config.get('gef.exception_debugger')
    if verbose or debug:
        command = 'set python print-stack full'
    else:
        command = 'set python print-stack message'
    gdb.execute(command, from_tty=True, to_string=True)
