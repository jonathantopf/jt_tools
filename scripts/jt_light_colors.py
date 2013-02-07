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

    
