'''
Written by Philip Rouse 2014

Module of procedures to create snowflake and shard particle geometry

This module contains the following classes and procedures
combineParts     : Combines a list of objects into one object
flakeIterate     : Creates a branching iteration of the input branch
makeFlake        : Creates a single snowflake
crystalise       : Adds hexagonal crystals to the input branch
createColourList : Creates a list containing possible shading groups for particles
makeShards       : Creates a number of ice shard particles
makeSnowflakes   : Creates a number of snowflakes

This module can be called upon to generate the geometry for the particles
'''
import maya.cmds as cmds
import random

def combineParts(partList,name):
    '''
    Combines a list of mesh objects into one object
    
    partList : List containing the names of the objects to be combined
    name     : The final object name
    
    All the element of the part list are selected and combined into 
    one object that's name is returned.
    '''
    cmds.select(partList[0:-1],partList[-1],r=1)
    obj=cmds.polyUnite(n=name, ch=0)[0]
    return obj

def flakeIterate(base, iterations, angle, scale):
    '''
    Creates a branching iteration of the input branch
    
    base       : The object to be duplicated
    iterations : Number of iterations remaining
    angle      : The angle to rotate the branches
    scale      : The amount to scale the duplicated branches
    
    A list is made containing the bas object, if there a no more iterations 
    to perform, the list is returned. Otherwise, the length of the base is 
    found and stored as offset and a random length is generated. The first 
    duplicate is made, and positioned at an angle at the end of the base, 
    it is crystallised, then duplicated and mirrored. The base for the next 
    iteration is created and the procedure is called again with one less 
    iteration. A list containing all the objects is returned.
    '''
    list = [base]
    if iterations==0:
        return list
    bBox = cmds.exactWorldBoundingBox(base)
    offset = bBox[3]-bBox[0]
    length=random.uniform(0.2,3)
    
    twig=cmds.duplicate(base)[0]
    cmds.scale(length,scale,scale, twig,r=1,p=[bBox[0],0,0])
    cmds.rotate(0,angle,0, twig,r=1,p=[bBox[0],0,0])
    cmds.move(offset,0,0,twig,r=1)
    list[len(list):]=[crystalise(twig)]
    list[len(list):]=[cmds.duplicate(list[-1])[0]]
    cmds.scale(-1,1,1,list[-1])
    
    nextBase=cmds.duplicate(base)[0]
    cmds.xform(nextBase,sp=[bBox[0],0,0],s=[1,scale,scale],t=[offset,0,0],r=1)
    list+=flakeIterate(nextBase,iterations-1,angle,scale)
    return list

def makeFlake(branches,radius):
    '''
    Creates a single snowflake
    
    branches : number of side branches
    radius   : radius of the snowflake
    
    A cube is created and transformed to taper with a diamond cross-section. 
    It is passed to flakeIterate to generate 1/6 of the snowflake. This branch 
    is duplicated and rotated around the centre to create the full snowflake. 
    The parts are combined, the flake is scaled and transformations are frozen. 
    The snowflake name is returned.
    '''
    name=cmds.polyCube()[0]
    cmds.rotate(45,0,0,name,r=1)
    cmds.move(0.5,0,0,name+'.vtx[0:7]',r=1)
    cmds.scale(0.7,0.2,0.1,p=[0,0,0],r=1)
    cmds.scale(1,0.7,0.7,name+'.f[4]',r=1,p=[0,0,0])
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
    partList=flakeIterate(name,7,random.uniform(30,70),0.7)
    branches=[combineParts(partList,'branch')]
    for i in range(1,6):
        branches[len(branches):]=[cmds.duplicate('branch')[0]]
        cmds.rotate(0,i*60,0,branches[-1],r=1)
    flake = combineParts(branches,'snowflake')
    scale = radius/6
    cmds.scale(scale,scale,scale,flake)
    cmds.makeIdentity(flake,apply=True, s=1, n=0)
    return flake

