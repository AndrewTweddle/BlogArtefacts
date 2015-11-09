import bpy
import math

from math import *

# From http://blenderscripting.blogspot.com/2011/05/blender-25-python-selecting-layer.html:
def selectLayer(layer):   
    return tuple(i == layer for i in range(0, 20))

# From http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Materials_and_textures:
def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT' 
    mat.diffuse_intensity = 1.0 
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat
 
def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)

# ************************************************
# Following code by Andrew Tweddle, November 2012:
# ************************************************

# -----------------------------------
# Code common to blocks and hexagons:
# -----------------------------------

class Direction:
    C = 0
    SW = 1
    W = 2
    NW = 3
    NE = 4
    E = 5
    SE = 6

def DirToString(direction):
    if direction == Direction.C:
        return "C"
    elif direction == Direction.SW:
        return "SW"
    elif direction == Direction.W: 
        return "W"
    elif direction == Direction.NW:
        return "NW"
    elif direction == Direction.NE:
        return "NE"
    elif direction == Direction.E:
        return "E"
    else:
        return "SE"


def getNextDir(direction):
    if direction == Direction.C:
        return Direction.C
    elif direction == Direction.SE:
        return Direction.SW
    else:
        return direction + 1

def getDirAndPosOfNextClockwiseBlockOrHex(direction, position, ring):
    if direction == Direction.C:
        return (direction, position)
    if position == ring - 1:
        newDir = getNextDir(direction)
        return (newDir, 1)
    return (direction, position + 1)

def getStartColorForDirection(direction):
    if direction == Direction.C:
        return (1,1,1)  # White
    elif direction == Direction.SW:
        return (1, 0, 0)  # Red
    elif direction == Direction.W:
        return (1, 1, 0)  # Yellow
    elif direction == Direction.NW:
        return (0, 1, 0)  # Green
    elif direction == Direction.NE:
        return (0, 1, 1) # Cyan
    elif direction == Direction.E:
        return (0, 0, 1)  # Blue
    else:  # direction == Direction.SE
        return (1, 0, 1)  # Magenta
    
def getColorForBlockOrHex(layer, ring, direction, position):
    # There is a better colour scheme than the one I chose.
    # Luckily it is easy to change to it. 
    # Each hex/block uses the colour that the hex after it would have been assigned.
    (direction, position) = getDirAndPosOfNextClockwiseBlockOrHex( direction, position, ring)
    startColor = getStartColorForDirection(direction)
    if ring == 1 or ring == 2:
        (r, g, b) = startColor
    else:
        nextDir = getNextDir(direction)
        endColor = getStartColorForDirection(nextDir)
        (r1, g1, b1) = startColor
        (r2, g2, b2) = endColor
        ratio1 = (ring - position)/(ring-1)
        ratio2 = (position - 1)/(ring-1)
        r = ratio1 * r1 + ratio2 * r2
        g = ratio1 * g1 + ratio2 * g2
        b = ratio1 * b1 + ratio2 * b2
    return (r,g,b)

    
# ----------------------------------
# Code specific to blocks and cubes:
# -----------------------------------
 
def getBlockPositionInLastLayer(ring, direction, position):
    if direction == Direction.C:
        return (0,0,0)
    elif direction == Direction.SW:
        return (ring-1, ring-position-1,0)
    elif direction == Direction.W:
        return (ring-1, 0,position)
    elif direction == Direction.NW:
        return (ring-position-1, 0, ring-1)
    elif direction == Direction.NE:
        return (0, position,ring-1)
    elif direction == Direction.E:
        return (0, ring-1, ring-position-1)
    else:  # direction == Direction.SE
        return (position, ring-1, 0)

def createBlock(layer, ring, direction, position, numberOfLayers):
    (x,y,z) = getBlockPositionInLastLayer(ring, direction, position)
    if layer < numberOfLayers:
        offset = numberOfLayers-layer
        (x,y,z) = (x+offset,y+offset,z+offset)
    blockName = "Block_L" + str(layer) + "R" + str(ring) + DirToString(direction) + "_" + str(position)
    blenderLayer = layer - ring + 1  # For bottom-up layering use: blenderLayer = layer
    layerSelection = selectLayer(blenderLayer)
    bpy.context.scene.layers[blenderLayer] = True  # Otherwise bpy.context.object is not the newly added cube!
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z), layers=layerSelection)
    bpy.context.object.name = blockName
    bpy.context.object.dimensions = (0.995,0.995,0.995)
    # Note: Made it slightly smaller to create shadows between adjacent blocks of the same colour
    # 
    # Create a material for the new block:
    diffuseColor = getColorForBlockOrHex(layer, ring, direction, position)
    matName = "Mat_" + blockName
    mat = makeMaterial(name = matName, diffuse = diffuseColor, specular=(1,1,1), alpha=1)
    setMaterial(bpy.context.object, mat)

def createLineInRingOfBlocks(layer, ring, direction, numberOfLayers):
    for pos in range(1,ring):
        createBlock(layer, ring, direction, pos, numberOfLayers)

