import random
from rl_framework.q_learning import QLearning
from rl_framework.environment import Environment
from rl_framework.trainer import Trainer
from rl_framework.constant_actions import get_all_actions

all_actions = get_all_actions()

# Initialize Q-learning agent with actions
q_learning_agent = QLearning(all_actions)

# Create the environment
environment = Environment(q_learning_agent)

# Initialize Trainer with the agent and environment
trainer = Trainer(q_learning_agent, environment,
                  num_episodes=100000, steps_per_episode=10)

# Load previous Q-table if available
print("\nLoading existing Q-table (if available)...")
trainer.q_learning.load_q_table()

# Train the RL agent
print("\nStarting training process...\n")
trainer.train()

# Evaluate the trained model
print("\nEvaluating trained model...\n")
trainer.evaluate(num_trials=10)

# Save the trained Q-table
print("\nSaving trained Q-table...\n")
trainer.q_learning.save_q_table()

print("\n Training and evaluation complete! Ready for deployment! \n")
   