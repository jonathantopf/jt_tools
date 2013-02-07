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