def crystalise(base):
    '''
    Adds hexagonal crystals to a branch
    
    base : The branch to be crystallised
    
    A crystal is created by scaling the top and bottom rings of vertices of a 
    cylinder. The crystal is aligned to the base branch and scaled to match. 
    The crystal is duplicated, randomly distributed along the branch and scaled 
    relative to their positioning. The crystals are combined with the base branch 
    mesh and this object is returned.
    '''
    crystal=[cmds.polyCylinder(r=1,sx=6,sy=2)[0]]
    cmds.polySoftEdge(crystal[0], a=0)
    cmds.scale(0.6,0.3,0.6,crystal[0]+'.f[12:13]',r=1)
    [(tx,ty,tz)] = cmds.getAttr(base+'.translate')
    [(rx,ry,rz)] = cmds.getAttr(base+'.rotate')
    cmds.move(tx,ty,tz,crystal[0])
    cmds.rotate(rx,ry,rz,crystal[0])
    [x1,y1,z1,x2,y2,z2] = cmds.xform(base+'.vtx[0:1]',q=1,t=1,ws=1)
    baseScale = cmds.getAttr(base+'.scaleX')
    cmds.scale(0.5,0.2,0.5,crystal[0])
    length = ((x2-x1)**2+(z2-z1)**2)**0.5
    for i in range(0,6):
        crystal[len(crystal):]=[cmds.duplicate(crystal[0])[0]]
    for x in crystal:
        dist = (random.random())
        cmds.move(length*dist,0,0,x,os=1,r=1,wd=1)
        size = (1.5-dist)*(length/3)
        cmds.scale(size,size,size,x,r=1)
        cmds.rotate(0,30,0,x,r=1)
    crystal += [base]
    return combineParts(crystal,base)

def createColourList(rgb1,rgb2,transparency,glow,number):
    '''
    Creates a list containing possible shading groups for particles
    
    rgb1         : One end of the colour range in the form (r,g,b)
    rgb2         : The other end of the colour range in the form (r,g,b)
    transparency : Alpha value for the shader
    glow         : Glow value for the shader
    number       : Number of colours to generate
    
    Random values for the r,g and b channels within the range of the two inputs 
    and generated and along with the transparency and glow values, are added to 
    a new phong shader. The shader is assigned a shading group and the group is 
    added the list. The list of shading groups is returned.
    '''
    shadingGroupList = []
    for i in range(0,number):
        r=random.uniform(rgb1[0],rgb2[0])
        g=random.uniform(rgb1[1],rgb2[1])
        b=random.uniform(rgb1[2],rgb2[2])
        particleMat = cmds.shadingNode('phong',n='particlePhong',asShader=1)
        cmds.setAttr(particleMat+'.color',r,g,b, typ='double3')
        cmds.setAttr(particleMat+'.transparency',transparency,transparency,transparency, typ='double3')
        cmds.setAttr(particleMat+'.glowIntensity',glow)
        shadingGroupList[len(shadingGroupList):] = [cmds.sets(renderable=1, noSurfaceShader=1, empty=1, name='particleSG')]
        cmds.connectAttr((particleMat+'.outColor'),(shadingGroupList[-1]+'.surfaceShader'),f=1)
    return shadingGroupList
    
def makeShards(number,size,sizeVar,rgb1,rgb2,transparency,glow):
    '''
    Creates a number of ice shard particles
    
    number       : Number of particles to create
    size         : Radius of the particles
    sizeVar      : Variation in the radius
    rgb1         : One end of the colour range in the form (r,g,b)
    rgb2         : The other end of the colour range in the form (r,g,b)
    transparency : Alpha value for the shader
    glow         : Glow value for the shader
    
    The progress window is updated and the shading group list is created. 
    A while loop is initiated to create octahedrons, add them to the list 
    and assign shaders. The list of objects is returned.
    '''
    cmds.progressWindow(e=1,progress=0,status='Making Shards...')
    SGList = createColourList(rgb1,rgb2,transparency,glow,5)
    list=[]
    count=0
    while count<number:
        radius = size+random.uniform(-(size*sizeVar*0.01),(size*sizeVar*0.01))
        list[len(list):] = [cmds.polyPlatonicSolid(r=radius,st=2)[0]]
        cmds.polySoftEdge(list[-1],a=0)
        cmds.sets(list[-1], e=1, forceElement=SGList[random.randint(0,4)])
        cmds.progressWindow(e=1,step=100/number)
        count += 1
    return list
    
def makeSnowflakes(number,size,sizeVar,rgb1,rgb2,transparency,glow):
    '''
    Creates a number of snowflakes
    
    number       : Number of particles to create
    size         : Radius of the snowflakes
    sizeVar      : Variation in the radius
    rgb1         : One end of the colour range in the form (r,g,b)
    rgb2         : The other end of the colour range in the form (r,g,b)
    transparency : Alpha value for the shader
    glow         : Glow value for the shader
    
    The progress window is updated and the shading group list is created. 
    A while loop is initiated to create snowflakes, add them to the list 
    and assign shaders. The list of objects is returned.
    '''
    cmds.progressWindow(e=1,progress=0,status='Making Snowflakes...')
    SGList = createColourList(rgb1,rgb2,transparency,glow,5)
    list=[]
    count=0
    while count<number:
        radius = size+random.uniform(-(size*sizeVar*0.01),(size*sizeVar*0.01))
        list[len(list):] = [makeFlake(random.randint(5,8),radius)]
        cmds.sets(list[-1], e=1, forceElement=SGList[random.randint(0,4)])
        cmds.progressWindow(e=1,step=100/number)
        count += 1
    return list
