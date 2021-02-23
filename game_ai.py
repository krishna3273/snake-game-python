import  pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
pygame.init()

font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    RIGHT=1
    LEFT=2
    UP=3
    DOWN=4

point=namedtuple('point','x,y')

WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE = (0, 0, 255)
BLUE_BRIGHT = (0, 100, 255)
BLACK = (0,0,0)

block_size=20
SPEED=40

class snakeGameAI:
    def __init__(self,width=1000,height=480):
        self.width=width
        self.height=height
        #Start Display
        self.display=pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption('Snake Game')
        self.clock=pygame.time.Clock()
        self.reset()
        
    
    def reset(self):
        #Intial Game state
        self.dir=Direction.RIGHT
        self.head=point(self.width/2,self.height/2)
        self.snake=[self.head,point(self.head.x-block_size,self.head.y),
                    point(self.head.x-2*block_size,self.head.y)]
        self.score=0
        self.food=None
        self._place_food()
        self.frame_iteration=0

    def _place_food(self):
        x=random.randint(0,(self.width-block_size)//block_size)*block_size
        y=random.randint(0,(self.height-block_size)//block_size)*block_size
        print(x,y)
        self.food=point(x,y)
        if self.food in self.snake:
            self._place_food()
        return
    
    def _update_ui(self):
        self.display.fill(BLACK)

        for point in self.snake:
            pygame.draw.rect(self.display,BLUE,pygame.Rect(point.x,point.y,block_size,block_size))
            pygame.draw.rect(self.display,BLUE_BRIGHT,pygame.Rect(point.x+4,point.y+4,12,12))

        pygame.draw.rect(self.display,RED,pygame.Rect(self.food.x,self.food.y,block_size,block_size))
        # pygame.draw.circle(self.display, RED, (self.food.x,self.food.y), block_size/2,0)
        text=font.render("Score: "+str(self.score),True,WHITE)

        self.display.blit(text,[0,0])
        pygame.display.flip()


    def _move(self,action):
        #action->straight-[1,0,0],right-[0,1,0],left-[0,0,1]
        directions_list_cw=[Direction.RIGHT,Direction.DOWN,Direction.LEFT,Direction.UP]
        curr_direction_index=directions_list_cw.index(self.dir)

        new_dir=self.dir
        
        if np.array_equal(action,[1,0,0]):
            new_dir=directions_list_cw[(curr_direction_index+1)%4]

        elif np.array_equal(action,[0,0,1]):
            new_dir=directions_list_cw[(curr_direction_index+3)%4]

        self.dir=new_dir

        x=self.head.x
        y=self.head.y
        if self.dir==Direction.RIGHT:
            x+=block_size
        elif self.dir==Direction.LEFT:
            x-=block_size
        elif self.dir==Direction.UP:
            y-=block_size
        elif self.dir==Direction.DOWN:
            y+=block_size
        self.head=point(x,y)

    def is_collision(self,pt=None):
        if pt is None:
            pt=self.head
        if pt.x>self.width-block_size or pt.x<0 or pt.y>self.height-block_size or pt.y<0:
            return True
        if pt in self.snake[1:]:
            return True
        return False

    def play_step(self,action):
        # print(self.snake)
        self.frame_iteration+=1
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
        self._move(action)
        self.snake.insert(0,self.head)

        reward=0
        game_over=False
        if self.is_collision() or self.frame_iteration>100*len(self.snake):
            game_over=True
            reward=-10
            return reward,game_over,self.score

        if self.head==self.food:
            self.score+=1
            reward=10
            self._place_food()

        else:
            self.snake.pop()        

        self._update_ui()
        self.clock.tick(SPEED)
        game_over=False
        return reward,game_over,self.score
