import numpy as np
from sac.sac_torch import Agent
from utils import plot_learning_curve
from gym import wrappers
from env_.TPS import TPS
from matplotlib import pyplot as plt
import time
import pandas as pd

if __name__ == '__main__':
    env = TPS()
    agent = Agent(input_dims=env.observation_space.shape,
                    env=env, n_actions=env.action_space.shape[0])

    n_games = 100
    score_history = []

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
            observation = observation_
            env.render()
            steps += 1
            time.sleep(0.01)
        score_history.append(score)

        avg_score = np.mean(score_history[-20:])
        avg_scores.append(avg_score)

        print('episode ', i, 'score %.1f' % score, 'avg_score %.1f' % avg_score)

        plt.plot(np.arange(len(score_history)), score_history)
        plt.savefig('./plots/sac_test.png')

    data = {'episode': np.arange(len(score_history)), 'avg_reward': score_history}
    df = pd.DataFrame(data)
    df.to_csv('./testing_log/sac/no_object.csv', index=False)



