import os.path

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
        self.name = read_module_name(sip_file)

def build_python_extension(sip_file):
    pass

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


def parse_args():
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--sip',
                 help = 'specify the path to a SIP install',
                 type = 'string')

    p.print_help()
    opts = p.parse_args()
