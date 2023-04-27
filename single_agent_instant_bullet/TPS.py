import pygame
import gym
import math
import numpy as np

from colisions import *
from Shooter import Shooter

RENDER_WIDTH = 600
RENDER_HEIGHT = 600
RADIUS = 20

ANGLE_INCREMENT = 0.1
ANGLE_SCALE = 360

BULLET_ACTION_DELAY = 200
AGENT_SPEED = 3




class TPS(gym.Env):
    def __init__(self):
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(3,))
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(7,))

        # render
        self.screen = pygame.display.set_mode((RENDER_HEIGHT, RENDER_WIDTH))

        # enemies and player
        self.enemies = []
        self.enemies.append(Shooter(RADIUS, (200, 50, 50), 0, 2, RENDER_WIDTH - 150, 50, 0))
        self.enemies.append(Shooter(RADIUS, (200, 50, 50), 0, 2, 150, 50, 0))
        self.agent = Shooter(RADIUS, (50, 50, 200), 0, 2, RENDER_WIDTH // 2, RENDER_HEIGHT - 50, AGENT_SPEED)


        self.agent.gun.x = self.agent.x + self.agent.radius * math.cos(self.agent.gun.angle)
        self.agent.gun.y = self.agent.y + self.agent.radius * math.sin(self.agent.gun.angle)
        for enemy in self.enemies:
            enemy.gun.x = enemy.x + enemy.radius * math.cos(enemy.gun.angle)
            enemy.gun.y = enemy.y + enemy.radius * math.sin(enemy.gun.angle)



        center_rect = pygame.Rect(RENDER_WIDTH // 2 - 100, RENDER_HEIGHT // 2 - 30, 100, 30)
        left_rect = pygame.Rect(RENDER_WIDTH // 4 - 100, RENDER_HEIGHT // 2 - 30, 100, 30)
        right_rect = pygame.Rect(RENDER_WIDTH * 3 // 4 - 100, RENDER_HEIGHT // 2 - 30, 100, 30)

        self.objects = [center_rect, left_rect, right_rect]




        # shoot delay
        self.shoot_delay = BULLET_ACTION_DELAY = 400


    def reset(self):
        # returning to initial positions
        self.enemies[0] = Shooter(RADIUS, (200, 50, 50), 0, 2, RENDER_WIDTH - 150, 50, 0)
        self.enemies[1] = Shooter(RADIUS, (200, 50, 50), 0, 2, 150, 50, 0)
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

        self.shoot_delay = BULLET_ACTION_DELAY
    
        return state

    def process(self, action):
        # action [0] = linear velocity player -> 1 = move forward, 0 = dont move
        # action [1] = angular velocity increment player -> 1 = increment, 0 = dont increment, -1 decrement
        # action [2] = player shoot -> 1 = shoot, 0 = do not shoot

        self.agent.move(self, np.abs(action[0] * AGENT_SPEED), RENDER_WIDTH, RENDER_HEIGHT)
        self.agent.gun.angle += action[1] * ANGLE_INCREMENT
        if action[2] > 0 and self.shoot_delay <= 0:
            self.agent.gun.shoot()
            self.shoot_delay = BULLET_ACTION_DELAY

        self.shoot_delay -= 1

    
    def verify_episode_end(self):
        alive = len(self.enemies)
        for enemy in self.enemies:
            if enemy is None:
                alive -= 1
        if alive == 0:
            return True
        return False

        
    def step(self, action):
        # actions 
        self.process(action)

        reward = -0.1

        idx = 0
        self.agent.updateGunPosition()

        for projectile in self.agent.gun.projectiles:
            # Calculate the trajectory of the projectile
            dx = math.cos(projectile.angle)
            dy = math.sin(projectile.angle)

            # verifying hit
            impact = False
            while not impact and 0 <= projectile.x < RENDER_WIDTH and 0 <= projectile.y < RENDER_HEIGHT:
                projectile.x += dx * 2
                projectile.y += dy * 2
                
                # colision with an obstacle
                for rect in self.objects:
                    if circle_rect_collision(projectile.x, projectile.y, projectile.radius, rect.left, rect.top, rect.width, rect.height):
                        impact = True
                        self.agent.gun.projectiles.remove(projectile)
                        break
                
                if not impact:
                    # Check for collision with an enemie
                    for enemy in self.enemies:
                        if enemy:
                            if circleCollision(projectile.x, projectile.y, projectile.radius, enemy.x, enemy.y, enemy.radius):
                                impact = True
                                self.agent.gun.projectiles.remove(projectile)
                                enemy.hp -= 1
                                reward += 20

                                if enemy.hp == 0:
                                    self.enemies[idx] = None
                                break
                self.render()
                            
            # Remove the projectile if it goes out of bounds
            if not impact:
                self.agent.gun.projectiles.remove(projectile)
                idx += 1


        next_state = []

        next_state.append(float(self.agent.x) / RENDER_WIDTH)
        next_state.append(float(self.agent.y) / RENDER_HEIGHT)
        next_state.append(float(self.agent.gun.angle) / ANGLE_SCALE)
        for enemy in self.enemies:
            if enemy:
                next_state.append(float(enemy.x) / RENDER_WIDTH)
                next_state.append(float(enemy.y) / RENDER_HEIGHT)
            else:
                next_state.append(-1)
                next_state.append(-1)

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
                pygame.draw.circle(self.screen, enemy.color, (enemy.x, enemy.y), enemy.radius)
        
            for i in self.objects:
                pygame.draw.rect(self.screen, (0, 0, 0), i)

            pygame.display.flip()

        else:
            return

    def close(self):
        pygame.quit()