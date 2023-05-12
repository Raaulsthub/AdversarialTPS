import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file into a DataFrame
df = pd.read_csv('./training_log/sac/no_object.csv')

# Create a figure and axis objects
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the episode and average reward
ax.plot(df['episode'], df['avg_reward'], label='Average Reward', alpha=0.05, linewidth=4)

# Calculate moving averages of the last 10 and 100 rewards
ma10 = df['avg_reward'].rolling(window=10, min_periods=1).mean()
ma100 = df['avg_reward'].rolling(window=100, min_periods=1).mean()

# Plot the moving averages
ax.plot(df['episode'], ma10, label='MA10', alpha=0.5, linewidth=1)
ax.plot(df['episode'], ma100, label='MA100', alpha=1, linewidth=1)

# Set axis labels and legend
ax.set_xlabel('Episode')
ax.set_ylabel('Average Reward')
ax.legend()

# Save the plot as a PDF file
plt.savefig('./training_plots/sac/no_object.pdf', format='pdf')