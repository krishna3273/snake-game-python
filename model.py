import torch
import torch.nn as nn
import os

class Qnet(nn.Module):
    def __init__(self,input_size,hidden_size,num_classes):
        super(Qnet, self).__init__()
        self.l1=nn.Linear(input_size,hidden_size)
        self.l2=nn.Linear(hidden_size,num_classes)
        self.relu=nn.ReLU()

    def forward(self,x):
        out=self.relu(self.l1(x))
        return self.l2(out)

    def save(self,file_name="model.pth"):
        model_folder_path='./model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name=os.path.join(model_folder_path,file_name)
        torch.save(self.state_dict(),file_name)


class Qtrainer:
    def __init__(self,model,lr,gamma):
        self.lr=lr
        self.gamma=gamma
        self.model=model
        self.optimiser=torch.optim.Adam(model.parameters(),lr=self.lr)
        self.loss_criterion=nn.MSELoss()

    def step(self,state,action,reward,next_state,done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        # 1: predicted Q values with current state
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new
    
        
        self.optimiser.zero_grad()
        loss = self.loss_criterion(target, pred)
        loss.backward()

        self.optimiser.step()
