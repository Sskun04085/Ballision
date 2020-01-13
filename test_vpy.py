from vpython import *
from math import *
import time, random, requests
import DAN

### for Iottalk
#ServerURL = 'http://IP:9999'      #with non-secure connection
ServerURL = 'https://2.iottalk.tw' #with SSL connection
Reg_addr = 'fjiojsnoijw' #if None, Reg_addr = MAC address

DAN.profile['dm_name']='Ball-Collision'
DAN.profile['df_list']=['Orientation','Orientation-O', 'Orientation_UserA']
#DAN.profile['d_name']= 'Assign a Device Name' 

DAN.device_registration_with_retry(ServerURL, Reg_addr)
#DAN.deregister()  #if you want to deregister this device, uncomment this line
#exit()            #if you want to deregister this device, uncomment this line

### for vpy
class Scene():
	scene.autoscale = False
	Window = canvas(title = "collision\n\n", width = 600, height = 400, center=vec(0, 0, 0), background = color.black)
	ballA = sphere(pos = vector(-5,0,0), radius = 0.5, color = color.orange)
	ballB = sphere(pos = vector(5,0,0), radius = 0.5, color = color.blue)
	#wallR = box(pos = vector(8, 0, 0), size = vector(0.2, 12, 12), color = color.green)
	#wallL = box(pos = vector(-8, 0, 0), size = vector(0.2, 12, 12), color = color.green)
	#wallT = box(pos = vector(0, 8, 0), size = vector(12, 0.2, 12), color = color.magenta)
	#wallD = box(pos = vector(0, -8, 0), size = vector(12, 0.2, 12), color = color.magenta)
	wallB = box(pos = vector(0, 0, -3), size = vector(20, 20, 0.2), color = color.white)

class SystemAttribute():
	def __init__(self, deltaT, dv, t, vscale, friction):
		self.deltaT = deltaT
		self.dv = dv
		self.t = t
		self.vscale = vscale
		self.friction = friction
		self.re = False
		self.end = False
		self.start = False

global system


def BoundaryDetection(ball_A, ball_B):
	### Do Elastic collision
	DirectionA2B = (ball_B.pos - ball_A.pos).norm()
	DirectionB2A = -DirectionA2B

	VectorAlong2B = ball_A.velocity
	if (ball_A.pos - ball_B.pos).mag <= 1.0:
		##cause collision A give B and B give A
		if (ball_A.velocity.dot(DirectionA2B) > 0 and ball_A.velocity.mag >= ball_B.velocity.mag) \
		or (ball_B.velocity.dot(DirectionB2A) > 0 and ball_B.velocity.mag >= ball_A.velocity.mag): ##cause collision A give B
			Parallel2B = DirectionA2B * ball_A.velocity.dot(DirectionA2B)
			Perpendicular2A = ball_A.velocity - Parallel2B
			Parallel2A = DirectionB2A * ball_B.velocity.dot(DirectionB2A)
			Perpendicular2B = ball_B.velocity - Parallel2A
			ball_A.velocity = Perpendicular2A + Parallel2A
			ball_B.velocity = Perpendicular2B + Parallel2B
	return

def InjectFriction(velocity, friction): 
	XEdge = velocity.x ** 2
	YEdge = velocity.y ** 2
	ThirdEdge = (XEdge + YEdge)
	if sqrt(ThirdEdge) <= 0.01:
		velocity = vector(0, 0, 0)
		return velocity
	signX = 1 if velocity.x <= 0 else -1
	signY = 1 if velocity.y <= 0 else -1 

	velocity.x += signX * (XEdge/ThirdEdge) * friction
	velocity.y += signY * (YEdge/ThirdEdge) * friction
	return velocity
### Start
def Start(b0):
	global system
	system.start = True
b0 = button(text="Start", pos=Scene.Window.title_anchor, bind=Start)

### Reset
def Reset(b1):
	global system
	system.re = not system.re
b1 = button(text="Reset", pos=Scene.Window.title_anchor, bind=Reset)

# 
def stop(b2):
    global system
    system.end = not system.end
    
b2 = button(text="Exit", pos=Scene.Window.title_anchor, bind=stop)

def init(ball_A, ball_B):
	global system
	ball_A.pos = vector(-5,0,0)
	ball_A.velocity = vector(0, 0, 0)
	ball_B.pos = vector(5,0,0)
	ball_B.velocity = vector(0, 0, 0)
	system.t = 0
	system.re = False
	system.start = False


