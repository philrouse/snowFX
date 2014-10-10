'''
Written by Philip Rouse 2014

Module of procedures to create the particle animations

This module contains the following classes and procedures
class: particles : Contains procedures to animate individual particles and stores there unique variables
        __init__ : Saves the object's name to an instance of the class
        explode  : Emits a particle with decreasing speed
        drift    : Adds particle drift and generates turbulence on new animation layers
        birth    : Makes the particle visible on its birth frame
        death    : Scales down the particle to 0 at the end of its lifetime
        bake     : Combines all animation layers
emitCurve   : Emits particles from a curve
followCurve : Animates a trail of particles following a curve
planeEmit   : Emits particles from a plane
reloadFile  : Reloads Maya scene to free memory and increase performance

In this module, one of the functions is called with a 
particle list. Those particles are then individually 
animated using a combination of the class specific functions.
'''
import maya.cmds as cmds
import random

cmds.cycleCheck(e=0)
cmds.autoKeyframe(state=0)

class particles():
    '''Contains procedures to animate individual particles and stores their unique variables'''
    def __init__(self,name):
        '''Saves the object's name to an instance of the class'''
        
        self.name=name
        
    def explode(self,start,duration,distance):
        '''
        Emits a particle along its local Y axis with decreasing speed
        
        start : Start of emission frame
        duration : Number of frames to reach final destination
        distance : Total distance to move object
        
        The procedure first keys the object's position at the first 
        frame when it is emitted then moves it the set distance along 
        its object Y axis and keys the end frame. Through several if 
        statement, it works out the angles and weights to set the 
        keyframe handles to.
        '''
        cmds.select(self.name)
        if cmds.animLayer('BaseAnimation',exists=True,q=True)==False:
            cmds.animLayer('BaseAnimation',aso=1)
        else:
            cmds.animLayer('BaseAnimation', e=1,aso=1)
        [(startX,startY,startZ)]=cmds.getAttr(self.name+'.translate',t=start)
        cmds.setKeyframe(self.name, at='translateX',t=start,v=startX,al='BaseAnimation')
        cmds.setKeyframe(self.name, at='translateY',t=start,v=startY,al='BaseAnimation')
        cmds.setKeyframe(self.name, at='translateZ',t=start,v=startZ,al='BaseAnimation')
        cmds.currentTime(start+duration)
        distance=distance
        cmds.move(0,distance,0,r=1,os=1)
        cmds.setKeyframe(self.name, at=['translateX','translateY','translateZ'],al='BaseAnimation')
        [(endX,endY,endZ)]=cmds.getAttr(self.name+'.translate')
        cmds.keyTangent(self.name, at=['translateX','translateY','translateZ'], t=(start,start+duration),weightLock=0, weightedTangents=1)
        weightX=(endX-startX)/1.5
        if weightX<0:
            angleX=-80
            weightX=-weightX
        else:
            angleX=80
        weightY=(endY-startY)/1.5
        if weightY<0:
            angleY=-80
            weightY=-weightY
        else:
            angleY=80
        weightZ=(endZ-startZ)/1.5
        if weightZ<0:
            angleZ=-80
            weightZ=-weightZ
        else:
            angleZ=80
        cmds.keyTangent(self.name, at='translateX',t=(start,start),oa=angleX,ow=weightX)
        cmds.keyTangent(self.name, at='translateY',t=(start,start),oa=angleY,ow=weightY)
        cmds.keyTangent(self.name, at='translateZ',t=(start,start),oa=angleZ,ow=weightZ)
        cmds.keyTangent(self.name, at='translateX',t=(start+duration,start+duration),ia=0,iw=duration/1.5)
        cmds.keyTangent(self.name, at='translateY',t=(start+duration,start+duration),ia=0,iw=duration/1.5)
        cmds.keyTangent(self.name, at='translateZ',t=(start+duration,start+duration),ia=0,iw=duration/1.5)

    def drift(self,start,(driftX,driftY,driftZ),turbulenceAmp,turbulencePer):
        '''
        Adds particle drift and generates turbulence on new animation layers
        
        start         : Frame to start the drift and turbulence
        driftX/Y/Z    : Distance to move the particle linearly over 10 frames
        turbulenceAmp : Amplitude of the turbulence animation graph
        turbulencePer : Period of the turbulence animation graph
        
        The procedures creates the two animation layers if they do not already 
        exist then keys the X, Y and Z translate for one frame then sets it to 
        repeat to infinity linearly. It then keys both the translate and rotate 
        channels on the turbulence layer and sets them to repeat and oscillate 
        to infinity.
        '''
        cmds.select(self.name)
        (driftX,driftY,driftZ)=(driftX/10,driftY/10,driftZ/10)
        a='AnimLayerDrift'
        b='AnimLayerTurbulence'
        if cmds.animLayer(a,exists=True,q=True)==False:
            cmds.animLayer(a,aso=1)
        else:
            cmds.animLayer(a, e=1,aso=1)
        if cmds.animLayer(b,exists=True,q=True)==False:
            cmds.animLayer(b,aso=1)
        else:
            cmds.animLayer(b, e=1,aso=1)
        cmds.setKeyframe(self.name, at=['translateX','translateY','translateZ'],t=start,v=0,ott='Linear',al=a,nr=1)
        cmds.setKeyframe(self.name,at='translateX',t=start+1, v=-(driftX*random.uniform(0.5,1.5)),itt='Linear',al=a,nr=1)
        cmds.setKeyframe(self.name,at='translateY',t=start+1, v=-(driftY*random.uniform(0.5,1.5)),itt='Linear',al=a,nr=1)
        cmds.setKeyframe(self.name,at='translateZ',t=start+1, v=-(driftZ*random.uniform(0.5,1.5)),itt='Linear',al=a,nr=1)
        cmds.setAttr(self.name+'_translateX_'+a+'_inputB.postInfinity',1)
        cmds.setAttr(self.name+'_translateY_'+a+'_inputB.postInfinity',1)
        cmds.setAttr(self.name+'_translateZ_'+a+'_inputB.postInfinity',1)
        cmds.setKeyframe(self.name, at=['translateX','translateY','translateZ','rotateX','rotateY','rotateZ'],t=start,v=0,al=b,nr=1)
        cmds.setKeyframe(self.name,at='translateX',t=start+turbulencePer+random.randint(-2,2), v=0.2*random.uniform(-turbulenceAmp,turbulenceAmp),al=b,nr=1)
        cmds.setKeyframe(self.name,at='translateY',t=start+turbulencePer+random.randint(-2,2), v=0.1*random.uniform(-turbulenceAmp,turbulenceAmp),al=b,nr=1)
        cmds.setKeyframe(self.name,at='translateZ',t=start+turbulencePer+random.randint(-2,2), v=0.2*random.uniform(-turbulenceAmp,turbulenceAmp),al=b,nr=1)
        cmds.setKeyframe(self.name,at='rotateX',t=start+turbulencePer+random.randint(-2,2), v=100*random.uniform(-turbulenceAmp,turbulenceAmp),al=b,nr=1)
        cmds.setKeyframe(self.name,at='rotateY',t=start+turbulencePer+random.randint(-2,2), v=100*random.uniform(-turbulenceAmp,turbulenceAmp),al=b,nr=1)
        cmds.setKeyframe(self.name,at='rotateZ',t=start+turbulencePer+random.randint(-2,2), v=100*random.uniform(-turbulenceAmp,turbulenceAmp),al=b,nr=1)
        cmds.setAttr(self.name+'_translateX_'+b+'_inputB.postInfinity',5)
        cmds.setAttr(self.name+'_translateY_'+b+'_inputB.postInfinity',5)
        cmds.setAttr(self.name+'_translateZ_'+b+'_inputB.postInfinity',5)
        cmds.setAttr(self.name+'_rotate_'+b+'_inputBX.postInfinity',4)
        cmds.setAttr(self.name+'_rotate_'+b+'_inputBY.postInfinity',4)
        cmds.setAttr(self.name+'_rotate_'+b+'_inputBZ.postInfinity',4)
        
    def birth(self):
        '''Keys object visibility to 'off' before its birth frame and 'on' on its birth frame'''
        
        cmds.setKeyframe(self.name,at='visibility',v=0,t=self.born-1,al='BaseAnimation')        
        cmds.setKeyframe(self.name,at='visibility',v=1,t=self.born,al='BaseAnimation')
    
    def death(self):
        '''
        Through several if statements, validates the lifeTime and fadeOut 
        values, then keys scale channel to 0 over fade out time and then 
        sets visibility to 'off'
        '''
        if self.lifeTime<=0:
            self.lifeTime=2
        if self.fadeOut<0:
            self.fadeOut=0
        if self.fadeOut>self.lifeTime:
            self.fadeOut=self.lifeTime
        cmds.setKeyframe(self.name,at='scale',v=1,t=self.born+self.lifeTime-self.fadeOut,al='BaseAnimation')        
        cmds.setKeyframe(self.name,at='scale',v=0,t=self.born+self.lifeTime+1,al='BaseAnimation')
        cmds.setKeyframe(self.name,at='visibility',v=1,t=self.born+self.lifeTime,al='BaseAnimation')        
        cmds.setKeyframe(self.name,at='visibility',v=0,t=self.born+self.lifeTime+1,al='BaseAnimation')
    
    def bake(self):
        '''Bakes animation from all animation layers to the 'BaseAnimation' layer'''
        
        cmds.bakeResults(self.name,t=(self.born,self.born+self.lifeTime+1),sm=0,sr=(1,5),dic=1,pok=0,sac=1,ral=1,bol=0,mr=0,s=1)
    
