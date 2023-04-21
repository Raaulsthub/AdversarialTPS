import pygame
import gym
import math
import numpy as np

from colisions import *
from Shooter import Shooter

RENDER_WIDTH = 800
RENDER_HEIGHT = 800
RADIUS = 20

ANGLE_INCREMENT = 5




class TPS(gym.Env):
    def __init__(self):
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(6,))
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(6,))

        # render
        self.screen = pygame.display.set_mode((800, 800))

        # initial state

        # players, initial positions
        self.players = []

        # team zero
        self.players.append(Shooter(RADIUS, (50, 50, 255), 0, 2, 150, RENDER_HEIGHT - 50, 50))
        # team one
        self.players.append(Shooter(RADIUS, (255, 50, 50), 1, 2, RENDER_WIDTH - 150, 50, 50))

        for i in range(2):
            self.players[i].gun.x = self.players[i].x + self.players[i].radius * math.cos(self.players[i].gun.angle)
            self.players[i].gun.y = self.players[i].y + self.players[i].radius * math.sin(self.players[i].gun.angle)


        # environment objects
        self.objects = []
        #self.objects.append(pygame.Rect(RENDER_WIDTH - 275, 100, 200, 50)) # upper right rect
        #self.objects.append(pygame.Rect(75, RENDER_HEIGHT - 130, 200, 50)) # lower left
        #self.objects.append(pygame.Rect(250, 375, 300, 50)) # central rect


    def reset(self):
        # team zero
        self.players[0] = Shooter(RADIUS, (50, 50, 255), 0, 2, 50, RENDER_HEIGHT - 50, 0.2)
        # team one
        self.players[1] = Shooter(RADIUS, (255, 50, 50), 1, 2, RENDER_WIDTH - 50, 50, 0.2)

        for i in range(2):
            self.players[i].gun.x = self.players[i].x + self.players[i].radius * math.cos(self.players[i].gun.angle)
            self.players[i].gun.y = self.players[i].y + self.players[i].radius * math.sin(self.players[i].gun.angle)


        for i in range(2):
            self.players[i].gun.x = self.players[i].x + self.players[i].radius * math.cos(self.players[i].gun.angle)
            self.players[i].gun.y = self.players[i].y + self.players[i].radius * math.sin(self.players[i].gun.angle)

        state = []
        for player in self.players:
            if player:
                state.append(float(player.x) / RENDER_WIDTH)
                state.append(float(player.y) / RENDER_HEIGHT)
                state.append(float(player.gun.angle) / 360)
            else:
                state.append(-1)
                state.append(-1)
                state.append(-1)
    
        return state

    def process(self, action):
        # action [0] = linear velocity player [0] -> 1 = move forward, 0 = dont move
        # action [1] = angular velocity increment player [0] -> 1 = increment, 0 = dont increment, -1 decrement
        # action [2] = player [0] shoot -> 1 = shoot, 0 = do not shoot
        # action [3] = linear velocity player [1] -> 1 = move forward, 0 = dont move
        # action [4] = angular velocity increment player [1] -> 1 = increment, 0 = dont increment, -1 decrement
        # action [5] = player [1] shoot -> 1 = shoot, 0 = do not shoot
        # action [6] = linear velocity player [2] -> 1 = move forward, 0 = dont move
        # action [7] = angular velocity increment player [2] -> 1 = increment, 0 = dont increment, -1 decrement
        # action [8] = player [2] shoot -> 1 = shoot, 0 = do not shoot
        # action [9] = linear velocity player [3] -> 1 = move forward, 0 = dont move
        # action [10] = angular velocity increment player [3] -> 1 = increment, 0 = dont increment, -1 decrement
        # action [11] = player [3] shoot -> 1 = shoot, 0 = do not shoot
        # action [12] = linear velocity player [4] -> 1 = move forward, 0 = dont move
        # action [13] = angular velocity increment player [4] -> 1 = increment, 0 = dont increment, -1 decrement
        # action [14] = player [4] shoot -> 1 = shoot, 0 = do not shoot
        # action [15] = linear velocity player [5] -> 1 = move forward, 0 = dont move
        # action [16] = angular velocity increment player [5] -> 1 = increment, 0 = dont increment, -1 decrement
        # action [17] = player [5] shoot -> 1 = shoot, 0 = do not shoot

        action_idx = 0
        for player in self.players:
            if player:
                #if (action[action_idx] < 0):
                    #player.move(self, action[action_idx] * 0.2)
                #else:
                    #player.move(self, np.abs(action[action_idx]))
                player.move(self, np.abs(action[action_idx]))
                # angle velocity
                player.gun.angle += action[action_idx + 1] * 0.2
                # shoot
                if action[action_idx + 1] > 0:
                    player.gun.shoot()
                else:
                    pass
                action_idx += 3

    
    def verify_episode_end(self):
        team0 = 0
        team1 = 0
        for player in self.players:
            if player is None:
                return True
    
        return False

        
    def step(self, action):
        # actions 
        self.process(action)   

        reward = 0
        
        idx = 0
        for player in self.players:
            if player:
                player.updateGunPosition()
                for projectile in player.gun.projectiles:
                    projectile.x += player.gun.bullet_speed * math.cos(projectile.angle)
                    projectile.y += player.gun.bullet_speed * math.sin(projectile.angle)
                    if projectile.x < 0 or projectile.x > RENDER_WIDTH or projectile.y < 0 or projectile.y > RENDER_HEIGHT:
                        player.gun.projectiles.remove(projectile)
                    for rect in self.objects:
                        if rectCircleCollision(rect.left, rect.top, rect.width, rect.height, projectile.x, projectile.y, projectile.radius):
                            player.gun.projectiles.remove(projectile)
                    for enemy in self.players:
                        if enemy:
                            if enemy != player:
                                if circleCollision(projectile.x, projectile.y, projectile.radius, enemy.x, enemy.y, enemy.radius):
                                    player.gun.projectiles.remove(projectile)
                                    enemy.hp -= 1
                                    reward += 5
                                    if enemy.hp == 0:
                                        self.players[idx] = None
            idx += 1

        next_state = []
        for player in self.players:
            if player:
                next_state.append(float(player.x) / RENDER_WIDTH)
                next_state.append(float(player.y) / RENDER_HEIGHT)
                next_state.append(float(player.gun.angle) / 360)
            else:
                next_state.append(-1)
                next_state.append(-1)
                next_state.append(-1)

        done = self.verify_episode_end()
        return next_state, reward, done, {}
    
    def render(self, mode='human'):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        
        self.screen.fill((255, 255, 255))

        for player in self.players:
            if (player):
                pygame.draw.circle(self.screen, player.color, (player.x, player.y), player.radius)
                pygame.draw.circle(self.screen, player.color, (player.gun.x, player.gun.y), player.gun.radius)
                for projectile in player.gun.projectiles:
                    pygame.draw.circle(self.screen, (0, 0, 0), (projectile.x, projectile.y), projectile.radius)

        for i in self.objects:
            pygame.draw.rect(self.screen, (0, 0, 0), i)

        pygame.display.flip()
        return True

    def close(self):
        pygame.quit()