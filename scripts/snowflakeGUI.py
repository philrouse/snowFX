'''
Written by Philip Rouse 2014

Module of procedures to create the SnowFX UI and execute the FX generation code from the other modules using the user defined variables

This module contains the following classes and procedures
snowflakeUI : Contains procedures to create and control the GUI, and to contain the input variables
    __init__          : Creates the GUI window
    hypCurveUI        : Creates the UI containing options to create a hyperbolic spiral
    logCurveUI        : Creates the UI containing options to create a logarithmic spiral
    arcCurveUI        : Creates the UI containing options to create an Archimedes spiral
    arcDoubCurveUI    : Creates the UI containing options to create an Archimedes spiral that spirals out then in again
    curveEmitUI       : Creates the UI containing options to emit particles from a curve
    curveFollowUI     : Creates the UI containing options to make a particle trail following a curve
    planeEmitUI       : Creates the UI containing options to emit particles from a plane
    flakeGenUI        : Creates the UI containing options to generate snowflakes
    spiralToggle      : Toggle direction of the spiral
    updateSourceCurve : Adds the name of the selected curve to the text field
    updateSourcePlane : Adds the name of the selected plane to the text field
    updateColour1     : Allows the user to select a colour for the 1st canvas
    updateColour2     : Allows the user to select a colour for the 2nd canvas
    runHypCurve       : Executes the code to make a hyperbolic spiral
    runLogCurve       : Executes the code to make a logarithmic spiral
    runArcCurve       : Executes the code to make an Archimedes spiral
    runArcDoubCurve   : Executes the code to make an Archimedes spiral that spirals out then in again
    runEmitCurve      : Executes the code to emit particles from a curve
    runCurveFollow    : Executes the code to animate particles following a curve
    runPlaneEmit      : Executes the code to emit particles from a plane
    runFlakeGen       : Executes the code to generate snowflakes
    makeAllParticles  : Executes the code to generate all the required particles
errorPopup  : Contains procedures to create and control an error popup
    __init__    : Create a popup window with an error message
    closeWindow : Closes popup window

The general structure of this module is that it first creates a window allowing 
the user to chose what they want to create. It then creates the required input fields 
based on what was selected. When the generate button is pressed it processes all the 
inputs and calls the relevant procedure from another module.
'''
import maya.cmds as cmds
import math, random, curves, makeSnowflakes, particleFX, sys
reload(curves)
reload(makeSnowflakes)
reload(particleFX)

