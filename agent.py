import torch
import random
import statistics
import numpy as np
from collections import deque
from game_ai import snakeGameAI,Direction,point,block_size
from model import Qnet,Qtrainer
from helper import plot
#_ doesn't make any difference,just for clear reading purpose
MAX_MEMORY=100_000
BATCH_SIZE=1000
LEARNING_RATE=0.001

class Agent:
    def __init__(self):
        self.num_games=0
        self.epsilon=0
        self.gamma=0.9
        self.memory=deque(maxlen=MAX_MEMORY)
        self.model=Qnet(11,256,3)
        self.trainer=Qtrainer(self.model,lr=LEARNING_RATE,gamma=self.gamma)

    def get_state(self,game):
        head = game.snake[0]
        point_l = point(head.x - block_size, head.y)
        point_r = point(head.x + block_size, head.y)
        point_u = point(head.x, head.y - block_size)
        point_d = point(head.x, head.y + block_size)
        
        dir_l = game.dir == Direction.LEFT
        dir_r = game.dir == Direction.RIGHT
        dir_u = game.dir == Direction.UP
        dir_d = game.dir == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]

        return np.array(state, dtype=int)

    def get_action(self,state):
        self.epsilon=75-self.num_games
        action=[0,0,0]

        if random.randint(0,200)<self.epsilon:
            move=random.randint(0,2)
            action[move]=1

        else:
            state=torch.tensor(state,dtype=torch.float)
            pred=self.model(state)
            move=torch.argmax(pred).item()
            action[move]=1
        return action

    def remember(self,state,action,reward,next_state,done):
        self.memory.append((state,action,reward,next_state,done))

    def train_long(self):
        if len(self.memory)>BATCH_SIZE:
            batch=random.sample(self.memory,BATCH_SIZE)
        else:
            batch=self.memory

        states,actions,rewards,next_states,done=zip(*batch)
        self.trainer.step(states,actions,rewards,next_states,done) 

    def train_short(self,state,action,reward,next_state,done):
        self.trainer.step(state,action,reward,next_state,done)

def train():
    scores=[]
    mean_scores=[]
    record_score=0
    agent=Agent()
    game=snakeGameAI()

    while True:
        curr_state=agent.get_state(game)

        action=agent.get_action(curr_state)

        reward,done,score=game.play_step(action)

        next_state=agent.get_state(game)

        agent.train_short(curr_state,action,reward,next_state,done)

        agent.remember(curr_state,action,reward,next_state,done)

        if done:
            game.reset()
            agent.num_games+=1
            agent.train_long()
            if(score>record_score):
                record_score=score
                agent.model.save()
            
            print(f"Game- {agent.num_games},Score: {score},Record: {record_score}")
            scores.append(score)
            min_len=min(len(scores),5)
            mean_score=statistics.mean(scores[-min_len:])
            mean_scores.append(mean_score)
            plot(scores,mean_scores)


if __name__=="__main__":
    train()