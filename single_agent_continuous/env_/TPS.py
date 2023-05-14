import pygame
import gym
import math
import numpy as np

from env_.colisions import *
from env_.Shooter import Shooter

RENDER_WIDTH = 300
RENDER_HEIGHT = 300
RADIUS = 20

ANGLE_INCREMENT = 0.2
ANGLE_SCALE = 360

BULLET_ACTION_DELAY = 40
AGENT_SPEED = 5

MAX_STEP = 80




class TPS(gym.Env):
    def __init__(self, render_mode='human'):
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(2,))
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(24,))
        self.render_mode = render_mode

        if render_mode == 'human':
            self.screen = pygame.display.set_mode((RENDER_HEIGHT, RENDER_WIDTH))

        # enemies and player
        self.enemies = []
        self.enemies.append(Shooter(RADIUS, (200, 50, 50), 0, 1, RENDER_WIDTH -  RADIUS//2, RENDER_HEIGHT // 3 - RADIUS//2, 0))
        #self.enemies.append(Shooter(RADIUS, (200, 50, 50), 0, 1, 50, 50, 0))
        self.agent = Shooter(RADIUS, (50, 50, 200), 0, 1, RENDER_WIDTH // 2 - RADIUS//2, RENDER_HEIGHT // 2 - RADIUS//2, AGENT_SPEED)


        self.agent.gun.x = self.agent.x + self.agent.radius * math.cos(self.agent.gun.angle)
        self.agent.gun.y = self.agent.y + self.agent.radius * math.sin(self.agent.gun.angle)
        for enemy in self.enemies:
            enemy.gun.x = enemy.x + enemy.radius * math.cos(enemy.gun.angle)
            enemy.gun.y = enemy.y + enemy.radius * math.sin(enemy.gun.angle)



        center_rect = pygame.Rect(RENDER_WIDTH // 2 - 100, RENDER_HEIGHT // 2 - 10, 200, 20)
        self.objects = [center_rect]


        self.nsteps = 0

        # shoot delay
        self.shoot_delay = BULLET_ACTION_DELAY


    def reset(self):
        # returning to initial positions
        self.enemies[0] = Shooter(RADIUS, (200, 50, 50), 0, 2,
                                  RENDER_WIDTH - np.random.randint(0, RENDER_WIDTH - RADIUS//2),
                                  np.random.randint(0, RENDER_HEIGHT//3 - RADIUS//2), 0)
        #self.enemies[1] = Shooter(RADIUS, (200, 50, 50), 0, 2,
        #                         np.random.randint(0, RENDER_WIDTH - RADIUS),
        #                         np.random.randint(0, RENDER_HEIGHT/2), 0)
        self.agent = Shooter(RADIUS, (50, 50, 200), 0, 2, RENDER_WIDTH // 2, RENDER_HEIGHT - 50, AGENT_SPEED)

        self.agent.gun.x = self.agent.x + self.agent.radius * math.cos(self.agent.gun.angle)
        self.agent.gun.y = self.agent.y + self.agent.radius * math.sin(self.agent.gun.angle)
        for enemy in self.enemies:
            enemy.gun.x = enemy.x + enemy.radius * math.cos(enemy.gun.angle)
            enemy.gun.y = enemy.y + enemy.radius * math.sin(enemy.gun.angle)

        # state
        state = []
        state.append(float(self.agent.x) / RENDER_WIDTH)
        state.append(float(self.agent.y) / RENDER_HEIGHT)
        state.append(float(self.agent.gun.angle) / ANGLE_SCALE)
        for enemy in self.enemies:
            state.append(float(enemy.x) / RENDER_WIDTH)
            state.append(float(enemy.y) / RENDER_HEIGHT)
            state.append(math.sqrt((self.agent.x - enemy.x) ** 2 + (self.agent.y - enemy.y) ** 2))


        for i in range(18):
            state.append(0)

        self.shoot_delay = BULLET_ACTION_DELAY
    
        return state

    def process(self, action, reward):
        # action [0] = linear velocity player -> 1 = move forward, 0 = dont move
        # action [1] = angular velocity increment player -> 1 = increment, 0 = dont increment, -1 decrement
        # action [2] = player shoot -> 1 = shoot, 0 = do not shoot

        self.agent.move(self, AGENT_SPEED, RENDER_WIDTH, RENDER_HEIGHT)
        self.agent.gun.angle += action[0] * ANGLE_INCREMENT
        if action[1] > 0 and self.shoot_delay <= 0:
            reward += 1
            self.agent.gun.shoot(self.agent.x, self.agent.y)
            self.shoot_delay = BULLET_ACTION_DELAY

        self.shoot_delay -= 1
        return reward
    
    def sensors(self, angle):
        aimEnemy = False
        aimObject = True
        impact = False

        px = self.agent.gun.x
        py = self.agent.gun.y
        dx = math.cos(angle)
        dy = math.sin(angle)

        while not impact and 0 <= px < RENDER_WIDTH and 0 <= py < RENDER_HEIGHT:
            for enemy in self.enemies:
                if enemy:
                    if circleCollision(px, py, self.agent.gun.radius, enemy.x, enemy.y, enemy.radius):
                        aimEnemy = True
                        impact = True
        
            # colision with an obstacle
            for rect in self.objects:
                if circle_rect_collision(px, py, self.agent.gun.radius, rect.left, rect.top, rect.width, rect.height):
                    aimEnemy = False
                    aimObject = True
                    impact = True
                    break
            
            px += dx * 1
            py += dy * 1
        return aimEnemy, aimObject

    
    def verify_episode_end(self):
        if (self.nsteps == MAX_STEP):
            self.nsteps = 0
            print("Finished by step limit")
            return True
        self.nsteps += 1
        alive = len(self.enemies)
        for enemy in self.enemies:
            if enemy is None:
                alive -= 1
        if alive == 0:
            print("Shot at all red dots")
            return True
        return False

        
    def step(self, action):
        # actions 
        reward = 0
        reward = self.process(action, reward)


        max_dist = math.sqrt(RENDER_WIDTH ** 2 + RENDER_HEIGHT ** 2)
        '''for enemy in self.enemies:
            if enemy is not None:
                reward -= 0.1 * (math.sqrt((self.agent.x - enemy.x) ** 2 + (self.agent.y - enemy.y) ** 2)) / max_dist'''


       # check if player is pointing at the enemies direction
        self.agent.updateGunPosition()
        # verify aimEnemy
        
        aimEnemy = [False] * 9
        aimObject = [False] * 9

        aimEnemy[0], aimObject[0] = self.sensors(self.agent.gun.angle)
        aimEnemy[1], aimObject[1] = self.sensors(self.agent.gun.angle + 30)
        aimEnemy[2], aimObject[2] = self.sensors(self.agent.gun.angle - 30)
        aimEnemy[3], aimObject[3] = self.sensors(self.agent.gun.angle + 15)
        aimEnemy[4], aimObject[4] = self.sensors(self.agent.gun.angle - 15)
        aimEnemy[5], aimObject[5] = self.sensors(self.agent.gun.angle + 7.5)
        aimEnemy[6], aimObject[6] = self.sensors(self.agent.gun.angle - 7.5)
        aimEnemy[7], aimObject[7] = self.sensors(self.agent.gun.angle + 22.5)
        aimEnemy[8], aimObject[8] = self.sensors(self.agent.gun.angle - 22.5)
        
        for projectile in self.agent.gun.projectiles:
            # Calculate the trajectory of the projectile
            dx = math.cos(projectile.angle)
            dy = math.sin(projectile.angle)

            # verifying hit
            impact = False
            while not impact and 0 <= projectile.x < RENDER_WIDTH and 0 <= projectile.y < RENDER_HEIGHT:
                projectile.x += dx * 0.5
                projectile.y += dy * 0.5
                self.render()
                
                # colision with an obstacle
                for rect in self.objects:
                    if circle_rect_collision(projectile.x, projectile.y, projectile.radius, rect.left, rect.top, rect.width, rect.height):
                        impact = True
                        self.agent.gun.projectiles.remove(projectile)
                        break
                
                if not impact:
                    # Check for collision with an enemy
                    idx = 0
                    for enemy in self.enemies:
                        if enemy:
                            if circleCollision(projectile.x, projectile.y, projectile.radius, enemy.x, enemy.y, enemy.radius):
                                impact = True
                                print("Shot enemy")
                                self.agent.gun.projectiles.remove(projectile)
                                self.enemies[idx] = None
                                reward += 50
                                break
                        idx += 1
                            
            # Remove the projectile if it goes out of bounds
            if not impact:
                if projectile:
                    self.agent.gun.projectiles.remove(projectile)

        next_state = []

        next_state.append(float(self.agent.x) / RENDER_WIDTH)
        next_state.append(float(self.agent.y) / RENDER_HEIGHT)
        next_state.append(float(self.agent.gun.angle) / ANGLE_SCALE)
        for enemy in self.enemies:
            if enemy:
                next_state.append(float(enemy.x) / RENDER_WIDTH)
                next_state.append(float(enemy.y) / RENDER_HEIGHT)
                next_state.append(math.sqrt((self.agent.x - enemy.x) ** 2 + (self.agent.y - enemy.y) ** 2))
            else:
                next_state.append(-1)
                next_state.append(-1)
                next_state.append(-1)

        for i in range(len(aimEnemy)):
            if aimEnemy[i] == True:
                next_state.append(1)
                next_state.append(0)
            elif aimObject[i] == True:
                next_state.append(0)
                next_state.append(1)
            else:
                next_state.append(0)
                next_state.append(0)
            # print()
            # print(aimEnemy[i])
            # print(aimObject[i])

        done = self.verify_episode_end()
        return next_state, reward, done, {}
    
    def render(self, mode='human'):
        if mode == 'human':
            self.screen.fill((255, 255, 255))

            # agent
            pygame.draw.circle(self.screen, self.agent.color, (self.agent.x, self.agent.y), self.agent.radius)
            pygame.draw.circle(self.screen, self.agent.color, (self.agent.gun.x, self.agent.gun.y), self.agent.gun.radius)
            for projectile in self.agent.gun.projectiles:
                pygame.draw.circle(self.screen, (0, 0, 0), (projectile.x, projectile.y), projectile.radius)

            # enemies
            for enemy in self.enemies:
                if enemy:
                    pygame.draw.circle(self.screen, enemy.color, (enemy.x, enemy.y), enemy.radius)
        
            for i in self.objects:
                pygame.draw.rect(self.screen, (0, 0, 0), i)

            pygame.display.flip()

        else:
            return

    def close(self):
        pygame.quit()