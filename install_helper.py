
#
# Copyright (c) 2013 Jonathan Topf
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


import sys
import os
import maya.cmds as cmds
import sys
import inspect

def install(module_dir, install_dir):

    installation_name = 'jt_tools'

    if not os.path.exists(module_dir):
        os.mkdir(module_dir)

    file = open(os.path.join(module_dir, installation_name + '.mod'), 'w')

    module_definition = """

+ jt_tools 0.0.1 {0}

icons: icons 
scripts: sctpts 
#presets: presets """.format(install_dir)

    file.write(module_definition)

    file.close()



    current_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    sys.path.append(os.path.join(current_script_path, 'scripts'))
    import jt_tools    
    jt_tools.create_shelf('jt_tools')
    sys.path.remove(os.path.join(current_script_path, 'scripts'))

    cmds.confirmDialog(title=installation_name + ' install', message='All done!, just restart and enable and plugins not already enabled in the plugin manager. jt', button='OK')
