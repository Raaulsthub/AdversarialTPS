from ddpg.ddpg import Agent
import gym
import numpy as np
from utils import plot_learning_curve
from env_.TPS import TPS
from matplotlib import pyplot as plt
import pandas as pd


if __name__ == '__main__':
    env = TPS()
    agent = Agent(alpha=0.000025, beta=0.00025, input_dims=env.observation_space.shape, tau=0.001, env=env,
              batch_size=64,  layer1_size=512, layer2_size=512, n_actions=3)

    n_games = 500
    score_history = []
    load_checkpoint = False

    best_score = -1000

    current_ep = 0

    if load_checkpoint:
        agent.load_models()

    avg_scores = []
    
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
            # time.sleep(0.05)
            steps += 1
        score_history.append(score)

        avg_score = np.mean(score_history[-10:])
        avg_scores.append(avg_score)


        print('episode ', i, 'score %.1f' % score, 'avg_score %.1f' % avg_score)
        if current_ep > 50 and np.mean(score_history[:10]) > best_score:
            best_score = np.mean(score_history[:10])
            agent.save_models()
        
        plt.plot(np.arange(len(avg_scores)), avg_scores)
        plt.savefig('./plots/ddpg_learning_curve.png')
        
        current_ep += 1

    data = {'episode': np.arange(len(score_history)), 'avg_reward': score_history}
    df = pd.DataFrame(data)
    df.to_csv('./training_log/ddpg/central_object.csv', index=False)
   
