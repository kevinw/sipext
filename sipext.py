import os.path
import sys
import shlex
import subprocess


def read_module_name(sip_file):
    '''
    Searches sip_file for a %Module declaration and returns the module
    name as a string.
    '''
    for line in open(sip_file):
        if line.startswith('%Module'):
            return line.split()[1]

    raise Exception('could not read %Module name from %r' % sip_file)

class PythonExtension(object):
    def __init__(self, sip_file):

        if not os.path.isfile(sip_file):
            raise Exception('file not found: %r' % sip_file)
        self.sip_file = sip_file
        self.gendir = opts.gendir

    def build(self):
        spawn_sip(self.sipdir, self.gendir)


def parse_sbf(filename):
    '''
    Parses the SBF file emitted by SIP after it generates sources for a module.

    Returns a mapping of the following form:

    {'target':  'the module name',
     'sources': ['generated_src.cpp', 'generated_src2.cpp', ...]
     'headers': ['generated_header.h', 'generated_header2.h', ...]}
    '''

    sbfdict = {}
    for line in open(filename):
        key, sep, value = line.partition(' = ')
        if value:
            assert not key in sbfdict
            if key == 'sources':
                value = value.split()
            sbfdict[key] = value

    assert all(k in sbfdict for k in ('target', 'sources', 'headers'))
    return sbfdict


def spawn_sip(sipfile, generated_src_dir):
    name, _ext = os.path.splitext(sipfile)

    # need to create generated_src_dir if it doesn't exist
    if not os.path.isdir(generated_src_dir):
        os.makedirs(generated_src_dir)

    # ask SIP to create a SBF file so we know which sources were generated
    sbf_filename = os.path.join(generated_src_dir, '%s.sbf' % name)

    import sipconfig
    cfg = sipconfig.Configuration()
    
    args = [
        cfg.sip_bin,
        '-c', generated_src_dir,  # generated sources go here
        '-b', sbf_filename,       # SBF output file describing the module's inputs
    ]

    args.append(sipfile)

    # spawn SIP, ensuring that a new SBF file is created
    mtime = os.path.getmtime(sbf_filename) if os.path.isfile(sbf_filename) else 0
    run(args)
    assert os.path.getmtime(sbf_filename) > mtime

    return parse_sbf(sbf_filename)


def run(args, checkret = True, expect_return_code = 0):
    '''
    Runs cmd.

    If the process returns 0, returns the contents of stdout.
    Otherwise, raises an exception showing the error code and stderr.
    '''

    if os.name == 'nt':
        if isinstance(args, basestring):
            args = shlex.split(args.replace('\\', '\\\\'))

    #inform('\n%s\n' % ' '.join(args))

    try:
        process = subprocess.Popen(args)
    except WindowsError:
        print >>sys.stderr, 'Error using Popen: args were %r' % args
        raise

    stdout, stderr = process.communicate()
    retcode = process.returncode

    if checkret and retcode != expect_return_code:
        sys.exit(retcode)

    return stdout

def parse_args():
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--sip',
                 help = 'specify the path to a SIP install',
                 default = 'generated')
    p.add_option('--gendir',
                 help = 'directory generated sources will be placed in',
                 default = 'generated')

    p.print_help()

    global opts
    opts = p.parse_args()

if __name__ == '__main__':
    parse_args()

