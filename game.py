import  pygame
import random
from enum import Enum
from collections import namedtuple
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
SPEED=15

class snakeGame:
    def __init__(self,width=1000,height=480):
        self.width=width
        self.height=height
        #Start Display
        self.display=pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption('Snake Game')
        self.clock=pygame.time.Clock()

        #Intial Game state
        self.dir=Direction.RIGHT
        self.head=point(self.width/2,self.height/2)
        self.snake=[self.head,point(self.head.x-block_size,self.head.y),
                    point(self.head.x-2*block_size,self.head.y)]
        self.score=0
        self.food=None
        self._place_food()
    
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


    def _move(self,dir):
        x=self.head.x
        y=self.head.y
        if dir==Direction.RIGHT:
            x+=block_size
        elif dir==Direction.LEFT:
            x-=block_size
        elif dir==Direction.UP:
            y-=block_size
        elif dir==Direction.DOWN:
            y+=block_size
        self.head=point(x,y)

    def _is_collision(self):
        if self.head.x>self.width-block_size or self.head.x<0 or self.head.y>self.height-block_size or self.head.y<0:
            return True
        if self.head in self.snake[1:]:
            return True
        return False

    def play_step(self):
        # print(self.snake)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_LEFT and self.dir!=Direction.RIGHT:
                    self.dir=Direction.LEFT
                elif event.key==pygame.K_RIGHT and self.dir!=Direction.LEFT:
                    self.dir=Direction.RIGHT
                elif event.key==pygame.K_UP and self.dir!=Direction.DOWN:
                    self.dir=Direction.UP
                elif event.key==pygame.K_DOWN and self.dir!=Direction.UP:
                    self.dir=Direction.DOWN
                
        
        self._move(self.dir)
        self.snake.insert(0,self.head)
        game_over=False
        if self._is_collision():
            game_over=True
            return game_over,self.score

        if self.head==self.food:
            self.score+=1
            self._place_food()

        else:
            self.snake.pop()        

        self._update_ui()
        self.clock.tick(SPEED)
        game_over=False
        return game_over,self.score


if __name__=='__main__':
    game=snakeGame()

    #Main Game Loop
    while  True:
        game_over,score=game.play_step()

        #Break the Loop if game is over
        
        if game_over:
            break
    
    print(f'Score:{score}')


    pygame.quit()
