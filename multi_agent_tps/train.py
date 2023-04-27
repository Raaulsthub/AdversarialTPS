from MultiAgentFPS import MultiAgentFPS   
import numpy as np   

def main():
    env = MultiAgentFPS()
    while True:
        action = np.zeros(18, dtype=int)
        for i in range(18):
            action[i] = np.random.choice([-1, 0, 1])
        state, reward, done, _ = env.step(action)
        env.render()
        if done:
            env.reset()
    env.close()


if __name__ == '__main__':
    main()