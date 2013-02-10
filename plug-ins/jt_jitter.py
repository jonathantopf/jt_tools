
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

# use...
# import maya
# maya.cmds.loadPlugin("jt_jitter.py")
# maya.cmds.sphere()
# maya.cmds.deformer( type='jt_jitter' )

import math, sys

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

import random

kPluginNodeTypeName = "jt_jitter"
jt_jitter_node_id = OpenMaya.MTypeId(0x6497)

# Node definition
class jt_jitter(OpenMayaMPx.MPxDeformerNode):
	# class variables
	angle = OpenMaya.MObject()

	# constructor
	def __init__(self):
		OpenMayaMPx.MPxDeformerNode.__init__(self)

	# deform
	def deform(self,dataBlock,geomIter,matrix,multiIndex):

		seedHandle = dataBlock.inputValue( self.seed )
		seedValue = seedHandle.asFloat()

		multiplierHandle = dataBlock.inputValue( self.multiplier )
		multiplierValue = multiplierHandle.asFloat()

		all_points = OpenMaya.MPointArray()


		# iterate over the object and change the angle
		while geomIter.isDone() == False:
			point = geomIter.position()

			random.seed(seedValue + geomIter.index())

			x_rand = multiplierValue * random.random()
			y_rand = multiplierValue * random.random()
			z_rand = multiplierValue * random.random()

			random_vector = OpenMaya.MVector(x_rand, y_rand, z_rand)

			all_points.append( point + random_vector)
			geomIter.next()

		geomIter.setAllPositions(all_points)
				
# creator
def nodeCreator():
	return OpenMayaMPx.asMPxPtr( jt_jitter() )

# initializer
def nodeInitializer():

	nAttr = OpenMaya.MFnNumericAttribute()

	# angle
	jt_jitter.seed = nAttr.create( "seed", "sd", OpenMaya.MFnNumericData.kFloat, 1.0 )
	nAttr.setKeyable(1)
	# multiplier
	jt_jitter.multiplier = nAttr.create( "multiplier", "mu", OpenMaya.MFnNumericData.kFloat, 1.0 )
	nAttr.setKeyable(1)

	# add attribute
	# try:
	outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
	jt_jitter.addAttribute( jt_jitter.multiplier )
	jt_jitter.addAttribute( jt_jitter.seed )
	jt_jitter.attributeAffects( jt_jitter.multiplier, outputGeom )
	jt_jitter.attributeAffects( jt_jitter.seed, outputGeom )
	# except:
	# 	cmds.error( "Failed to create attributes of %s node\n", kPluginNodeTypeName )




# initialize the script plug-in
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	mplugin.registerNode( kPluginNodeTypeName, jt_jitter_node_id, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDeformerNode )
	# cmds.error( "Failed to register node: %s\n" % kPluginNodeTypeName )

# uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	mplugin.deregisterNode( jt_jitter_node_id )
	# except:
	# 	cmds.error( "Failed to unregister node: %s\n" % kPluginNodeTypeName )

	
