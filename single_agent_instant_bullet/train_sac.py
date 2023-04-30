import numpy as np
from sac.sac_torch import Agent
from utils import plot_learning_curve
from gym import wrappers
from env.TPS import TPS
from matplotlib import pyplot as plt
import time

if __name__ == '__main__':
    env = TPS()
    agent = Agent(input_dims=env.observation_space.shape,
                    env=env, n_actions=env.action_space.shape[0])

    n_games = 1500
    score_history = []
    load_checkpoint = False

    if load_checkpoint:
        agent.load_models()

    avg_scores = []
    best_score = -np.inf
    patience = 50
    early_stop = False
    
    for i in range(n_games):
        observation = env.reset()
        done = False
        score = 0
        steps = 0
        while done == False:
            action = agent.choose_action(observation)
            observation_, reward, done, info = env.step(action)
            score += reward
            agent.remember(observation, action, reward, observation_, done)
            agent.learn()
            observation = observation_
            env.render()
            steps += 1
        score_history.append(score)

        avg_score = np.mean(score_history[-100:])
        avg_scores.append(avg_score)

        print('episode ', i, 'score %.1f' % score, 'avg_score %.1f' % avg_score)
        if avg_score > best_score:
            best_score = avg_score
            agent.save_models()
            patience = 50  # reset patience
        elif i > 100:
            patience -= 1  # reduce patience
            if patience == 0:
                early_stop = True
                print("Training stopped early")
                break

        if early_stop:
            break
    
        plt.plot(np.arange(len(avg_scores)), avg_scores)
        plt.savefig('./plots/saclearning_curve.png')


