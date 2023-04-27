import pygame
import gym
import math
import numpy as np

from colisions import *
from Shooter import Shooter

RENDER_WIDTH = 400
RENDER_HEIGHT = 400
RADIUS = 20

ANGLE_INCREMENT = 5

BULLET_ACTION_DELAY = 200



class TPS(gym.Env):
    def __init__(self):
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(6,))
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(6,))

        # render
        self.screen = pygame.display.set_mode((RENDER_HEIGHT, RENDER_WIDTH))

        # initial state

        # players, initial positions
        self.players = []

        # team zero
        self.players.append(Shooter(RADIUS, (50, 50, 255), 0, 2, 150, RENDER_HEIGHT - 50, 120))
        # team one
        self.players.append(Shooter(RADIUS, (255, 50, 50), 1, 2, RENDER_WIDTH - 150, 50, 120))

        for i in range(2):
            self.players[i].gun.x = self.players[i].x + self.players[i].radius * math.cos(self.players[i].gun.angle)
            self.players[i].gun.y = self.players[i].y + self.players[i].radius * math.sin(self.players[i].gun.angle)


        # environment objects
        self.objects = []
        #self.objects.append(pygame.Rect(RENDER_WIDTH - 275, 100, 200, 50)) # upper right rect
        #self.objects.append(pygame.Rect(75, RENDER_HEIGHT - 130, 200, 50)) # lower left
        #self.objects.append(pygame.Rect(150, 175, 100, 50)) # central rect


        # shoot delay
        self.delay0 = BULLET_ACTION_DELAY = 400
        self.delay1 = BULLET_ACTION_DELAY = 400


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

        self.delay0 = BULLET_ACTION_DELAY
        self.delay1 = BULLET_ACTION_DELAY 
    
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
                player.move(self, np.abs(action[action_idx]))
                # angle velocity
                player.gun.angle += action[action_idx + 1] * 0.2
                # shoot
                if action[action_idx + 2] > 0:
                    if (player.team == 0 and self.delay0 <= 0):
                        player.gun.shoot()
                        self.delay0 = BULLET_ACTION_DELAY
                    elif (player.team == 1 and self.delay1 <= 0):
                        player.gun.shoot()
                        self.delay1 = BULLET_ACTION_DELAY
                
                # shoot delay
                self.delay0 -= 1
                self.delay1 -= 1
                action_idx += 3

    
    def verify_episode_end(self):
        for player in self.players:
            if player is None:
                return True
        return False

        
    def step(self, action):
        # actions 
        self.process(action)   

        reward = -0.1
        reward_ = -0.1

        idx = 0
        for player in self.players:
            if player:
                player.updateGunPosition()
                # verify aim
                impact = False
                aim = False
                px = player.gun.x
                py = player.gun.y
                dx = math.cos(player.gun.angle)
                dy = math.sin(player.gun.angle)

                while not impact and 0 <= px < RENDER_WIDTH and 0 <= py < RENDER_HEIGHT:
                    for enemy in self.players:
                        if enemy and enemy != player:
                            if circleCollision(px, py, player.gun.radius / 2, enemy.x, enemy.y, enemy.radius):
                                if player.team == 0:
                                    reward += 5
                                elif player.team == 1:
                                    reward_ += 5
                                impact = True

                    if ~impact:
                        for rect in self.objects:
                            if rectCircleCollision(rect.left, rect.top, rect.width, rect.height, px, py, player.gun.radius / 2):
                                impact = True
                                break

                    px += dx * 5
                    py += dy * 5

                         
                for projectile in player.gun.projectiles:
                    # Calculate the trajectory of the projectile
                    dx = math.cos(projectile.angle)
                    dy = math.sin(projectile.angle)

                    # verifying hit
                    impact = False
                    while not impact and 0 <= projectile.x < RENDER_WIDTH and 0 <= projectile.y < RENDER_HEIGHT:
                        projectile.x += dx * 10
                        projectile.y += dy * 10
                        
                        # colision with an obstacle
                        for rect in self.objects:
                            if rectCircleCollision(rect.left, rect.top, rect.width, rect.height, projectile.x, projectile.y, projectile.radius):
                                impact = True
                                player.gun.projectiles.remove(projectile)
                                break
                        
                        if not impact:
                            # Check for collision with a player
                            for enemy in self.players:
                                if enemy and enemy != player:
                                    if circleCollision(projectile.x, projectile.y, projectile.radius, enemy.x, enemy.y, enemy.radius):
                                        impact = True
                                        player.gun.projectiles.remove(projectile)
                                        enemy.hp -= 1
                                        if player.team == 0:
                                            reward += 20
                                            reward_ -= 2
                                        elif player.team == 1:
                                            reward_ += 20
                                            reward -= 2
                                        if enemy.hp == 0:
                                            self.players[idx] = None
                                        break
                        self.render()
                                    
                    # Remove the projectile if it goes out of bounds
                    if not impact:
                        player.gun.projectiles.remove(projectile)
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
        return next_state, reward, reward_, done, {}
    
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