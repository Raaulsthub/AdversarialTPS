import time

from Projectile import Projectile

TIME_TO_SHOOT = 0.5

class Gun:
    def __init__(self, radius, angle, bullet_speed, x, y):
        self.radius = radius
        self.angle = angle
        self.bullet_speed = bullet_speed
        self.projectiles = []
        self.x = x
        self.y = y 
        self.time_since_last_shot = 0

    def shoot(self):
        if(abs(self.time_since_last_shot - time.time()) > TIME_TO_SHOOT):
            self.projectiles.append(Projectile(self.radius / 2, self.angle, self.x, self.y))
            self.time_since_last_shot = time.time()