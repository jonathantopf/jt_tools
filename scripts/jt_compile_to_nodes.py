
#
# Copyright (c) 2014 Jonathan Topf
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


#--------------------------------------------------------------------------------------------------
# GenericNode. All classes derive from this
#--------------------------------------------------------------------------------------------------

class GenericNode(object):
    def __init__(self):
        self.output_attr = None
        self.inputs = {}
        self.nodes = []
        
    def compile(self):
        pass

    def collect_inputs(self):
        for key, value in self.inputs.items():
            if issubclass(value.__class__, GenericNode):
                value.compile()
                self.nodes += value.nodes

    def bind_input(self, x, attr):
        x_class =  x.__class__.__name__
        if x_class == 'int' or x_class == 'float': # is numeric value
            cmds.setAttr(attr, x)
        elif issubclass(x.__class__, GenericNode): # is decendant of GenericNode
            cmds.connectAttr(x.output_attr, attr)
        else:
            cmds.connectAttr(x, attr)
            

#--------------------------------------------------------------------------------------------------
# Mult.
#--------------------------------------------------------------------------------------------------

class Mult(GenericNode):
    def __init__(self, input_1, input_2):
        super(Mult, self).__init__()
        self.inputs['input_1'] = input_1
        self.inputs['input_2'] = input_2
        
    def compile(self):
        mult_node = cmds.createNode('multiplyDivide')
        self.output_attr = mult_node + '.outputX'
        self.collect_inputs()
        self.bind_input(self.inputs['input_1'], mult_node + '.input1X')
        self.bind_input(self.inputs['input_2'], mult_node + '.input2X')
        self.nodes.append(mult_node)

        return self.output_attr, self.nodes 


#--------------------------------------------------------------------------------------------------
# Divide.
#--------------------------------------------------------------------------------------------------

class Divide(GenericNode):
    def __init__(self, input_1, input_2):
        super(Divide, self).__init__()
        self.inputs['input_1'] = input_1
        self.inputs['input_2'] = input_2
        
    def compile(self):
        mult_node = cmds.createNode('multiplyDivide')
        cmds.setAttr(mult_node + '.operation', 2)
        self.output_attr = mult_node + '.outputX'
        self.collect_inputs()
        self.bind_input(self.inputs['input_1'], mult_node + '.input1X')
        self.bind_input(self.inputs['input_2'], mult_node + '.input2X')
        self.nodes.append(mult_node)

        return self.output_attr, self.nodes 


#--------------------------------------------------------------------------------------------------
# Pow.
#--------------------------------------------------------------------------------------------------

class Pow(GenericNode):
    def __init__(self, input_1, exponent):
        super(Pow, self).__init__()
        self.inputs['input_1'] = input_1
        self.inputs['exponent'] = exponent
        
    def compile(self):
        mult_node = cmds.createNode('multiplyDivide')
        cmds.setAttr(mult_node + '.operation', 3)
        self.output_attr = mult_node + '.outputX'
        self.collect_inputs()
        self.bind_input(self.inputs['input_1'], mult_node + '.input1X')
        self.bind_input(self.inputs['exponent'], mult_node + '.input2X')
        self.nodes.append(mult_node)

        return self.output_attr, self.nodes 


#--------------------------------------------------------------------------------------------------
# Add.
#--------------------------------------------------------------------------------------------------

class Add(GenericNode):
    def __init__(self, input_1, input_2):
        super(Add, self).__init__()
        self.inputs['input_1'] = input_1
        self.inputs['input_2'] = input_2
        
    def compile(self):
        add_node = cmds.createNode('plusMinusAverage')
        self.output_attr = add_node + '.output1D'
        self.collect_inputs()
        self.bind_input(self.inputs['input_1'], add_node + '.input1D[0]')
        self.bind_input(self.inputs['input_2'], add_node + '.input1D[1]')
        self.nodes.append(add_node)

        return self.output_attr, self.nodes 


#--------------------------------------------------------------------------------------------------
# Minus.
#--------------------------------------------------------------------------------------------------

class Minus(GenericNode):
    def __init__(self, input_1, input_2):
        super(Minus, self).__init__()
        self.inputs['input_1'] = input_1
        self.inputs['input_2'] = input_2
        
    def compile(self):
        add_node = cmds.createNode('plusMinusAverage')
        cmds.setAttr(add_node + '.operation', 2)
        self.output_attr = add_node + '.output1D'
        self.collect_inputs()
        self.bind_input(self.inputs['input_1'], add_node + '.input1D[0]')
        self.bind_input(self.inputs['input_2'], add_node + '.input1D[1]')
        self.nodes.append(add_node)

        return self.output_attr, self.nodes 


#--------------------------------------------------------------------------------------------------
# Clamp.
#--------------------------------------------------------------------------------------------------

class Clamp(GenericNode):
    def __init__(self, input_1, minimum=0, maximum=1):
        super(Clamp, self).__init__()
        self.inputs['input'] = input_1
        self.inputs['min'] = minimum
        self.inputs['max'] = maximum
        
    def compile(self):
        clamp_node = cmds.createNode('clamp')
        self.output_attr = clamp_node + '.outputR'
        self.collect_inputs()
        self.bind_input(self.inputs['input'], clamp_node + '.inputR')
        self.bind_input(self.inputs['min'],   clamp_node + '.minR')
        self.bind_input(self.inputs['max'],   clamp_node + '.maxR')
        self.nodes.append(clamp_node)

        return self.output_attr, self.nodes 


#--------------------------------------------------------------------------------------------------
# Blend.
#--------------------------------------------------------------------------------------------------

class Blend(GenericNode):
    def __init__(self, input_1, input_2, blend):
        super(Blend, self).__init__()
        self.inputs['input_1'] = input_1
        self.inputs['input_2'] = input_2
        self.inputs['blend']   = blend
        
    def compile(self):
        blend_node = cmds.createNode('blendColors')
        self.output_attr = blend_node + '.outputR'
        self.collect_inputs()
        self.bind_input(self.inputs['input_1'], blend_node + '.color1R')
        self.bind_input(self.inputs['input_2'], blend_node + '.color2R')
        self.bind_input(self.inputs['blend'],   blend_node + '.blender')
        self.nodes.append(blend_node)

        return self.output_attr, self.nodes 







