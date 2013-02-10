
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


import maya.cmds as cmds

def load_ui():

    # values from http://planetpixelemporium.com/tutorialpages/light.html

    light_colors = {
        'candle'                    : (255, 147, 41 ),
        'tungesten_40w'             : (255, 197, 143),
        'tungesten_100w'            : (255, 214, 170),
        'halogen'                   : (255, 241, 224),
        'carbon_arc'                : (255, 250, 244),
        'high_noon_sun'             : (255, 255, 251),
        'direct_sunlight'           : (255, 255, 255),
        'overcast'                  : (201, 226, 255),
        'clear_blue_sky'            : (64 , 156, 255),
        'fluorescent'               : (244, 255, 250),
        'warm_fluorescent'          : (255, 244, 229),
        'cool_white_fluorescent'    : (212, 235, 255),
        'full_Spectrum_fluorescent' : (255, 244, 242),
        'grow_light_fluorescent'    : (255, 239, 247),
        'black_light_flourescent'   : (167, 0  , 255),
        'mercury_vapor'             : (216, 247, 255),
        'sodium_vapor'              : (255, 209, 178),
        'metal_halide'              : (242, 252, 255),
        'high_pressure_sodium'      : (255, 183, 76 )
    }

    window = cmds.loadUi('JT_LightColors.ui')

    cmds.showUi(window)

    
