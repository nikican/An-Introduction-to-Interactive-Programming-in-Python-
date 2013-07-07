# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
width = 800
height = 600
score = 0
lives = 3
time = 0
rotatingRight = False
rotatingLeft = False
paused = False
thrust_rel = False
brake_rel = False

to_blink = False
blink_length = 0
blinked_out = False

starting = True

submission = False

velocity = 0.22
brake_vel = 0.15
ang_velocity = 5
acc_rate = 10
friction = 0.99

quick_shot_on = False

rocks = set([])
explosions = set([])
powerUps = []
power_up_waiting = None

total_big_rocks = 0

shot_vel = 10
shot_vel_hom = 5


class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated
        

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# missile image - shot1.png, shot2.png, shot3.png
homing_missile_info = ImageInfo([5,5], [10, 10], 3, 1000)
homing_missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot1.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blend.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.1)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0]-q[0])**2+(p[1]-q[1])**2)

def spawn_power_up(pos, vel):
    PUtype = random.choice(["Shrink", "QuickShot", "Homing"])
    if PUtype == "Shrink":
        label = "S"
        lifespan = 10
        color_circle = "red"
        color_font = "white"
    if PUtype == "QuickShot":
        label = "Q"
        lifespan = 10
        color_circle = "white"
        color_font = "black"
    if PUtype == "Homing":
        label = "H"
        lifespan = 10
        color_circle = "yellow"
        color_font = "purple"
    powerUps.append(PowerUp(PUtype, pos, vel, 10, lifespan, label, color_circle, color_font))

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.brake = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.powerUp = None
        ship_thrust_sound.set_volume(0.1)
        self.shrinkage = 0
        self.enlarge = self.image_size[0]
        self.missiles = set([])
        
    def draw(self,canvas):
        if self.powerUp != None:
            if self.powerUp.PUtype == "Shrink":
                if self.shrinkage > self.image_size[0] / 2:
                    self.shrinkage = self.shrinkage - 1
                    drawSize = self.shrinkage
                else:
                    drawSize = self.image_size[0] / 2
                    if self.enlarge < self.image_size[0]:
                        self.enlarge = self.enlarge + 1
                        drawSize = self.enlarge
                    elif self.shrinkage == 0:
                        self.resetPowerUp()
                        self.enlarge = self.image_size[0]
                if self.thrust == False:
                    canvas.draw_image(ship_image, self.image_center, self.image_size, self.pos, [drawSize, drawSize], self.angle)
                    if self.brake:
                        canvas.draw_image(ship_image, [(self.image_center[0] + 55), self.image_center[0]] , [30,20], [self.pos[0] + (round((drawSize)/2)+1) * math.cos(self.angle), self.pos[1] + (round((drawSize)/2)+1) * math.sin(self.angle)], [15 + round(drawSize/6), 10 + round(drawSize/9)], math.radians(180) + self.angle)
                else:
                    canvas.draw_image(ship_image, [(self.image_center[0] + 90), self.image_center[0]] , self.image_size, self.pos, [drawSize, drawSize], self.angle)
            else:
                if self.thrust == False:
                    if self.brake == False:
                        canvas.draw_image(ship_image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
                    else:
                        canvas.draw_image(ship_image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
                        canvas.draw_image(ship_image, [(self.image_center[0] + 55), self.image_center[0]] , [30,20], [self.pos[0] + (45 * math.cos(self.angle)), self.pos[1] + (45 * math.sin(self.angle))], [30,20], math.radians(180) + self.angle)
                else:
                    canvas.draw_image(ship_image, [(self.image_center[0] + 90), self.image_center[0]] , self.image_size, self.pos, self.image_size, self.angle)
        else: 
            if self.thrust == False:
                if self.brake == False:
                    canvas.draw_image(ship_image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
                else:
                    canvas.draw_image(ship_image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
                    canvas.draw_image(ship_image, [(self.image_center[0] + 55), self.image_center[0]] , [30,20], [self.pos[0] + (45 * math.cos(self.angle)), self.pos[1] + (45 * math.sin(self.angle))], [30,20], math.radians(180) + self.angle)
            else:
                canvas.draw_image(ship_image, [(self.image_center[0] + 90), self.image_center[0]] , self.image_size, self.pos, self.image_size, self.angle)

    def rotate(self, clockwise, stop):
        if stop == False:
            if clockwise:
                self.angle_vel = - math.radians(ang_velocity)
            else:
                self.angle_vel = math.radians(ang_velocity)
        else:
            self.angle_vel = 0
            
    def thrusting(self, start):
        if start:
            self.thrust = True
            ship_thrust_sound.play()
        else:
            self.thrust = False
            ship_thrust_sound.rewind()
    
    def braking(self, start):
        if start:
            self.brake = True
            ship_thrust_sound.play()
        else:
            self.brake = False
            ship_thrust_sound.rewind()
            
    def shoot(self):
        if self.powerUp != None:
            if self.powerUp.PUtype == "Homing":
                if len(self.missiles) == 0:
                    self.missiles.add(Sprite([self.pos[0] + (45 * math.cos(self.angle)) , self.pos[1] + (45 * math.sin(self.angle))], [self.vel[0] + (shot_vel * math.cos(self.angle)), self.vel[1] + (shot_vel * math.sin(self.angle))], 0, 0, homing_missile_image, homing_missile_info, missile_sound, 1, "Missile"))
            else:
                self.missiles.add(Sprite([self.pos[0] + (45 * math.cos(self.angle)) , self.pos[1] + (45 * math.sin(self.angle))], [self.vel[0] + (shot_vel * math.cos(self.angle)), self.vel[1] + (shot_vel * math.sin(self.angle))], 0, 0, missile_image, missile_info, missile_sound, 1, "Missile"))
        else:
            self.missiles.add(Sprite([self.pos[0] + (45 * math.cos(self.angle)) , self.pos[1] + (45 * math.sin(self.angle))], [self.vel[0] + (shot_vel * math.cos(self.angle)), self.vel[1] + (shot_vel * math.sin(self.angle))], 0, 0, missile_image, missile_info, missile_sound, 1, "Missile"))
        
    def collectPowerUp(self, powerUp):
        global quick_shot_on, power_up_waiting
        if self.powerUp != None:
            if self.powerUp.PUtype == powerUp.PUtype:
                self.powerUp.age = 0
            else:
                if self.powerUp.PUtype == "Shrink":
                    my_ship.enlarge = 45
                    my_ship.shrinkage = 0
                    power_up_waiting = powerUp
                    powerUps.remove(powerUp)
                else:
                    self.resetPowerUp()
        if self.powerUp == None:
            self.powerUp = powerUp
            if self.powerUp.PUtype == "Shrink":
                self.radius = self.radius/2
                self.shrinkage = self.image_size[0]
            if self.powerUp.PUtype == "QuickShot":
                quick_shot_on = True
        if power_up_waiting == None:
            powerUps.remove(powerUp)
            
        
    def resetPowerUp(self):
        global quick_shot_on, power_up_waiting
        if self.powerUp != None:
            if self.powerUp.PUtype == "Shrink":
                self.radius = self.radius * 2
                self.powerUp = None
            elif self.powerUp.PUtype == "QuickShot":
                quick_shot_on = False
                self.powerUp = None
            else:
                self.powerUp = None
        if power_up_waiting != None:
            self.collectPowerUp(power_up_waiting)
            power_up_waiting = None
            
        
    
    def hit(self):
        global lives, starting, rocks, to_blink, powerUps, power_up_waiting
        lives = lives - 1
        explosions.add(Sprite([self.pos[0], self.pos[1]], [0, 0], 0, 0, explosion_image, explosion_info, explosion_sound))
        if lives == 0:
            starting = True
            soundtrack.rewind()
            rocks = set([])
            timer.stop()
            powerUps = []
            power_up_waiting = None
            self.resetPowerUp()
            self.powerUp = None
            total_big_rocks = 0
        else:
            to_blink = True
            timer_blink.start()
            power_up_waiting = None
            self.resetPowerUp()
        
        self.pos = [width / 2, height / 2]
        self.vel = [0, 0]
        self.angle = 0
        self.angle_vel = 0
        self.thrust = False
        self.brake = False
        powerUp_On = False
        
        
    
    def update(self):
        global powerUp_On, score, to_blink, a_powerUp
        self.pos[0] = (self.pos[0] + self.vel[0]) % width
        """if self.pos[0] > (width + self.radius):
            self.pos[0] = - self.radius 
        if self.pos[0] < - self.radius:
            self.pos[0] = (width + self.radius)"""
        self.pos[1] = (self.pos[1] + self.vel[1]) % height
        """if self.pos[1] > (height + self.radius):
            self.pos[1] = - self.radius
        if self.pos[1] < - self.radius:
            self.pos[1] = (height + self.radius)"""
        self.vel[0] = self.vel[0] * friction
        self.vel[1] = self.vel[1] * friction 
        self.angle = self.angle + self.angle_vel
        if self.thrust:
            self.vel[0] = self.vel[0] + velocity * math.cos(self.angle)
            self.vel[1] = self.vel[1] + velocity * math.sin(self.angle)
        if self.brake:
            self.vel[0] = self.vel[0] - brake_vel * math.cos(self.angle)
            self.vel[1] = self.vel[1] - brake_vel * math.sin(self.angle)
        
        if to_blink == False:
            for w in powerUps:
                if dist([self.pos[0], self.pos[1]], [w.pos[0], w.pos[1]]) <= self.radius + w.radius:
                    self.collectPowerUp(w)
                
        
        for x in list(self.missiles):
            if x.age == x.lifespan:
                self.missiles.remove(x)
        
        rocks_to_remove = set([])
        for y in rocks:
            if to_blink == False:
                if dist([self.pos[0], self.pos[1]], [y.pos[0], y.pos[1]]) <= (self.radius + y.radius):
                    self.hit()
            for x in list(self.missiles):
                if dist([x.pos[0], x.pos[1]], [y.pos[0], y.pos[1]]) <= (x.radius + y.radius):
                    self.missiles.remove(x)
                    rocks_to_remove.add(y)
                    score = score + 10
                    explosions.add(Sprite([y.pos[0], y.pos[1]], [0, 0], 0, 0, explosion_image, explosion_info, explosion_sound))
                    if y.size_ratio == 1:
                        score = score + 10
                        rocks.add(Sprite([y.pos[0], y.pos[1]], [random.choice([-1, 1]) * (random.random()), random.choice([-1, 1]) * (random.random())], 0, random.choice([-1, 1]) * math.radians(random.randrange(1, 10)), asteroid_image, asteroid_info, None, 0.5))
                        rocks.add(Sprite([y.pos[0], y.pos[1]], [random.choice([-1, 1]) * (random.random()), random.choice([-1, 1]) * (random.random())], 0, random.choice([-1, 1]) * math.radians(random.randrange(1, 10)), asteroid_image, asteroid_info, None, 0.5))
                        rocks.add(Sprite([y.pos[0], y.pos[1]], [random.choice([-1, 1]) * (random.random()), random.choice([-1, 1]) * (random.random())], 0, random.choice([-1, 1]) * math.radians(random.randrange(1, 10)), asteroid_image, asteroid_info, None, 0.5))
                    if y.size_ratio == 0.5:
                        score = score + 100
                        rocks.add(Sprite([y.pos[0], y.pos[1]], [random.choice([-1, 1]) * (random.random()), random.choice([-1, 1]) * (random.random())], 0, random.choice([-1, 1]) * math.radians(random.randrange(1, 10)), asteroid_image, asteroid_info, None, 0.25))
                        rocks.add(Sprite([y.pos[0], y.pos[1]], [random.choice([-1, 1]) * (random.random()), random.choice([-1, 1]) * (random.random())], 0, random.choice([-1, 1]) * math.radians(random.randrange(1, 10)), asteroid_image, asteroid_info, None, 0.25))
                        #rocks.add(Sprite([y.pos[0], y.pos[1]], [0, 0], 0, random.choice([-1, 1]) * math.radians(random.randrange(1, 10)), asteroid_image, asteroid_info, None, 0.25))
                        rocks.add(Sprite([y.pos[0], y.pos[1]], [random.choice([-1, 1]) * (random.random()), random.choice([-1, 1]) * (random.random())], 0, random.choice([-1, 1]) * math.radians(random.randrange(1, 10)), asteroid_image, asteroid_info, None, 0.25))
                    if y.size_ratio == 0.25:
                        score = score + 1000
                        powerUp_On = True
                        spawn_power_up(y.pos, [0, 0])

        rocks.difference_update(rocks_to_remove)
        
                
     
        
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None, size_ratio = 1, kind = "None"):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.size_ratio = size_ratio
        self.radius = info.get_radius() * self.size_ratio
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.kind = kind
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, [self.image_size[0]*self.size_ratio, self.image_size[1]*self.size_ratio], self.angle)
    
    def update(self):
        
        """if self.pos[0] > (width + self.radius):
            self.pos[0] = - self.radius 
        if self.pos[0] < - self.radius:
            self.pos[0] = (width + self.radius)
        
        if self.pos[1] > (height + self.radius):
            self.pos[1] = - self.radius
        if self.pos[1] < - self.radius:
            self.pos[1] = (height + self.radius)"""
        
        self.angle = self.angle + self.angle_vel
        if self.lifespan != None:
            self.age = self.age + 1
                       
        if self.animated:
            self.image_center[0] = (self.age * self.image_size[0]) - (self.image_size[0] / 2)
        
               
        if my_ship.powerUp != None:
            if my_ship.powerUp.PUtype == "Homing":
                if self.kind == "Missile" and len(rocks) > 0:
                    distance = 100000
                    closest_rock = None
                    
                    for y in rocks:
                        if dist(y.pos, self.pos) < distance:
                            distance = dist(y.pos, self.pos)
                            #print distance
                            closest_rock = y
                    vector = [0, 0]
                    vector[0] = - math.cos(math.atan2(self.pos[1] - closest_rock.pos[1], self.pos[0] - closest_rock.pos[0]))
                    vector[1] = - math.sin(math.atan2(self.pos[1] - closest_rock.pos[1], self.pos[0] - closest_rock.pos[0]))
                    self.pos[0] = (self.pos[0] + shot_vel_hom * vector[0]) % width
                    self.pos[1] = (self.pos[1] + shot_vel_hom * vector[1]) % height
                else:  
                    self.pos[0] = (self.pos[0] + self.vel[0]) % width
                    self.pos[1] = (self.pos[1] + self.vel[1]) % height 
            else:
                self.pos[0] = (self.pos[0] + self.vel[0]) % width
                self.pos[1] = (self.pos[1] + self.vel[1]) % height 
                    
        else:
            self.pos[0] = (self.pos[0] + self.vel[0]) % width
            self.pos[1] = (self.pos[1] + self.vel[1]) % height 
                    
              

# PowerUp class
class PowerUp:
    def __init__(self, PUtype, pos, vel, radius, lifespan, label, color_circle, color_font):
        self.PUtype = PUtype
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.radius = radius
        self.lifespan = lifespan
        self.label = label
        self.color_circle = color_circle
        self.color_font = color_font
        self.age = 0
        
   
    
    def draw(self, canvas):
        canvas.draw_circle(self.pos, self.radius, 1, self.color_circle, self.color_circle)
        canvas.draw_text(self.label, [self.pos[0] - self.radius/1.7, self.pos[1] + self.radius*0.8], self.radius * 1.8, self.color_font)
    
    def update(self):
        self.pos[0] = (self.pos[0] + self.vel[0]) % width
        self.pos[1] = (self.pos[1] + self.vel[1]) % height
                   
def draw(canvas):
    global time, a_powerUp, pause, lives, score, blinked_out
   
    # animate background
    if paused == False:
        time += 1
    center = debris_info.get_center()
    size = debris_info.get_size()
    wtime = (time / 8) % center[0]
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [width/2, height/2], [width, height])
    canvas.draw_image(debris_image, [center[0]-wtime, center[1]], [size[0]-2*wtime, size[1]], 
                                [width/2+1.25*wtime, height/2], [width-2.5*wtime, height])
    canvas.draw_image(debris_image, [size[0]-wtime, center[1]], [2*wtime, size[1]], 
                                [1.25*wtime, height/2], [2.5*wtime, height])

    
    for z in explosions:
        z.draw(canvas)
    
    # draw ship and sprites
    if blinked_out == False:
        my_ship.draw(canvas)
    for y in rocks:
        y.draw(canvas)
    for x in my_ship.missiles:
        x.draw(canvas)
    for w in powerUps:
        w.draw(canvas)
    
    # update ship and sprites
    if paused == False:
        my_ship.update()
        for y in rocks:
            y.update()
        for x in my_ship.missiles:
            x.update()
        for z in list(explosions):
            z.update()
            if z.age == z.lifespan:
                explosions.remove(z)
            
    

    canvas.draw_text("Lives: " + str(lives), [50, 50], 20, "yellow")
    canvas.draw_text("Score: " + str(score), [600, 50], 20, "yellow")
   
    if my_ship.powerUp != None:
        canvas.draw_text("Power Up: " + str(my_ship.powerUp.PUtype), [50, 520], 20, "yellow")
        canvas.draw_text("Timer: " + str(my_ship.powerUp.lifespan - my_ship.powerUp.age), [50, 550], 20, "yellow")
        
        
    if starting == True:
        canvas.draw_image(splash_image, splash_info.get_center(), splash_info.get_size(), [width/2, height/2], splash_info.get_size())
        
            
def keydown(key):
    global paused, thrust_rel, brake_rel, powerUp_On, a_powerUp, rotatingRight, rotatingLeft
    if starting == False:
        if paused == False:
            if key == simplegui.KEY_MAP["left"]:
                my_ship.rotate(True, False)
                rotatingLeft = True
            if key == simplegui.KEY_MAP["right"]:
                my_ship.rotate(False, False)
                rotatingRight = True
            if key == simplegui.KEY_MAP["space"]:
                if quick_shot_on:
                    timer_power_ups.start()
                else:
                    my_ship.shoot()
        if key == simplegui.KEY_MAP["up"]:
            if paused == False:
                my_ship.thrusting(True)
            else:
                thrust_rel = False
        if key == simplegui.KEY_MAP["down"]:
            if paused == False:
                my_ship.braking(True)
            else:
                brake_rel = False    
                
                
        
        if key == simplegui.KEY_MAP["p"]:
            if paused == False:
                paused = True
                timer.stop()
                timerPowerUp.stop()
                ship_thrust_sound.pause()
                soundtrack.pause()
            else:
                paused = False
                soundtrack.play()
                if (thrust_rel == False or brake_rel == False) and (my_ship.thrust or my_ship.brake):
                    ship_thrust_sound.play()
                if thrust_rel:
                    my_ship.thrusting(False)
                    thrust_rel = False
                if brake_rel:
                    my_ship.braking(False)
                    brake_rel = False
                timer.start()
                timerPowerUp.start()
            
   
def keyup(key):
    global thrust_rel, brake_rel, rotatingRight, rotatingLeft
    if paused == False:
        if key == simplegui.KEY_MAP["left"]:
            rotatingLeft = False
            if rotatingRight == False:
                my_ship.rotate(True, True)
        if key == simplegui.KEY_MAP["right"]:
            rotatingRight = False
            if rotatingLeft == False:
                my_ship.rotate(False, True)
    if key == simplegui.KEY_MAP["up"]:
        if paused == False:
            my_ship.thrusting(False)
        else:
            thrust_rel = True
    if key == simplegui.KEY_MAP["down"]:
        if paused == False:
            my_ship.braking(False)
        else:
            brake_rel = True
    if key == simplegui.KEY_MAP["space"]:
        if quick_shot_on:
            timer_power_ups.stop()
        
def mouse_click(position):
    global starting, lives, score
    if starting == True:
        if ((width / 2) - (splash_info.get_size()[0] / 2)) <= position[0] <= ((width / 2) + (splash_info.get_size()[0] / 2)) and ((height / 2) - (splash_info.get_size()[1] / 2)) <= position[1] <= ((height / 2) + (splash_info.get_size()[1] / 2)):
            starting = False
            soundtrack.play()
            timer.start()
            lives = 3
            score = 0

def powerUpExpiration():
    if my_ship.powerUp != None:
        my_ship.powerUp.age += 1
        if my_ship.powerUp.age == my_ship.powerUp.lifespan:
            if my_ship.powerUp.PUtype == "Shrink":
                my_ship.enlarge = 45
                my_ship.shrinkage = 0
            else:
                my_ship.resetPowerUp()
    
        
# timer handler that spawns a rock    
def rock_spawner():
    global rocks, submission, total_big_rocks
    if len(rocks) == 0:
        total_big_rocks = total_big_rocks + 1
        for x in range(total_big_rocks):
            rock_pos = [0, 0]
            rock_speed = [0, 0]
            if submission:
                rock_pos[0] = random.randrange(0, width)
                rock_pos[1] = random.randrange(0, height)
                rock_speed[0] = random.choice([-1, 1]) * (random.random())
                rock_speed[1] = random.choice([-1, 1]) * (random.random())
            else:
                side = random.randrange(1, 5)
                if side == 1:
                    rock_pos[0] = 0
                    rock_pos[1] = random.randrange(0, height)
                    rock_speed[0] = random.random()
                    rock_speed[1] = random.choice([-1, 1]) * (random.random())
                if side == 2:
                    rock_pos[1] = 0
                    rock_pos[0] = random.randrange(0, width)
                    rock_speed[0] = random.choice([-1, 1]) * (random.random())
                    rock_speed[1] = - (random.random())
                if side == 3:
                    rock_pos[0] = width
                    rock_pos[1] = random.randrange(0, height)
                    rock_speed[0] = - (random.random())
                    rock_speed[1] = random.choice([-1, 1]) * (random.random())
                if side == 4:
                    rock_pos[1] = height
                    rock_pos[0] = random.randrange(0, width)
                    rock_speed[0] = random.choice([-1, 1]) * (random.random())
                    rock_speed[1] = (random.random())
            rock_ang_vel = random.choice([-1, 1]) * math.radians(random.randrange(1, 10))
            
            rocks.add(Sprite([rock_pos[0], rock_pos[1]], [rock_speed[0], rock_speed[1]], 0, rock_ang_vel, asteroid_image, asteroid_info))

def rock_spawner_test():
    rocks.add(Sprite([200, 200], [0, 0], 0, 0, asteroid_image, asteroid_info, None, 0.25))
    #rocks.add(Sprite([500, 500], [0, 0], 0, 0, asteroid_image, asteroid_info, None, 0.25))
    
            
            
def ship_blinking():
    global to_blink, blinked_out, blink_length	
    
    if to_blink:
        if blinked_out == True:
            blinked_out = False
        else:
            blinked_out = True
        blink_length = blink_length + 1
        if blink_length == 20:
            to_blink = False
            blink_length = 0
            blinked_out = False
            timer_blink.stop()
            
def power_up_timeline():
    if quick_shot_on:
        my_ship.shoot()
    
    
# initialize frame
frame = simplegui.create_frame("Asteroids", width, height)

# initialize ship and two sprites
my_ship = Ship([width / 2, height / 2], [0, 0], 0, ship_image, ship_info)
#my_ship.powerUp = PowerUp("Homing", [0, 0], [0, 0], 10, 1000, "H", "yellow", "purple")


# register handlers
frame.set_draw_handler(draw)


timerPowerUp = simplegui.create_timer(1000, powerUpExpiration)
timer = simplegui.create_timer(1000.0, rock_spawner)
timer_blink = simplegui.create_timer(100.0, ship_blinking)
timer_power_ups = simplegui.create_timer(50.0, power_up_timeline)

frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(mouse_click)

# get things rolling

timerPowerUp.start()
frame.start()
