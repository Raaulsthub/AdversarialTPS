import numpy as np
from sac_torch import Agent
from utils import plot_learning_curve
from gym import wrappers
from TPS import TPS
from matplotlib import pyplot as plt

if __name__ == '__main__':
    env = TPS()
    agent = Agent(input_dims=env.observation_space.shape,
                    env=env, n_actions=env.action_space.shape[0] // 2)
    agent_ = Agent(input_dims=env.observation_space.shape,
                    env=env, n_actions=env.action_space.shape[0] // 2)

    n_games = 2000
    filename = 'vss.png'
    figure_file = 'plots/' + filename

    score_history = []
    score_history_ =[]
    load_checkpoint = True

    if load_checkpoint:
        agent.load_models()

    avg_scores = []
    avg_scores_ = []

    
    for i in range(n_games):
        observation = env.reset()
        done = False
        score = 0
        score_ = 0
        steps = 0
        while done == False and steps < 5000:
            action = agent.choose_action(observation)
            action_ = agent_.choose_action(observation)
            action_final = np.concatenate([action, action_])
            observation_, reward, reward_, done, info = env.step(action_final)
            score += reward
            score_ += reward_
            agent.remember(observation, action, reward, observation_, done)
            agent_.remember(observation, action_, reward_, observation_, done)
            agent.learn()
            agent_.learn()
            observation = observation_
            env.render()
            steps += 1
        score_history.append(score)
        score_history_.append(score_)

        avg_score = np.mean(score_history[-100:])
        avg_score_ = np.mean(score_history_[-100:])
        avg_scores.append(avg_score)
        avg_scores_.append(avg_score_)


        print('episode ', i, 'score %.1f' % score, 'avg_score %.1f' % avg_score)
        print('episode ', i, 'score %.1f' % score_, 'avg_score %.1f' % avg_score_)
        agent.save_models()
        agent_.save_models()
        
        plt.plot(np.arange(len(avg_scores)), avg_scores)
        plt.plot(np.arange(len(avg_scores_)), avg_scores_)
        plt.savefig('./plots/leaning_curve.png')
        #x = [i+1 for i in range(steps)]
        #plot_learning_curve(x, score_history, figure_file)
        

