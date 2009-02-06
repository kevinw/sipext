import os
import shlex
import subprocess
import sys

def run(args, checkret = True, expect_return_code = 0, env = None):
    '''
    Runs cmd.

    If the process returns 0, returns the contents of stdout.
    Otherwise, raises an exception showing the error code and stderr.
    '''

    if os.name == 'nt':
        if isinstance(args, basestring):
            args = shlex.split(args.replace('\\', '\\\\'))

    print '\n%s\n' % ' '.join(args)

    try:
        process = subprocess.Popen(args, env = env)
    except WindowsError:
        print >>sys.stderr, 'Error using Popen: args were %r' % args
        raise

    stdout, stderr = process.communicate()
    retcode = process.returncode

    if checkret and retcode != expect_return_code:
        sys.exit(retcode)

    return stdout

