'''
Written by Philip Rouse 2014

Module of procedures to create various spiral curves

This module contains the following classes and procedures
hyperbolic       : creates a hyperbolic spiral
logarithmic      : creates a logarithmic spiral
archimedes       : creates a Archimedes spiral
archimedesDouble : creates a Archimedes spiral that spirals out then in again

This module creates a variety of simple spirals allowing the user to easily 
make some visually pleasing effects. However any curve can be used as a base 
for particle effects allowing for much more complex and versatile uses for 
this project.
'''
import maya.cmds as cmds
import random
import math

def hyperbolic(loops,spiralIn,height):
    '''
    Creates a hyperbolic spiral
    
    loops    : Number of complete turns the spiral should have
    spiralIn : Direction of the generated curve
    height   : Vertical height of the spiral
    
    The curve is created and the required number of control vertices is calculated 
    along with the fraction of the height each CV needs to be placed. The polar 
    equation of a hyperbolic spiral is r=a/theta where a scales the spiral. The 
    polar coordinates are converted to Cartesian form by x=r*math.cos(theta) and 
    y=r*math.sin(theta). The direction of the curve can be reversed based on the 
    spiralInwards flag.
    '''
    curve=cmds.curve(p=[(0,0,0)],n='curve_01')
    cvNo=loops*8
    heightFrac = float(height)/cvNo
    for i in range(1,cvNo+2):
        theta=i*(0.25*math.pi)
        r=theta**(-1)
        x=r*math.cos(theta)
        y=r*math.sin(theta)
        cmds.curve(curve,a=True,p=[(x,i*heightFrac,y)])
    cmds.delete(curve+'.cv[0]')
    if spiralIn==False:
        cmds.reverseCurve(curve,ch=0,rpo=1)

def logarithmic(loops,spiralIn,growth,height):
    '''
    Creates a logarithmic spiral
    
    loops    : Number of complete turns the spiral should have
    spiralIn : Direction of the generated curve
    growth   : Growth factor
    height   : Vertical height of the spiral
    
    The curve is created and the required number of control vertices is calculated 
    along with the fraction of the height each CV needs to be placed. The polar 
    equation of a logarithmic spiral is r=a*e^(b*theta) where a scales the spiral 
    and b controls how tightly it winds. The polar coordinates are converted to 
    Cartesian form by x=r*math.cos(theta) and y=r*math.sin(theta). The direction 
    of the curve can be reversed based on the spiralInwards flag.
    '''
    curve=cmds.curve(p=[(0,0,0)],n='curve_01')
    cvNo=loops*8
    heightFrac = float(height)/cvNo
    for i in range(1,cvNo+1):
        theta=i*(0.25*math.pi)
        r=0.1*(1/(1.8*math.pi))*math.e**(growth*theta)
        x=r*math.cos(theta)
        y=r*math.sin(theta)
        cmds.curve(curve,a=True,p=[(x,i*heightFrac,y)])
    if spiralIn==True:
        cmds.reverseCurve(curve,ch=0,rpo=1)
        
def archimedes(loops,spiralIn,gaps,height):
    '''
    Creates a Archimedes spiral
    
    loops    : Number of complete turns the spiral should have
    spiralIn : Direction of the generated curve
    gaps     : Distance between successive turnings
    height   : Vertical height of the spiral
    
    The curve is created and the required number of control vertices is calculated 
    along with the fraction of the height each CV needs to be placed. The polar 
    equation of a Archimedes spiral is r=a+b*theta where a rotates the spiral 
    and b controls distance between successive turnings. The polar coordinates 
    are converted to Cartesian form by x=r*math.cos(theta) and y=r*math.sin(theta).
    The direction of the curve can be reversed based on the spiralInwards flag.
    '''
    curve=cmds.curve(p=[(0,0,0)],n='curve_01')
    cvNo=loops*8
    heightFrac = float(height)/cvNo
    for i in range(1,cvNo+1):
        theta=i*(0.25*math.pi)
        r=(gaps/(1.8*math.pi))*theta
        x=r*math.cos(theta)
        y=r*math.sin(theta)
        cmds.curve(curve,a=True,p=[(x,i*heightFrac,y)])
    if spiralIn==True:
        cmds.reverseCurve(curve,ch=0,rpo=1)

def archimedesDouble(loops,spiralDown,gaps,height):
    '''
    Creates a Archimedes spiral that spirals out then in again
    
    loops      : Number of complete turns the spiral should have
    spiralDown : Direction of the generated curve
    growth     : Growth factor
    height     : Vertical height of the spiral
    
    The curve is created and the required number of control vertices is calculated 
    along with the fraction of the height each CV needs to be placed. The polar 
    equation of a Archimedes spiral is r=a+b*theta where a rotates the spiral 
    and b controls distance between successive turnings. The polar coordinates 
    are converted to Cartesian form by x=r*math.cos(theta) and y=r*math.sin(theta).
    After half the CVs, I reverse the equation to wind the spiral back in. The 
    direction of the curve can be reversed based on the spiralDown flag.
    '''
    curve=cmds.curve(p=[(0,0,0)],n='curve_01')
    cvNo=int(loops*8)
    heightFrac = float(height)/cvNo
    for i in range(1,(cvNo/2)+1):
        theta=i*(0.25*math.pi)
        r=(gaps/(1.8*math.pi))*theta
        x=r*math.cos(theta)
        y=r*math.sin(theta)
        cmds.curve(curve,a=True,p=[(x,i*heightFrac,y)])
    for i in reversed(range(0,cvNo/2)):
        theta=i*(0.25*math.pi)
        r=(gaps/(1.8*math.pi))*theta
        x=(r*math.cos(theta))
        y=-(r*math.sin(theta))
        cmds.curve(curve,a=True,p=[(x,height-i*heightFrac,y)])
    if spiralDown==True:
        cmds.reverseCurve(curve,ch=0,rpo=1)