def createRingOfBlocks(layer, ring, numberOfLayers):
    if ring == 1:
        createBlock(layer, 1, Direction.C, 1, numberOfLayers)
    else:
        for dir in range(1,7):
            createLineInRingOfBlocks(layer, ring, dir, numberOfLayers)
        
def createLayerOfBlocks(layer, numberOfLayers):
    for ring in range(1,layer+1):
        createRingOfBlocks(layer, ring, numberOfLayers)

def createCube(numberOfLayers):
    for layer in range(1, numberOfLayers+1):
        createLayerOfBlocks(layer, numberOfLayers)


# ----------------------------------
# Code specific to hexagons:
# -----------------------------------
def getHexPositionOnFlatSurface(ring, direction, position, radius):
    sqrt3 = math.sqrt(3)
    if direction == Direction.C:
        return ( 0, 0)
    elif direction == Direction.SW:
        return ( -1.5 * position * radius, -sqrt3 * (ring-1) * radius + sqrt3 / 2 * position * radius)
    elif direction == Direction.W:
        return ( -1.5 * (ring - 1) * radius, -sqrt3 / 2 * (ring - 1 - 2 * position ))
    elif direction == Direction.NW:
        return ( -1.5 * (ring - 1 - position) * radius, sqrt3 / 2 * (ring - 1 + position ) * radius )
    elif direction == Direction.NE:
        return ( 1.5 * position * radius, sqrt3 * ( ring - 1 - position / 2 ) )
    elif direction == Direction.E:
        return ( 1.5 * (ring-1) * radius, sqrt3 / 2 * radius * ( ring - 1 - 2 * position))
    else:  # direction == Direction.SE
        return ( 1.5 * radius * ( ring - 1 - position), - sqrt3 / 2 * radius  * ( ring - 1 + position ))
    
def getHexPosition(layer, ring, direction, position, numberOfLayers, radius, thickness):
    (x,y) = getHexPositionOnFlatSurface(ring, direction, position, radius)
    z = thickness * (numberOfLayers - layer)
    return (x,y,z)

def createHexTile(layer, ring, direction, position, numberOfLayers, radius, thickness):
    (x,y,z) = getHexPosition(layer, ring, direction, position, numberOfLayers, radius, thickness)
    hexName = "Hex_L" + str(layer) + "R" + str(ring) + DirToString(direction) + "_" + str(position)
    blenderLayer = 10 + layer - ring + 1  # For bottom-up layering, use blenderLayer = 10 + layer
    # Note: hexagons are in a separate set of layers from blocks
    layerSelection = selectLayer(blenderLayer)
    bpy.context.scene.layers[blenderLayer] = True  # Otherwise bpy.context.object is not the newly added cube!
    # Make it slightly smaller to create shadows between adjacent hexes of the same colour:
    adjustedThickness = thickness * 0.995
    adjustedRadius = radius * 0.995
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=adjustedRadius, depth=adjustedThickness, end_fill_type='NGON', location=(x,y,z), rotation=(0,0,radians(30)), layers=layerSelection)
    bpy.context.object.name = hexName
    # Create a material for the new hex tile:
    diffuseColor = getColorForBlockOrHex(layer, ring, direction, position)
    matName = "Mat_" + hexName
    mat = makeMaterial(name = matName, diffuse = diffuseColor, specular=(1,1,1), alpha=1)
    setMaterial(bpy.context.object, mat)

def createLineInRingOfHexTiles(layer, ring, direction, numberOfLayers, radius, thickness):
    if ring == 1:
        createHexTile(layer, 1, Direction.C, 1, numberOfLayers, radius, thickness)
    else:
        for pos in range(1,ring):
            createHexTile(layer, ring, direction, pos, numberOfLayers, radius, thickness)

def createRingOfHexTiles(layer, ring, numberOfLayers, radius, thickness):
    if ring == 1:
        createLineInRingOfHexTiles(layer, ring, Direction.C, numberOfLayers, radius, thickness)
    else:
        for dir in range(1,7):
            createLineInRingOfHexTiles(layer, ring, dir, numberOfLayers, radius, thickness)
    
def createLayerOfHexTiles(layer, numberOfLayers, radius, thickness):
    for ring in range(1,layer+1):
        createRingOfHexTiles(layer, ring, numberOfLayers, radius, thickness)

def createHexPyramid(numberOfLayers, radius = 1, thickness = 1):
    for layer in range(1, numberOfLayers+1):
        createLayerOfHexTiles(layer, numberOfLayers, radius, thickness)


# --------------------------------
# Generate cubes and hex pyramids:
# --------------------------------

# Use any number of layers up to 7.
# More than that and hexes/blocks will be placed in camera layers, 
# making deleting more difficult...
createCube(4)
createHexPyramid(4)


# -------------------------------------------------------------
# Sample code to generate cubes and hex pyramids incrementally:
# -------------------------------------------------------------
 
# You can build up the cube incrementally e.g.
# createLineInRingOfBlocks(4, 4, Direction.SW, 4)
# createLineInRingOfHexTiles(4, 4, Direction.SW, 4, radius=1, thickness=1)
# 
# createRingOfBlocks(4, 4, 4)
# createRingOfHexTiles(4, 4, 4, radius=1, thickness=1)