class snowflakeUI():

    '''Contains procedures to create and control the GUI, and contains the input variables'''

    def __init__(self):
        '''
        Creates the GUI window with the image banner and options for what to generate
        
        self.curveOptionsFrame  : The UI layout that the curve options will be placed into when created
        self.snowFXOptionsFrame : The UI layout that the particle options will be placed into when created
        '''
        if cmds.window('snowflakeUI', exists = True):
            cmds.deleteUI('snowflakeUI')
            
        self.window = cmds.window('snowflakeUI',t='Snowflake FX Generator',w=545,h=500,mxb=0,mnb=0,s=0)
        
        self.mainLayout = cmds.formLayout()
        
        imgPane = cmds.paneLayout(h=130, bgc=(0, 0, 0))
        bannerLayout = cmds.formLayout()
        banner = cmds.image(image=cmds.internalVar(upd=1)+'/icons/snowflakeBanner.png')
        cmds.formLayout(bannerLayout, e=1,
                                  attachForm=[(banner,'top',0),
                                  (banner,'bottom',0),
                                  (banner,'left',0),
                                  (banner,'right',0)])
                                  
        cmds.setParent(self.mainLayout)
        tabs = cmds.tabLayout(innerMarginWidth=5,innerMarginHeight=5,scr=1)
        
        cmds.formLayout(self.mainLayout, e=1, 
                                  attachForm=[(imgPane,'top',5),
                                                      (imgPane,'left',5),
                                                      (imgPane,'right',5),
                                                      (tabs, 'left', 5), 
                                                      (tabs, 'right', 5), 
                                                      (tabs, 'bottom', 5)], 
                                  attachControl=[(tabs, 'top', 0, imgPane)])
                                  
        self.curvesTab = cmds.rowColumnLayout(numberOfColumns=1,cs=[(1,5),(1,5)],cw=(1,500))
        cmds.rowLayout(numberOfColumns=5,cw=(1,110))
        cmds.text(label='Spiral Type:')
        curvesRadioMenu = cmds.radioCollection()
        cmds.radioButton( label='Hyperbolic', cc=self.hypCurveUI)
        cmds.radioButton( label='Logarithmic', cc=self.logCurveUI )
        cmds.radioButton( label='Archimedes', cc=self.arcCurveUI )
        cmds.radioButton( label='Archimedes Double', cc=self.arcDoubCurveUI )
        cmds.setParent('..')
        
        
        self.curveOptionsFrame = cmds.rowColumnLayout(numberOfColumns=1)
        cmds.setParent('..')
        cmds.setParent('..')
         
        self.snowFXTab = cmds.rowColumnLayout(numberOfColumns=1,cs=(1,5),cw=(1,500))
        cmds.rowLayout(numberOfColumns=5,cw=(1,110))
        cmds.text(label='Generate:')
        snowFXRadioMenu = cmds.radioCollection()
        cmds.radioButton( label='Emit from Curve', cc=self.curveEmitUI)
        cmds.radioButton( label='Follow Curve', cc=self.curveFollowUI )
        cmds.radioButton( label='Emit from Plane', cc=self.planeEmitUI )
        cmds.radioButton( label='Just Snowflakes', cc=self.flakeGenUI )
        cmds.setParent('..')
        
        
        self.snowFXOptionsFrame = cmds.rowColumnLayout(numberOfColumns=1)
        cmds.setParent('..')
         
        cmds.tabLayout(tabs, edit=True, 
                      tabLabel=((self.curvesTab,'Curves'), (self.snowFXTab,'Snow FX')), 
                      scr=True, cr=True )
                      
        cmds.showWindow(self.window)
    def hypCurveUI(self,state):  
        '''
        Creates the UI containing options to create a hyperbolic spiral
        
        Initialises the following variables
        self.loops    : Number of complete rotations the spiral should have
        self.height   : The vertical height of the spiral
        self.spiralIn : The direction of the generated curve
        
        '''
        if state == 1:
            self.tempFrame0 = cmds.rowColumnLayout(numberOfColumns=1,parent=self.curveOptionsFrame)
            cmds.frameLayout(label='Spiral',cll=1)
            cmds.rowColumnLayout(numberOfColumns=2,cs=[(1,5),(2,5)],cw=[(1,350),(2,118)],cal=[(1,'right'),(2,'left')])
            
            cmds.text(label='Number of Loops')
            self.loops = cmds.floatField(minValue=0,width=60,pre=1,v=2)
            cmds.text(label='Height')
            self.height = cmds.floatField(width=60,pre=3)
            cmds.text(label='Curve Direction')
            self.spiralIn = 1
            cmds.checkBox(label='Inwards',v=1,cc=self.spiralToggle)
            cmds.setParent('..')
            cmds.setParent('..')
            cmds.button(label='Generate',width=100,c=self.runHypCurve)
            cmds.setParent('..')
        else:
            cmds.deleteUI(self.tempFrame0)
        
    def logCurveUI(self,state):
        '''
        Creates the UI containing options to create a logarithmic spiral
        
        Initialises the following variables
        self.loops    : Number of complete rotations the spiral should have
        self.growth   : Growth factor 
        self.height   : The vertical height of the spiral
        self.spiralIn : The direction of the generated curve
        '''
        if state == 1:
            self.tempFrame1 = cmds.rowColumnLayout(numberOfColumns=1,parent=self.curveOptionsFrame)
            cmds.frameLayout(label='Spiral',cll=1)
            cmds.rowColumnLayout(numberOfColumns=2,cs=[(1,5),(2,5)],cw=[(1,350),(2,118)],cal=[(1,'right'),(2,'left')])
            
            cmds.text(label='Number of Loops')
            self.loops = cmds.floatField(minValue=0,width=60,pre=1,v=2)
            cmds.text(label='Growth Factor')
            self.growth = cmds.floatField(minValue=0,width=60,pre=3,v=0.4)
            cmds.text(label='Height')
            self.height = cmds.floatField(width=60,pre=3)
            cmds.text(label='Curve Direction')
            self.spiralIn = 1
            cmds.checkBox(label='Inwards',v=1,cc=self.spiralToggle)
            cmds.setParent('..')
            cmds.setParent('..')
            cmds.button(label='Generate',width=100,c=self.runLogCurve)
            cmds.setParent('..')
        else:
            cmds.deleteUI(self.tempFrame1)
        
    def arcCurveUI(self,state):
        '''
        Creates the UI containing options to create an Archimedes spiral
        
        Initialises the following variables
        self.loops    : Number of complete rotations the spiral should have
        self.gap      : Size of the gaps between successive turnings
        self.height   : The vertical height of the spiral
        self.spiralIn : The direction of the generated curve
        '''
        if state == 1:
            self.tempFrame2 = cmds.rowColumnLayout(numberOfColumns=1,parent=self.curveOptionsFrame)
            cmds.frameLayout(label='Spiral',cll=1)
            cmds.rowColumnLayout(numberOfColumns=2,cs=[(1,5),(2,5)],cw=[(1,350),(2,118)],cal=[(1,'right'),(2,'left')])
            
            cmds.text(label='Number of Loops')
            self.loops = cmds.floatField(minValue=0,width=60,pre=1,v=3)
            cmds.text(label='Gap Between Rings')
            self.gap = cmds.floatField(minValue=0,width=60,pre=3,v=1)
            cmds.text(label='Height')
            self.height = cmds.floatField(width=60,pre=3,v=5)
            cmds.text(label='Curve Direction')
            self.spiralIn = 1
            cmds.checkBox(label='Inwards',v=1,cc=self.spiralToggle)
            cmds.setParent('..')
            cmds.setParent('..')
            cmds.button(label='Generate',width=100,c=self.runArcCurve)
            cmds.setParent('..')
        else:
            cmds.deleteUI(self.tempFrame2)
       
    def arcDoubCurveUI(self,state):
        '''
        Creates the UI containing options to create an Archimedes spiral that spirals out then in again
        
        Initialises the following variables
        self.loops    : Number of complete rotations the spiral should have
        self.gap      : Size of the gaps between successive turnings
        self.height   : The vertical height of the spiral
        self.spiralIn : The direction of the generated curve
        '''
        if state == 1:
            self.tempFrame3 = cmds.rowColumnLayout(numberOfColumns=1,parent=self.curveOptionsFrame)
            cmds.frameLayout(label='Spiral',cll=1)
            cmds.rowColumnLayout(numberOfColumns=2,cs=[(1,5),(2,5)],cw=[(1,350),(2,118)],cal=[(1,'right'),(2,'left')])
            
            cmds.text(label='Number of Loops')
            self.loops = cmds.floatField(minValue=0,width=60,pre=1,v=2)
            cmds.text(label='Gap Between Rings')
            self.gap = cmds.floatField(minValue=0,width=60,pre=3,v=1)
            cmds.text(label='Height')
            self.height = cmds.floatField(width=60,pre=3,v=8)
            cmds.text(label='Curve Direction')
            self.spiralIn = 0
            cmds.checkBox(label='Downwards',v=0,cc=self.spiralToggle)
            cmds.setParent('..')
            cmds.setParent('..')
            cmds.button(label='Generate',width=100,c=self.runArcDoubCurve)
            cmds.setParent('..')
        else:
            cmds.deleteUI(self.tempFrame3)
    
    def curveEmitUI(self, state):
        '''
        Creates the UI containing options to emit particles from a curve
        
        Initialises the following variables
        self.startFrame     : Frame to start emission
        self.endFrame       : Frame to finish emission
        self.maxDistance    : Maximum distance particles will be emitted from the middle of the curve
        self.minDistance    : Maximum distance particles will be emitted from the start and end of the curve
        self.emitTime       : Number of frames particles will be affected by the emission force
        self.lifeTime       : Average lifetime of a particle
        self.lifeTimeVar    : Variation from average lifetime as a percentage
        self.fadeOut        : Number of frames to scale down particles at the end of their lifetime
        self.driftX         : Distance a particle will drift in the X direction in 10 frames
        self.driftY         : Distance a particle will drift in the Y direction in 10 frames
        self.driftZ         : Distance a particle will drift in the Z direction in 10 frames
        self.turbulenceAmp  : Amplitude of the turbulence animation graph
        self.turbulencePer  : Period of the turbulence animation graph
        self.sourceCurve    : Name of the curve particles will emit from
        self.flakeNumber    : Number of snowflake particles to generate
        self.flakeRadius    : Average radius of snowflake particles
        self.flakeRadiusVar : Variation from average radius as a percentage
        self.shardNumber    : Number of shard particles to generate
        self.shardRadius    : Average radius of shard particles
        self.shardRadiusVar : Variation from average radius as a percentage
        self.colour1        : Canvas showing one end of the particle colour range
        self.colour2        : Canvas showing the other end of the particle colour range
        self.transparency   : Alpha value for the particle material
        self.glow           : Glow value for the particle material
        '''
        if state == 1:
            self.tmpFrame0 = cmds.rowColumnLayout(numberOfColumns=1,parent=self.snowFXOptionsFrame)
            cmds.frameLayout(label='Animation',cll=1)
            cmds.rowColumnLayout(numberOfColumns=2,cs=[(1,5),(2,5)],cw=[(1,350),(2,118)],cal=[(1,'right'),(2,'left')])
            
            cmds.text(label='Start Frame')
            self.startFrame = cmds.intField(minValue=0,width=60)
            cmds.text(label='End Frame')
            self.endFrame = cmds.intField(minValue=0,width=60,v=20)
            cmds.text(label='Middle Max Emission Distance')
            self.maxDistance = cmds.floatField(minValue=0,width=60,pre=3,v=1)
            cmds.text(label='Start/End Max Emission Distance')
            self.minDistance = cmds.floatField(minValue=0,width=60,pre=3)
            cmds.text(label='Emission Force Time')
            self.emitTime = cmds.intField(minValue=0,width=60,v=10)
            cmds.text(label='Particle Lifetime')
            self.lifeTime = cmds.intField(minValue=0,width=60,v=20)
            cmds.text(label='Particle Lifetime Variation (%)')
            self.lifeTimeVar = cmds.intField(minValue=0,maxValue=100,width=60,v=20)
            cmds.text(label='Particle Fadeout')
            self.fadeOut = cmds.intField(minValue=0,width=60,v=3)
            cmds.text(label = 'Drift:')
            cmds.rowLayout(numberOfColumns = 6)
            cmds.text(label = 'X')
            self.driftX = cmds.floatField(width=30,pre=2,v=0.05)
            cmds.text(label = 'Y')
            self.driftY = cmds.floatField(width=30,pre=2,v=0.1)
            cmds.text(label = 'Z')
            self.driftZ = cmds.floatField(width=30,pre=2,v=0.05)
            cmds.setParent('..')
            cmds.text(label='Turbulence Amplitude')
            self.turbulenceAmp = cmds.floatField(minValue=0,width=60,pre=3,v=1)
            cmds.text(label='Turbulence Period')
            self.turbulencePer = cmds.intField(minValue=0,width=60,v=12)
            cmds.text(label='Source Curve Name')
            self.sourceCurve = cmds.textField(width=60)
            cmds.text(label='')
            cmds.button(label='Set Selected', c=self.updateSourceCurve)
            cmds.setParent('..')
            cmds.setParent('..')
            
            
            cmds.frameLayout(label='Particles',cll=1)
            cmds.rowColumnLayout(numberOfColumns=2,cs=[(1,5),(2,5)],cw=[(1,350),(2,118)],cal=[(1,'right'),(2,'left')])
            
            cmds.text(label='Number of Snowflakes')
            self.flakeNumber = cmds.intField(minValue=0,width=60,v=10)
            cmds.text(label='Snowflake Radius')
            self.flakeRadius = cmds.floatField(minValue=0,width=60,pre=3,v=0.2)
            cmds.text(label='Snowflake Radius Variation (%)')
            self.flakeRadiusVar = cmds.intField(minValue=0,maxValue=100,width=60,v=20)
            cmds.text(label='Number of Shards')
            self.shardNumber = cmds.intField(minValue=0,width=60,v=50)
            cmds.text(label='Shard Size')
            self.shardSize = cmds.floatField(minValue=0,width=60,pre=3,v=0.07)
            cmds.text(label='Shard Size Variation (%)')
            self.shardSizeVar = cmds.intField(minValue=0,width=60,v=20)
            cmds.text(label='Colour Range 1')
            self.colour1 = cmds.canvas( rgb=(0.82,0.87,0.94),width = 60,height=20,pc=self.updateColour1)
            cmds.text(label='Colour Range 2')
            self.colour2 = cmds.canvas( rgb=(0.83,0.82,0.92),width = 60,height=20,pc=self.updateColour2)
            cmds.text(label='Transparency')
            self.transparency = cmds.floatField(minValue=0,maxValue=1,width=60,pre=3,v=0.6)
            cmds.text(label='Glow Intensity')
            self.glow = cmds.floatField(minValue=0,maxValue=1,width=60,pre=3,v=0.15)
            cmds.setParent('..')
            cmds.setParent('..')
            
            
            cmds.button(label='Generate',width=100,c=self.runEmitCurve)
            cmds.setParent('..')
        else:
            cmds.deleteUI(self.tmpFrame0)
        
    def curveFollowUI(self,state):
        '''
        Creates the UI containing options to make a particle trail following a curve
        
        Initialises the following variables
        self.startFrame     : Frame to start particle movement along curve
        self.endFrame       : Frame to finish particle movement along curve
        self.maxDistance    : Maximum distance particles will be from the curve
        self.minDistance    : Maximum distance particles will be from the curve at the nose or tail of the group
        self.length         : Total trail length in frames
        self.nose           : Number of frames to taper to the nose of the trail
        self.turbulenceAmp  : Amplitude of the turbulence animation graph
        self.turbulencePer  : Period of the turbulence animation graph
        self.sourceCurve    : Name of the curve particles will emit from
        self.flakeNumber    : Number of snowflake particles to generate
        self.flakeRadius    : Average radius of snowflake particles
        self.flakeRadiusVar : Variation from average radius as a percentage
        self.shardNumber    : Number of shard particles to generate
        self.shardRadius    : Average radius of shard particles
        self.shardRadiusVar : Variation from average radius as a percentage
        self.colour1        : Canvas showing one end of the particle colour range
        self.colour2        : Canvas showing the other end of the particle colour range
        self.transparency   : Alpha value for the particle material
        self.glow           : Glow value for the particle material
        '''
        if state == 1:
            self.tmpFrame1 = cmds.rowColumnLayout(numberOfColumns=1,parent=self.snowFXOptionsFrame)
            cmds.frameLayout(label='Animation',cll=1)
            cmds.rowColumnLayout(numberOfColumns=2,cs=[(1,5),(2,5)],cw=[(1,350),(2,118)],cal=[(1,'right'),(2,'left')])
            
            cmds.text(label='Start Frame')
            self.startFrame = cmds.intField(minValue=0,width=60)
            cmds.text(label='End Frame')
            self.endFrame = cmds.intField(minValue=0,width=60,v=20)
            cmds.text(label='Max Distance from Curve')
            self.maxDistance = cmds.floatField(minValue=0,width=60,pre=3,v=0.5)
            cmds.text(label='Nose/Tail Distance from Curve')
            self.minDistance = cmds.floatField(minValue=0,width=60,pre=3)
            cmds.text(label='Total Trail Length (frames)')
            self.length = cmds.intField(minValue=0,width=60,v=16)
            cmds.text(label='Nose Length (frames)')
            self.nose = cmds.intField(minValue=0,width=60,v=3)
            cmds.text(label='Tail Length (frames)')
            self.tail = cmds.intField(minValue=0,maxValue=100,width=60,v=10)
            cmds.text(label='Turbulence Amplitude')
            self.turbulenceAmp = cmds.floatField(minValue=0,width=60,pre=3,v=1)
            cmds.text(label='Turbulence Period')
            self.turbulencePer = cmds.intField(minValue=0,width=60,v=12)
            cmds.text(label='Source Curve Name')
            self.sourceCurve = cmds.textField(width=60)
            cmds.text(label='')
            cmds.button(label='Set Selected', c=self.updateSourceCurve)
            cmds.setParent('..')
            cmds.setParent('..')
            cmds.frameLayout(label='Particles',cll=1)
            cmds.rowColumnLayout(numberOfColumns=2,cs=[(1,5),(2,5)],cw=[(1,350),(2,118)],cal=[(1,'right'),(2,'left')])
            
            cmds.text(label='Number of Snowflakes')
            self.flakeNumber = cmds.intField(minValue=0,width=60,v=10)
            cmds.text(label='Snowflake Radius')
            self.flakeRadius = cmds.floatField(minValue=0,width=60,pre=3,v=0.2)
            cmds.text(label='Snowflake Radius Variation (%)')
            self.flakeRadiusVar = cmds.intField(minValue=0,maxValue=100,width=60,v=20)
            cmds.text(label='Number of Shards')
            self.shardNumber = cmds.intField(minValue=0,width=60,v=50)
            cmds.text(label='Shard Size')
            self.shardSize = cmds.floatField(minValue=0,width=60,pre=3,v=0.07)
            cmds.text(label='Shard Size Variation (%)')
            self.shardSizeVar = cmds.intField(minValue=0,width=60,v=20)
            cmds.text(label='Colour Range 1')
            self.colour1 = cmds.canvas( rgb=(0.82,0.87,0.94),width = 60,height=20,pc=self.updateColour1)
            cmds.text(label='Colour Range 2')
            self.colour2 = cmds.canvas( rgb=(0.83,0.82,0.92),width = 60,height=20,pc=self.updateColour2)
            cmds.text(label='Transparency')
            self.transparency = cmds.floatField(minValue=0,maxValue=1,width=60,pre=3,v=0.6)
            cmds.text(label='Glow Intensity')
            self.glow = cmds.floatField(minValue=0,maxValue=1,width=60,pre=3,v=0.15)
            cmds.setParent('..')
            cmds.setParent('..')
            
            cmds.button(label='Generate',width=100,c=self.runCurveFollow)
            cmds.setParent('..')
        else:
            cmds.deleteUI(self.tmpFrame1)
        
    def planeEmitUI(self,state):
        '''
        Creates the UI containing options to emit particles from a plane
        
        Initialises the following variables
        self.startFrame     : Frame to start emission
        self.endFrame       : Frame to finish emission
        self.maxDistance    : Maximum distance particles will be emitted from the plane
        self.minDistance    : Minimum distance particles will be emitted from the plane
        self.maxAngle       : Maximum angle from the plane normal the particles con be emitted at
        self.emitTime       : Number of frames particles will be affected by the emission force
        self.lifeTime       : Average lifetime of a particle
        self.lifeTimeVar    : Variation from average lifetime as a percentage
        self.fadeOut        : Number of frames to scale down particles at the end of their lifetime
        self.driftX         : Distance a particle will drift in the X direction in 10 frames
        self.driftY         : Distance a particle will drift in the Y direction in 10 frames
        self.driftZ         : Distance a particle will drift in the Z direction in 10 frames
        self.turbulenceAmp  : Amplitude of the turbulence animation graph
        self.turbulencePer  : Period of the turbulence animation graph
        self.sourcePlane    : Name of the plane particles will emit from
        self.flakeNumber    : Number of snowflake particles to generate
        self.flakeRadius    : Average radius of snowflake particles
        self.flakeRadiusVar : Variation from average radius as a percentage
        self.shardNumber    : Number of shard particles to generate
        self.shardRadius    : Average radius of shard particles
        self.shardRadiusVar : Variation from average radius as a percentage
        self.colour1        : Canvas showing one end of the particle colour range
        self.colour2        : Canvas showing the other end of the particle colour range
        self.transparency   : Alpha value for the particle material
        self.glow           : Glow value for the particle material
        '''
        if state == 1:
            self.tmpFrame2 = cmds.rowColumnLayout(numberOfColumns=1,parent=self.snowFXOptionsFrame)
            cmds.frameLayout(label='Animation',cll=1)
            cmds.rowColumnLayout(numberOfColumns=2,cs=[(1,5),(2,5)],cw=[(1,350),(2,118)],cal=[(1,'right'),(2,'left')])
            
            cmds.text(label='Start Emission')
            self.startFrame = cmds.intField(minValue=0,width=60)
            cmds.text(label='End Emission')
            self.endFrame = cmds.intField(minValue=0,width=60,v=3)
            cmds.text(label='Maximum Distance')
            self.maxDistance = cmds.floatField(minValue=0,width=60,pre=3,v=8)
            cmds.text(label='Minimum Distance')
            self.minDistance = cmds.floatField(width=60,pre=3,v=-1)
            cmds.text(label='Maximum Angle')
            self.maxAngle = cmds.floatField(minValue=0,width=60,pre=3,v=15)
            cmds.text(label='Force Duration')
            self.forceTime = cmds.intField(minValue=0,width=60,v=10)
            cmds.text(label='Particle Lifetime')
            self.lifeTime = cmds.intField(minValue=0,width=60,v=40)
            cmds.text(label='Particle Lifetime Variation (%)')
            self.lifeTimeVar = cmds.intField(minValue=0,maxValue=100,width=60,v=20)
            cmds.text(label='Particle Fadeout')
            self.fadeOut = cmds.intField(minValue=0,width=60,v=3)
            cmds.text(label = 'Drift:')
            cmds.rowLayout(numberOfColumns = 6)
            cmds.text(label = 'X')
            self.driftX = cmds.floatField(width=30,pre=2,v=0.05)
            cmds.text(label = 'Y')
            self.driftY = cmds.floatField(width=30,pre=2,v=0.1)
            cmds.text(label = 'Z')
            self.driftZ = cmds.floatField(width=30,pre=2,v=0.05)
            cmds.setParent('..')
            cmds.text(label='Turbulence Amplitude')
            self.turbulenceAmp = cmds.floatField(minValue=0,width=60,pre=3,v=1)
            cmds.text(label='Turbulence Period')
            self.turbulencePer = cmds.intField(minValue=0,width=60,v=12)
            cmds.text(label='Source Plane Name')
            self.sourcePlane = cmds.textField(width=60)
            cmds.text(label='')
            cmds.button(label='Set Selected', c=self.updateSourcePlane)
            cmds.setParent('..')
            cmds.setParent('..')
            
            
            cmds.frameLayout(label='Particles',cll=1)
            cmds.rowColumnLayout(numberOfColumns=2,cs=[(1,5),(2,5)],cw=[(1,350),(2,118)],cal=[(1,'right'),(2,'left')])
            
            cmds.text(label='Number of Snowflakes')
            self.flakeNumber = cmds.intField(minValue=0,width=60,v=10)
            cmds.text(label='Snowflake Radius')
            self.flakeRadius = cmds.floatField(minValue=0,width=60,pre=3,v=0.2)
            cmds.text(label='Snowflake Radius Variation (%)')
            self.flakeRadiusVar = cmds.intField(minValue=0,maxValue=100,width=60,v=20)
            cmds.text(label='Number of Shards')
            self.shardNumber = cmds.intField(minValue=0,width=60,v=50)
            cmds.text(label='Shard Size')
            self.shardSize = cmds.floatField(minValue=0,width=60,pre=3,v=0.07)
            cmds.text(label='Shard Size Variation (%)')
            self.shardSizeVar = cmds.intField(minValue=0,width=60,v=20)
            cmds.text(label='Colour Range 1')
            self.colour1 = cmds.canvas( rgb=(0.82,0.87,0.94),width = 60,height=20,pc=self.updateColour1)
            cmds.text(label='Colour Range 2')
            self.colour2 = cmds.canvas( rgb=(0.83,0.82,0.92),width = 60,height=20,pc=self.updateColour2)
            cmds.text(label='Transparency')
            self.transparency = cmds.floatField(minValue=0,maxValue=1,width=60,pre=3,v=0.6)
            cmds.text(label='Glow Intensity')
            self.glow = cmds.floatField(minValue=0,maxValue=1,width=60,pre=3,v=0.15)
            cmds.setParent('..')
            cmds.setParent('..')
            
            
            cmds.button(label='Generate',width=100,c=self.runPlaneEmit)
            cmds.setParent('..')
        else:
            cmds.deleteUI(self.tmpFrame2)
        return
        
    def flakeGenUI(self,state):
        '''
        Creates the UI containing options to generate snowflakes
        
        Initialises the following variables
        self.flakeNumber    : Number of snowflake particles to generate
        self.flakeRadius    : Average radius of snowflake particles
        self.flakeRadiusVar : Variation from average radius as a percentage
        self.colour1        : Canvas showing one end of the particle colour range
        self.colour2        : Canvas showing the other end of the particle colour range
        self.transparency   : Alpha value for the snowflake material
        self.glow           : Glow value for the snowflake material
        '''
        if state == 1:
            self.tmpFrame3 = cmds.rowColumnLayout(numberOfColumns=1,parent=self.snowFXOptionsFrame)
            cmds.frameLayout(label='Particles',cll=1)
            cmds.rowColumnLayout(numberOfColumns=2,cs=[(1,5),(2,5)],cw=[(1,350),(2,118)],cal=[(1,'right'),(2,'left')])
            
            cmds.text(label='Number of Snowflakes')
            self.flakeNumber = cmds.intField(minValue=0,width=60,v=10)
            cmds.text(label='Snowflake Radius')
            self.flakeRadius = cmds.floatField(minValue=0,width=60,pre=3,v=0.5)
            cmds.text(label='Snowflake Radius Variation (%)')
            self.flakeRadiusVar = cmds.intField(minValue=0,maxValue=100,width=60,v=20)
            cmds.text(label='Colour Range 1')
            self.colour1 = cmds.canvas( rgb=(0.82,0.87,0.94),width = 60,height=20,pc=self.updateColour1)
            cmds.text(label='Colour Range 2')
            self.colour2 = cmds.canvas( rgb=(0.83,0.82,0.92),width = 60,height=20,pc=self.updateColour2)
            cmds.text(label='Transparency')
            self.transparency = cmds.floatField(minValue=0,maxValue=1,width=60,pre=3,v=0.6)
            cmds.text(label='Glow Intensity')
            self.glow = cmds.floatField(minValue=0,maxValue=1,width=60,pre=3,v=0.15)
            cmds.setParent('..')
            cmds.setParent('..')
            
            cmds.button(label='Generate',width=100,c=self.runFlakeGen)
            cmds.setParent('..')
        else:
            cmds.deleteUI(self.tmpFrame3)
        return
    
    def spiralToggle(self,state):
        '''
        Toggle the curve direction 
        
        state : The state of the checkbox which called the procedure
        '''
        self.spiralIn = state
        return
        
    def updateSourceCurve(self,state):
        '''
        Adds the name of the selected curve to the text field.
        Will create an error popup if a single curve isn't selected
        '''
        if len(cmds.ls(sl=1))>1:
            errorPopup('Select only the target curve')
            return
        elif len(cmds.ls(sl=1))==0:
            errorPopup('Select a curve')
            return
        selected = cmds.ls(sl=1)[0]
        try:
            tmp = cmds.duplicateCurve(cmds.ls(sl=1)[0])[0]
            cmds.delete(tmp)
        except:
            errorPopup('Select a curve')
            return
        cmds.textField(self.sourceCurve,tx=selected,edit=1)
        return
        
    def updateSourcePlane(self,state):
        '''
        Adds the name of the selected curve to the text field.
        Will create an error popup if a single, unsubdivided plane isn't selected
        '''
        if len(cmds.ls(sl=1))>1:
            errorPopup('Select only the target plane')
            return
        elif len(cmds.ls(sl=1))==0:
            errorPopup('Select a plane')
            return
        selected = cmds.ls(sl=1)[0]
        print selected
        try:
            vtxCount = cmds.polyEvaluate(selected,v=1)
            if vtxCount!=4:
                errorPopup('Select an unsubdivided plane')
                return
        except:
            errorPopup('Select a plane')
            return
        cmds.textField(self.sourcePlane,tx=selected,edit=1)
        return
        
    def updateColour1(self):
        '''
        Opens a colour picker to allow the user to select a colour for the 1st canvas
        '''
        cmds.colorEditor(rgb=cmds.canvas(self.colour1,q=1,rgb=1))
        if cmds.colorEditor(q=1,r=1):
            rgb=cmds.colorEditor(q=1,rgb=1)
            cmds.canvas(self.colour1,e=1,rgb=rgb)
        else:
            return
        
    def updateColour2(self):
        '''
        Opens a colour picker to allow the user to select a colour for the 1nd canvas
        '''
        cmds.colorEditor(rgb=cmds.canvas(self.colour2,q=1,rgb=1))
        if cmds.colorEditor(q=1,r=1):
            rgb=cmds.colorEditor(q=1,rgb=1)
            cmds.canvas(self.colour2,e=1,rgb=rgb)
        else:
            return
     
    def runHypCurve(self,state):
        '''
        Executes the code to make a hyperbolic spiral using the variables defined in snowflakeUI.hypCurveUI
        '''
        curves.hyperbolic(cmds.floatField(self.loops,v=1,q=1),
                                 self.spiralIn,
                                 cmds.floatField(self.height,v=1,q=1))
     
    def runLogCurve(self,state):
        '''
        Executes the code to make a logarithmic spiral using the variables defined in snowflakeUI.logCurveUI
        '''
        curves.logarithmic(cmds.floatField(self.loops,v=1,q=1),
                                  self.spiralIn,
                                  cmds.floatField(self.growth,v=1,q=1),
                                  cmds.floatField(self.height,v=1,q=1))
     
    def runArcCurve(self,state):
        '''
        Executes the code to make an Archimedes spiral using the variables defined in snowflakeUI.arcCurveUI
        '''
        curves.archimedes(cmds.floatField(self.loops,v=1,q=1),
                                  self.spiralIn,
                                  cmds.floatField(self.gap,v=1,q=1),
                                  cmds.floatField(self.height,v=1,q=1))
     
    def runArcDoubCurve(self,state):
        '''
        Executes the code to make an Archimedes spiral that spirals out then in again using the variables defined in snowflakeUI.arcDoubCurveUI
        '''
        curves.archimedesDouble(cmds.floatField(self.loops,v=1,q=1),
                                           self.spiralIn,
                                           cmds.floatField(self.gap,v=1,q=1),
                                           cmds.floatField(self.height,v=1,q=1))
     
    def runEmitCurve(self,state):
        '''
        Executes the code to emit particles from a curve using the variables defined in snowflakeUI.curveEmitUI and starts the progress window
        Will create an error popup if the variable values would stop the code from functioning correctly
        '''
        if cmds.intField(self.endFrame,v=1,q=1)<=cmds.intField(self.startFrame,v=1,q=1):
            errorPopup('End Frame must be after Start Frame')
            return
        if cmds.intField(self.lifeTime,v=1,q=1)<=0:
            errorPopup('Particles have to have a lifetime')
            return
        if cmds.intField(self.fadeOut,v=1,q=1)>cmds.intField(self.lifeTime,v=1,q=1):
            errorPopup('Lifetime must be larger than fadeout time')
            return
        try:
            tmp = cmds.duplicateCurve(cmds.textField(self.sourceCurve,tx=1,q=1))[0]
            cmds.delete(tmp)
        except:
            errorPopup('Choose a source curve')
            return
        particleFX.reloadFile()
        cmds.progressWindow(title='SnowFX',
                                      progress=0,
                                      status='Starting up...')
        try:
            particles=self.makeAllParticles()
            particleFX.emitCurve(cmds.textField(self.sourceCurve,tx=1,q=1),
                                           cmds.intField(self.startFrame,v=1,q=1),
                                           cmds.intField(self.endFrame,v=1,q=1)-cmds.intField(self.startFrame,v=1,q=1),
                                           particles,
                                           cmds.floatField(self.maxDistance,v=1,q=1),
                                           cmds.floatField(self.minDistance,v=1,q=1),
                                           cmds.intField(self.emitTime,v=1,q=1),
                                           cmds.intField(self.lifeTime,v=1,q=1),
                                           cmds.intField(self.lifeTimeVar,v=1,q=1),
                                           cmds.intField(self.fadeOut,v=1,q=1),
                                           cmds.floatField(self.turbulenceAmp,v=1,q=1),
                                           cmds.intField(self.turbulencePer,v=1,q=1),
                                           (cmds.floatField(self.driftX,v=1,q=1),cmds.floatField(self.driftY,v=1,q=1),cmds.floatField(self.driftZ,v=1,q=1)))
            group = cmds.group(em=1,n='snowFX')
            for x in particles:
                cmds.parent(x.name,group)
            cmds.progressWindow(ep=1)
        except Exception, err:
            sys.stderr.write('ERROR: %s\n' % str(err))
            cmds.progressWindow(ep=1)
            errorPopup('Something went wrong :( \n Check the script editor for detials')
    
    def runCurveFollow(self,state):
        '''
        Executes the code to animate particles following a curve using the variables defined in snowflakeUI.curveFollowUI and starts the progress window
        Will create an error popup if the variable values would stop the code from functioning correctly
        '''
        if cmds.intField(self.endFrame,v=1,q=1)<=cmds.intField(self.startFrame,v=1,q=1):
            errorPopup('End Frame must be after Start Frame')
            return
        if cmds.intField(self.nose,v=1,q=1)+cmds.intField(self.tail,v=1,q=1)>cmds.intField(self.length,v=1,q=1):
            errorPopup('Nose and Tail must be less than Trail Length')
            return
        try:
            tmp = cmds.duplicateCurve(cmds.textField(self.sourceCurve,tx=1,q=1))[0]
            cmds.delete(tmp)
        except:
            errorPopup('Choose a source curve')
            return
        particleFX.reloadFile()
        cmds.progressWindow(title='SnowFX',
                                      progress=0,
                                      status='Starting up...')
        try:
            particles=self.makeAllParticles()
            particleFX.followCurve(cmds.textField(self.sourceCurve,tx=1,q=1),
                                           cmds.intField(self.startFrame,v=1,q=1),
                                           cmds.intField(self.endFrame,v=1,q=1)-cmds.intField(self.startFrame,v=1,q=1),
                                           particles,
                                           cmds.floatField(self.maxDistance,v=1,q=1),
                                           cmds.floatField(self.minDistance,v=1,q=1),
                                           cmds.intField(self.nose,v=1,q=1),
                                           cmds.intField(self.tail,v=1,q=1),
                                           cmds.intField(self.length,v=1,q=1),
                                           cmds.floatField(self.turbulenceAmp,v=1,q=1),
                                           cmds.intField(self.turbulencePer,v=1,q=1))
            group = cmds.group(em=1,n='snowFX')
            for x in particles:
                cmds.parent(x.name,group)
            cmds.progressWindow(ep=1)
        except Exception, err:
            sys.stderr.write('ERROR: %s\n' % str(err))
            cmds.progressWindow(ep=1)
            errorPopup('Something went wrong :( \n Check the script editor for detials')
        
    def runPlaneEmit(self,state):
        '''
        Executes the code to emit particles from a plane using the variables defined in snowflakeUI.planeEmitUI and starts the progress window
        Will create an error popup if the variable values would stop the code from functioning correctly
        '''
        if cmds.intField(self.endFrame,v=1,q=1)<=cmds.intField(self.startFrame,v=1,q=1):
            errorPopup('End Frame must be after Start Frame')
            return
        if cmds.intField(self.lifeTime,v=1,q=1)<=0:
            errorPopup('Particles have to have a lifetime')
            return
        if cmds.intField(self.fadeOut,v=1,q=1)>cmds.intField(self.lifeTime,v=1,q=1):
            errorPopup('Lifetime must be larger than fadeout time')
            return
        try:
            vtxCount = cmds.polyEvaluate(cmds.textField(self.sourcePlane,tx=1,q=1),v=1)
            if vtxCount!=4:
                errorPopup('Select an unsubdivided plane')
                return
        except:
            errorPopup('Choose a source plane')
            return
        particleFX.reloadFile()
        cmds.progressWindow(title='SnowFX',
                                      progress=0,
                                      status='Starting up...')
        try:
            particles=self.makeAllParticles()
            particleFX.planeEmit(cmds.textField(self.sourcePlane,tx=1,q=1),
                                           cmds.intField(self.startFrame,v=1,q=1),
                                           cmds.intField(self.endFrame,v=1,q=1)-cmds.intField(self.startFrame,v=1,q=1),
                                           particles,
                                           cmds.floatField(self.maxDistance,v=1,q=1),
                                           cmds.floatField(self.minDistance,v=1,q=1),
                                           cmds.floatField(self.maxAngle,v=1,q=1),
                                           cmds.intField(self.forceTime,v=1,q=1),
                                           cmds.intField(self.lifeTime,v=1,q=1),
                                           cmds.intField(self.lifeTimeVar,v=1,q=1),
                                           cmds.intField(self.fadeOut,v=1,q=1),
                                           cmds.floatField(self.turbulenceAmp,v=1,q=1),
                                           cmds.intField(self.turbulencePer,v=1,q=1),
                                           (cmds.floatField(self.driftX,v=1,q=1),cmds.floatField(self.driftY,v=1,q=1),cmds.floatField(self.driftZ,v=1,q=1)))
            group = cmds.group(em=1,n='snowFX')
            for x in particles:
                cmds.parent(x.name,group)
            cmds.progressWindow(ep=1)
        except Exception, err:
            sys.stderr.write('ERROR: %s\n' % str(err))
            cmds.progressWindow(ep=1)
            errorPopup('Something went wrong :( \n Check the script editor for detials')

    def runFlakeGen(self,state):
        '''
        Executes the code to generate snowflakes and starts the progress window using the variables defined in snowflakeUI.flakeGenUI and starts the progress window
        '''
        cmds.progressWindow(title='SnowFX',
                                      progress=0,
                                      status='Starting up...')
        try:
            particles=makeSnowflakes.makeSnowflakes(cmds.intField(self.flakeNumber,v=1,q=1),
                                                                      cmds.floatField(self.flakeRadius,v=1,q=1),
                                                                      cmds.intField(self.flakeRadiusVar,v=1,q=1),
                                                                      cmds.canvas(self.colour1,rgb=1,q=1),
                                                                      cmds.canvas(self.colour2,rgb=1,q=1),
                                                                      cmds.floatField(self.transparency,v=1,q=1),
                                                                      cmds.floatField(self.glow,v=1,q=1))
            for i in range(0,len(particles)):
                cmds.move(0,0,cmds.floatField(self.flakeRadius,v=1,q=1)*2*i,particles[i])
            group = cmds.group(em=1,n='snowFX')
            for x in particles:
                cmds.parent(x,group)
            cmds.progressWindow(ep=1)
        except Exception, err:
            sys.stderr.write('ERROR: %s\n' % str(err))
            cmds.progressWindow(ep=1)
            errorPopup('Something went wrong :( \n Check the script editor for detials')
                                       
    def makeAllParticles(self):
        '''
        Generates all the required particles
        On End : Returns a list containing the names of all the particles
        '''
        shards=makeSnowflakes.makeShards(cmds.intField(self.shardNumber,v=1,q=1),
                                                          cmds.floatField(self.shardSize,v=1,q=1),
                                                          cmds.intField(self.shardSizeVar,v=1,q=1),
                                                          cmds.canvas(self.colour1,rgb=1,q=1),
                                                          cmds.canvas(self.colour2,rgb=1,q=1),
                                                          cmds.floatField(self.transparency,v=1,q=1),
                                                          cmds.floatField(self.glow,v=1,q=1))
        flakes=makeSnowflakes.makeSnowflakes(cmds.intField(self.flakeNumber,v=1,q=1)+1,
                                                               cmds.floatField(self.flakeRadius,v=1,q=1),
                                                               cmds.intField(self.flakeRadiusVar,v=1,q=1),
                                                               cmds.canvas(self.colour1,rgb=1,q=1),
                                                               cmds.canvas(self.colour2,rgb=1,q=1),
                                                               cmds.floatField(self.transparency,v=1,q=1),
                                                               cmds.floatField(self.glow,v=1,q=1))
        particles = flakes+shards
        cmds.delete(particles[0])
        particles=particles[1:]
        return particles

        
class errorPopup():
    '''
    Contains procedures to create and control an error popup
    '''
    def __init__(self,errorMessage):
        '''
        Creates a window containing an error message
        
        errorMessage : The message to be printed in the window
        '''
        if cmds.window('error', exists = True):
            cmds.deleteUI('error')
            
        self.window = cmds.window('error',t='Error',w=200,h=100,mxb=0,mnb=0,s=0)
        self.layout = cmds.rowColumnLayout(numberOfColumns=1,co=(1,'both',5),ro=(1,'both',5))
        cmds.text(label=errorMessage)
        cmds.button(label='Close',c=self.closeWindow)
        cmds.setParent(self.layout)
        cmds.showWindow(self.window)
        
    def closeWindow(self,state):
        '''
        Closes the error window
        '''
        cmds.deleteUI(self.window)
        
try:
    snowflakeUI()
except Exception, err:
    sys.stderr.write('ERROR: %s\n' % str(err))
    cmds.progressWindow(ep=1)
    errorPopup('Something went wrong :( \n Check the script editor for detials')
    
