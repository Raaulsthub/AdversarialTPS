import time

from env_.Projectile import Projectile

class Gun:
    def __init__(self, radius, angle, bullet_speed, x, y):
        self.radius = radius
        self.angle = angle
        self.bullet_speed = bullet_speed
        self.projectiles = []
        self.x = x
        self.y = y 
        self.time_since_last_shot = 0

    def shoot(self, x, y):
        self.projectiles.append(Projectile(self.radius, self.angle, x, y))
        self.time_since_last_shot = time.time()