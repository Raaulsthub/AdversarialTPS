import math

from env_.colisions import *
from env_.Gun import Gun

class Shooter:
    def __init__(self, radius, color, team, hp, x, y, speed):
        self.radius = radius
        self.color = color
        self.team = team
        self.hp = hp
        self.x = x
        self.y = y
        self.gun = Gun(10, 180, 4, 0, 0)
        self.speed = speed
    
    def move(self, env, speed, width, height):
        self.speed = speed
        new_x = self.x + speed * math.cos(self.gun.angle)
        new_y = self.y + speed * math.sin(self.gun.angle)

        for object in env.objects:
            if circle_rect_collision(new_x, self.y, self.radius, object.left, object.top, object.width, object.height):
                new_x = self.x
            if circle_rect_collision(self.x, new_y, self.radius, object.left, object.top, object.width, object.height):
                new_y = self.y
        
        for enemy in env.enemies:
            if enemy:
                if circleCollision(new_x, self.y, self.radius, enemy.x, enemy.y, enemy.radius):
                    new_x = self.x
                if circleCollision(self.x, new_y, self.radius, enemy.x, enemy.y, enemy.radius):
                    new_y = self.y
        
        if (0 <= new_x - self.radius and width >= new_x + self.radius) == False:
            new_x = self.x
        if (0 <= new_y - self.radius and height >= new_y + self.radius) == False:
            new_y = self.y
        
        self.x = new_x
        self.y = new_y



    
    def updateGunPosition(self):
        self.gun.x = self.x + self.radius * math.cos(self.gun.angle)
        self.gun.y = self.y + self.radius * math.sin(self.gun.angle)