def emitCurve(sourceCurve,curveStart,duration,particleList,maxDistance,minDistance,emitTime,lifeTime,lifeTimeVar,fadeOut,turbulenceAmp,turbulencePer,drift):
    '''
    Emits particles from a curve
    
    sourceCurve   : Name of the curve particles will emit from
    curveStart    : Frame to start emission
    duration      : Number of frames to emit for
    particleList  : List containing names of all the particles to be animatied
    maxDistance   : Maximum distance particles will be emitted from at the middle of the curve
    minDistance   : Maximum distance particles will be emitted from at the start and end of the curve
    emitTime      : Number of frames particles will be affected by the emission force
    lifeTime      : Average lifetime of a particle
    lifeTimeVar   : Variation from average lifetime as a percentage
    fadeOut       : Number of frames to scale down particles at the end of their lifetime
    turbulenceAmp : Amplitude of the turbulence animation graph
    turbulencePer : Period of the turbulence animation graph
    drift         : Distance a particle will drift 10 frames. Contains (x,y,z)
    
    Updates the progress window and assigns all the elements in particleList to the class particles. 
    Creates a locator and keys it to follow the curve linearly over the emission time. At the emit 
    time, copies the coordinates of the locator and moves particle to that location and add a random 
    rotation. The distance is calculated depending on the time the particle is emitted. Runs the 
    relevant class specific procedures to animate the particle.
    '''
    cmds.progressWindow(e=1,progress=0,status='Animating Particles...')
    for i in range(0,len(particleList)):
        particleList[i]=particles(particleList[i])
    count=0
    [emitter] = [cmds.spaceLocator(n='emitter')[0]]
    motionPath = cmds.pathAnimation(fm=1, stu=curveStart,etu=curveStart+duration,c=sourceCurve)
    cmds.keyTangent(motionPath,at='uValue',itt='Linear',ott='Linear')
    for x in particleList:
        launchTime=random.uniform(0,duration)
        [(emitX,emitY,emitZ)]=cmds.getAttr(emitter+'.translate',t=curveStart+launchTime)
        cmds.move(emitX,emitY,emitZ,x.name)
        cmds.rotate(random.uniform(0,360),random.uniform(0,360),random.uniform(0,360),x.name)
        if launchTime/duration <=0.5:
            distance=(launchTime/duration)*2*(maxDistance-minDistance)+minDistance
        else:
            distance=(1-(launchTime/duration))*2*(maxDistance-minDistance)+minDistance
        x.born = int(curveStart+launchTime+random.randint(-1,1))
        x.explode(x.born,emitTime,distance)
        x.drift(x.born,drift,turbulenceAmp*random.random(),turbulencePer+random.randint(-2,2))
        x.lifeTime=int(lifeTime+random.uniform(-lifeTime*lifeTimeVar*0.01,lifeTime*lifeTimeVar*0.01))
        x.fadeOut=random.randint(fadeOut-2,fadeOut+2)
        x.bake()
        cmds.keyframe(x.name,at='visibility',a=1,vc=0)
        count+=1
        cmds.progressWindow(e=1,progress=int((100.0/len(particleList))*count))
    for x in particleList:
        x.birth()
        x.death()
    return
    
