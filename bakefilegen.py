'''
functions for generating bakefile XML
'''

try:
    from xml.etree.cElementTree import Element, SubElement, ElementTree
except ImportError:
    from xml.etree.ElementTree import Element, SubElement, ElementTree

import os.path

from utils import run

def xmlnode(root, name, text = '', **attrs):
    'Simple way to attach an ElementTree node.'

    elem = SubElement(root, name) if root is not None else Element(name)
    if text:
        elem.text = text

    for k, v in attrs.iteritems():
        elem.set(k, v)

    return elem

def project():
    proj =  Element('makefile')
    xmlnode(proj, 'include', file = 'sipext-base.bkl')
    return proj

def add_module(project, module):
    module_xml = xmlnode(project, 'module', id = module.name, template = 'python_extension')

    import sipconfig
    sip_cfg = sipconfig.Configuration()

    xmlnode(module_xml, 'include', sip_cfg.sip_inc_dir)
    xmlnode(module_xml, 'include', sip_cfg.py_inc_dir)
    xmlnode(module_xml, 'lib-path', sip_cfg.py_lib_dir)

    for tagname, attr in (
        ('lib-path', 'libdirs'),
        ('sys-lib',  'libs'),
        ('include',  'includes')):

        value = getattr(module, attr)
        if value: xmlnode(module_xml, tagname, getattr(module, attr))
    
    xmlnode(module_xml, 'sources', '\n'.join(module.sources))

def run_bakefile(project_name, makefile, outputdir = None):
    '''
    Spawns bakefile
    '''
    # First, create the BKL file which will tell bakefile how to create platform
    # specific makefiles.
    bkl = project_name + '.bkl'
    write_xml(makefile, bkl)

    # TODO: support more formats here
    formats = [('msvs2008prj', '%s.sln' % project_name)]

    # create Bakefiles.bkgen
    write_xml(bakefile_gen(bkl, formats), 'Bakefiles.bkgen')

    # define extra variables that are passed to bakefile_gen with -D
    bakefile_vars = dict(
        #WXPY_PYDEBUG = '1' if DEBUG else '0', # link against python25_d.dll
    )

    bakefile_vars_str = ' '.join('-D %s=%s' % (key, value)
        for key, value in bakefile_vars.iteritems())

    env = dict(BAKEFILE_PATHS = os.path.dirname(__file__))

    # This results in Makefile (autotools), SLN (Visual Studio), or other
    # platform specific files.
    run('bakefile_gen' +
        #(' -V' if BAKEFILES_VERBOSE else '') +
        ' ' + bakefile_vars_str,
        env = env)

    if len(formats) > 1:
        raise AssertionError('figure out a better way to return the name of the sln')
    return formats[0][1]

def bakefile_gen(input, formats):
    bakefile_gen = xmlnode(None, 'bakefile-gen',
                           xmlns = 'http://www.bakefile.org/schema/bakefile-gen')

    xmlnode(bakefile_gen, 'input', input)
    xmlnode(bakefile_gen, 'add-formats', ', '.join(compiler for compiler, output in formats))

    for compiler, output in formats:
        xmlnode(bakefile_gen, 'add-flags', '-o%s' % output,
                files   = input,
                formats = compiler)

    return bakefile_gen

def write_xml(node, filename, encoding = 'utf-8'):
    _indent_xml(node) # pretty print xml
    ElementTree(node).write(filename, encoding)

def _indent_xml(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            _indent_xml(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
