import sys
sys.path.append('..')

import sipext


spam = sipext.PythonModule('spam.sip')
spam.build()