if __name__ == '__main__':

	system = SystemAttribute(0.01, 0.1, 0, 0.1, 0.01)
	ball_A = Scene.ballA
	ball_B = Scene.ballB
	"""
	wallL = Scene.wallL
	wallR = Scene.wallR
	wallT = Scene.wallT
	wallD = Scene.wallD
	"""
	wallB = Scene.wallB
	

	ball_A.velocity = vector(0, 0, 0)
	ball_B.velocity = vector(0, 0, 0)
	Data_UserA = []
	Data_UserB = []
	
	varrA = arrow(pos = ball_A.pos, axis = system.vscale*ball_A.velocity, color = color.yellow)
	varrB = arrow(pos = ball_B.pos, axis = system.vscale*ball_B.velocity, color = color.yellow)

	while not system.end:
		### IottalkConnection
		try:
		#DAN.push ('i_0516241', IDF_data) #Push data to an input device feature "Dummy_Sensor"

		#==================================
			ODF_data_UserA = DAN.pull('Orientation_UserA')
			ODF_data_UserB = DAN.pull('Orientation-O')#Pull data from an output device feature "Dummy_Control"
			if ODF_data_UserA != None:
				Data_UserA = ODF_data_UserA
				#print("debug :" , Data_UserA[2])
			if ODF_data_UserB != None:
				Data_UserB = ODF_data_UserB
				#print('1:',ODF_data_UserA[1],' 2:', ODF_data_UserA[2])

		except Exception as e:
			print(e)
			if str(e).find('mac_addr not found:') != -1:
				print('Reg_addr is not found. Try to re-register...')
				DAN.device_registration_with_retry(ServerURL, Reg_addr)
			else:
				print('Connection failed due to unknow reasons.')
				time.sleep(1)    
		time.sleep(0.001)


		if system.start:
			if system.re:
				print("Reset")
				init(ball_A, ball_B)
			##Finish
			if ball_A.pos.x > 10 or ball_A.pos.x < -10 or ball_A.pos.y > 10 or ball_A.pos.y < -10:
				print("PlayerB win")
				system.start = False
				time.sleep(3)
				init(ball_A, ball_B)
				continue
			if ball_B.pos.x > 10 or ball_B.pos.x < -10 or ball_B.pos.y > 10 or ball_B.pos.y < -10:
				print("PlayerA win")
				system.start = False
				time.sleep(3)
				init(ball_A, ball_B)
				continue

			rate(100)
			#k = keysdown() # a list of keys that are down
			###Euler
			ball_A.pos = ball_A.pos + ball_A.velocity*system.deltaT
			#varrA.axis = system.vscale * ball_A.velocity
			#varrA.pos = ball_A.pos

			ball_B.pos = ball_B.pos + ball_B.velocity*system.deltaT
			system.t = system.t + system.deltaT
			###
			"""
			### ball A control
			if 'left' in k: ball_A.velocity.x -= system.dv
			if 'right' in k: ball_A.velocity.x += system.dv
			if 'down' in k: ball_A.velocity.y -= system.dv
			if 'up' in k: ball_A.velocity.y += system.dv
			###
			### ball B control
			if 'a' in k: ball_B.velocity.x -= system.dv
			if 'd' in k: ball_B.velocity.x += system.dv
			if 's' in k: ball_B.velocity.y -= system.dv
			if 'w' in k: ball_B.velocity.y += system.dv
			###
			"""
			### ball A control
			if Data_UserA[2] < 0: ball_A.velocity.x -= system.dv * abs(Data_UserA[2]) / 90
			if Data_UserA[2] > 0: ball_A.velocity.x += system.dv * abs(Data_UserA[2]) / 90
			if Data_UserA[1] > 0: ball_A.velocity.y -= system.dv * abs(Data_UserA[1]) / 90
			if Data_UserA[1] < 0: ball_A.velocity.y += system.dv * abs(Data_UserA[1]) / 90
			###
			### ball B control
			if Data_UserB[2] < 0: ball_B.velocity.x -= system.dv * abs(Data_UserB[2]) / 90
			if Data_UserB[2] > 0: ball_B.velocity.x += system.dv * abs(Data_UserB[2]) / 90
			if Data_UserB[1] > 0: ball_B.velocity.y -= system.dv * abs(Data_UserB[1]) / 90
			if Data_UserB[1] < 0: ball_B.velocity.y += system.dv * abs(Data_UserB[1]) / 90

			### A block to check collision //no use??
			if (ball_A.pos - ball_B.pos).mag <=1.5:
				BoundaryDetection(ball_A, ball_B)
			###
			"""
			if ball_A.pos.x > wallR.pos.x or ball_A.pos.x < wallL.pos.x:
					ball_A.velocity.x = -ball_A.velocity.x
			if ball_A.pos.y > wallT.pos.y or ball_A.pos.y < wallD.pos.y:
					ball_A.velocity.y = -ball_A.velocity.y
			if ball_A.pos.z > 6.0 or ball_A.pos.z < wallB.pos.z:
					ball_A.velocity.z = -ball_A.velocity.z	

			if ball_B.pos.x > wallR.pos.x or ball_B.pos.x < wallL.pos.x:
					ball_B.velocity.x = -ball_B.velocity.x
			if ball_B.pos.y > wallT.pos.y or ball_B.pos.y < wallD.pos.y:
					ball_B.velocity.y = -ball_B.velocity.y
			if ball_B.pos.z > 6.0 or ball_B.pos.z < wallB.pos.z:
					ball_B.velocity.z = -ball_B.velocity.z	
			"""

			ball_A.velocity = InjectFriction(ball_A.velocity, system.friction)
			ball_B.velocity = InjectFriction(ball_B.velocity, system.friction)
	print("GameOver")
	exit()