def followCurve(sourceCurve,curveStart,duration,particleList,maxDistance,minDistance,nose,tail,length,turbulenceAmp,turbulencePer):
    '''
    Creates a trail of particles following the source curve
    
    sourceCurve   : Name of the curve particles will emit from
    curveStart    : Frame to start emission
    duration      : Number of frames to emit for
    particleList  : List containing names of all the particles to be animatied
    maxDistance   : Maximum distance particles will be emitted from the curve at the middle of the trail
    minDistance   : Maximum distance particles will be emitted from the curve at the nose and tail of the trail
    nose          : Number of frames to taper the front of the trail
    tail          : Number of frames to taper the end of the trail
    length        : Length of the trail in frames
    emitTime      : Number of frames particles will be affected by the emission force
    turbulenceAmp : Amplitude of the turbulence animation graph
    turbulencePer : Period of the turbulence animation graph
    
    Updates the progress window and assigns all the elements in particleList to the class particles. 
    Particle assigned to the source curve as a motion path and this motion is baked here as Maya 
    doesn't correctly combine animation layers when motion paths are used. The particle offset 
    calculated and keyed. Turbulence is added and visibility is temporarily set to 'off' to speed up
    processing of subsequent particles. After all particles are animated, birth and death are keyed.
    '''
    cmds.progressWindow(e=1,progress=0,status='Animating Particles...')
    for i in range(0,len(particleList)):
        particleList[i]=particles(particleList[i])
    count=0
    for x in particleList:
        launch = random.uniform(0,length)
        x.born = curveStart+int(launch)
        x.lifeTime = duration+random.randint(-(length/4),(length/4))
        motionPath = cmds.pathAnimation(x.name, fm=1, stu=curveStart+launch, etu=x.born+x.lifeTime, c=sourceCurve)
        cmds.keyTangent(motionPath,at='uValue',itt='Linear',ott='Linear')
        cmds.bakeResults(x.name,at=['translateX','translateY','translateZ'],t=(x.born,x.born+x.lifeTime+1),sm=1,dic=1,pok=0,sac=1,sb=1,ral=1,bol=0,mr=0,s=1)
        if launch<nose:
            distance = ((launch/float(nose))*(maxDistance-minDistance))+minDistance
        elif length-launch<tail:
            distance = (((length-launch)/float(tail))*(maxDistance-minDistance))+minDistance
        else:
            distance = maxDistance
        a = 'AnimLayerOffset'
        cmds.select(x.name)
        if cmds.animLayer(a,exists=True,q=True)==False:
            cmds.animLayer(a,aso=1)
        else:
            cmds.animLayer(a, e=1,aso=1)
        cmds.setKeyframe(x.name,at='translateX',t=x.born, v=random.uniform(-distance,distance),al=a,nr=1)
        cmds.setKeyframe(x.name,at='translateY',t=x.born, v=random.uniform(-distance,distance),al=a,nr=1)
        cmds.setKeyframe(x.name,at='translateZ',t=x.born, v=random.uniform(-distance,distance),al=a,nr=1)
        cmds.setKeyframe(x.name,at='rotateX',t=x.born, v=random.uniform(0,360),al=a,nr=1)
        cmds.setKeyframe(x.name,at='rotateY',t=x.born, v=random.uniform(0,360),al=a,nr=1)
        cmds.setKeyframe(x.name,at='rotateZ',t=x.born, v=random.uniform(0,360),al=a,nr=1)
        x.drift(x.born,(0,0,0),turbulenceAmp*random.random(),turbulencePer+random.randint(-2,2))
        x.bake()
        cmds.keyframe(x.name,at='visibility',a=1,vc=0)
        count+=1
        cmds.progressWindow(e=1,progress=int((100.0/len(particleList))*count))
    for x in particleList:
        x.fadeOut = 0
        x.birth()
        x.death()
    return
    
