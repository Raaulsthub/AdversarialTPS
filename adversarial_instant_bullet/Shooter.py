import math

from colisions import *
from Gun import Gun

class Shooter:
    def __init__(self, radius, color, team, hp, x, y, speed):
        self.radius = radius
        self.color = color
        self.team = team
        self.hp = hp
        self.x = x
        self.y = y
        self.gun = Gun(10, 120, 4, 0, 0)
        self.speed = speed
    
    def move(self, env, speed):
        normal_speed = self.speed
        self.speed *= speed
        okX = True
        okY = True
        for rect in env.objects:
            if(rectCircleCollision(rect.left, rect.top, rect.width, rect.height, self.x + self.speed * math.cos(self.gun.angle), self.y, self.radius)):
                okX = False
            if(rectCircleCollision(rect.left, rect.top, rect.width, rect.height, self.x, self.y + self.speed * math.sin(self.gun.angle), self.radius)):
                okY = False

        colisionsX = 0
        colisionsY = 0
        for other_player in env.players:
            if other_player:
                if circleCollision(self.x + self.speed, self.y, self.radius, other_player.x, other_player.y, other_player.radius):
                    colisionsX += 1
                if circleCollision(self.x, self.y + self.speed, self.radius, other_player.x, other_player.y, other_player.radius):
                    colisionsY += 1
                    
        # can colide only with himself
        if (colisionsX  > 1):
            okX = False
        if (colisionsY > 1):
            okY = False
        
        if okX and self.x + self.speed * math.cos(self.gun.angle) > self.radius and self.x + self.speed * math.cos(self.gun.angle) < 400 - self.radius:
            self.x += self.speed * math.cos(self.gun.angle)
        if okY and self.y + self.speed * math.sin(self.gun.angle) > self.radius and self.y + self.speed * math.sin(self.gun.angle) < 400 - self.radius:
            self.y += self.speed * math.sin(self.gun.angle)


        self.speed = normal_speed
    
    def updateGunPosition(self):
        self.gun.x = self.x + self.radius * math.cos(self.gun.angle)
        self.gun.y = self.y + self.radius * math.sin(self.gun.angle)