def planeEmit(sourcePlane,start,emitTime,particleList,maxDistance,minDistance,maxAngle,forceTime,lifeTime,lifeTimeVar,fadeOut,turbulenceAmp,turbulencePer,drift):
    '''
    Emits particles from a plane
    
    sourcePlane   : Name of the plane particles will emit from
    start         : Frame to start emission
    emitTime      : Number of frames to emit for
    particleList  : List containing names of all the particles to be animatied
    maxDistance   : Maximum distance particles will be emitted from at the middle of the curve
    minDistance   : Maximum distance particles will be emitted from at the start and end of the curve
    maxAngle      : Maximum angle to emit particles at
    forceTime     : Number of frames particles will be affected by the emission force
    lifeTime      : Average lifetime of a particle
    lifeTimeVar   : Variation from average lifetime as a percentage
    fadeOut       : Number of frames to scale down particles at the end of their lifetime
    turbulenceAmp : Amplitude of the turbulence animation graph
    turbulencePer : Period of the turbulence animation graph
    drift         : Distance a particle will drift 10 frames. Contains (x,y,z)
    
    Updates the progress window and assigns all the elements in particleList to the class particles. 
    Constrains particle to plane to copy its location and orientation then deletes the constraint 
    and adds a random rotation in the object y axis and moves the particle a random distance away 
    from the plane centre along its surface. Emission angle is randomly chosen and applied to object 
    z axis so that all particles move in line with the plane centre. Runs the relevant class specific 
    procedures to animate the particle.
    '''
    cmds.progressWindow(e=1,progress=0,status='Animating Particles...')
    for i in range(0,len(particleList)):
        particleList[i]=particles(particleList[i])
    count=0
    for x in particleList:
        x.born = start+random.randint(0,emitTime)
        constraint = cmds.parentConstraint(sourcePlane,x.name)
        cmds.delete(constraint)
        rotation = random.uniform(0,360)
        cmds.rotate(0,rotation,0,x.name,r=1,os=1)
        [x0,y0,z0,x1,y1,z1]=cmds.xform(sourcePlane+'.vtx[0:1]',t=1,q=1,ws=1)
        sideLength=((x0-x1)**2+(y0-y1)**2+(z0+z1)**2)**0.5
        distance=random.uniform(0,sideLength/2)
        cmds.move(distance,0,0,x.name,r=1,os=1)
        angle=random.uniform(-maxAngle,maxAngle)
        cmds.rotate(0,0,angle,x.name,r=1,os=1)
        x.explode(x.born,forceTime,random.uniform(minDistance,maxDistance))
        x.drift(x.born,drift,turbulenceAmp*random.random(),turbulencePer+random.randint(-2,2))
        x.lifeTime=int(lifeTime+random.uniform(-lifeTime*lifeTimeVar*0.01,lifeTime*lifeTimeVar*0.01))
        x.fadeOut=random.randint(fadeOut-2,fadeOut+2)
        x.bake()
        cmds.keyframe(x.name,at='visibility',a=1,vc=0)
        count+=1
        cmds.progressWindow(e=1,progress=int((100.0/len(particleList))*count))
    for x in particleList:
        x.birth()
        x.death()
    return
        
    
def reloadFile():
    '''
    Reloads Maya scene to free memory and increase performance.
    
    A copy of the file is saved as filename.tmp and opened. The open file is renamed to the original filename
    '''
    deState = cmds.file(de=1,q=1)
    cmds.file(de=0)
    fullFileName = cmds.file(exn=1,q=1)
    fileName = fullFileName.rpartition('/')[-1]
    fileLocation = fullFileName.rpartition('/')[0]
    tmpName = cmds.file(rn=fileName+'.tmp')
    cmds.file(s=1,de=0)
    cmds.file(new=1,force=1)
    cmds.file(tmpName,o=1)
    cmds.file(rn=fileName)
    cmds.file(de=deState)
    cmds.flushUndo()
