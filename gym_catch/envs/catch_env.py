import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
import random
from gym.envs.classic_control import rendering
import time

STILL, LEFT, RIGHT = 0, 1, 2

class CatchEnv(gym.Env):
  metadata = {'render.modes': ['human'], 'video.frames_per_second': 1}

  def __init__(self):
    self.width = 5
    self.height = 5
    self.pad_width = 1
    self.action_space = spaces.Discrete(3) # Left, Right, Still
    self.observation_space = spaces.Box(low=0, high=1, shape=(self.height, self.width))

    self.viewer = None

    self._reset()
    self._configure()

  def _configure(self, display=None):
    self.display = display

  def _step(self, action):
    assert self.action_space.contains(action), "%r (%s) invalid"%(action, type(action))
    self.move_pad(action)
    self.move_ball()
    reward, done = self.reward()
    return np.copy(self.board), reward, done, {}

  def reward(self):
    x = self.ball[0]
    y = self.ball[1]
    if y == self.height - 1:
      if self.pad_loc <= x < self.pad_loc + self.pad_width:
        self.place_ball()
        return 1, False 
      else:
        return -1, True
    else:
        return 0, False # The ball is still in the air

  # Moves the pad in the direction
  def move_pad(self, action):
  	if action == STILL:
  		return
  	if action == LEFT:
  		self.pad_loc = max(0, self.pad_loc - 1)
  	if action == RIGHT:
  		self.pad_loc = min(self.pad_loc + 1, self.width - self.pad_width)
  	self.board[self.height-1] = 0
  	self.board[self.height-1][self.pad_loc:self.pad_loc + self.pad_width] = 1

  # Moves the ball down by one
  def move_ball(self):
  	x = self.ball[0]
  	y = self.ball[1]
  	self.board[y][x] = 0 
  	self.board[y+1][x] = 1
  	self.ball[1] += 1
  
  def _reset(self):
    self.board = np.zeros((self.height, self.width))
    self.board[self.height-1][:self.pad_width] = 1 # The pad
    self.pad_loc = 0
    self.place_ball()
    return np.copy(self.board)

  def place_ball(self):
    x = random.randint(0, self.width-1)
    self.board[0][x] = 1
    self.ball = [x,0]

  def _render(self, mode='human', close=False):
    if close:
        if self.viewer is not None:
          self.viewer.close()
          self.viewer = None
          return
    screen_width = 60
    screen_height = 60

    cube_width = screen_width / self.width
    cube_height = screen_height / self.height

    if self.viewer is None:
      self.viewer = rendering.Viewer(screen_width, screen_height, display=self.display)

    l,r = self.pad_loc * cube_width, (self.pad_loc + self.pad_width) * cube_width
    t,b = cube_height, 0


    x = self.ball[0]
    y = self.ball[1]
    bl,br = x * cube_width, (x + 1) * cube_width
    bt,bb = (self.height - y) * cube_height, (self.height - y - 1) * cube_height

    ball = rendering.FilledPolygon([(bl,bb), (bl,bt), (br,bt), (br,bb)])
    ball.set_color(0.5,0.2,0.9)
    self.viewer.add_onetime(ball)

    pad = rendering.FilledPolygon([(l,b), (l,t), (r,t), (r,b)])
    pad.set_color(.8,.6,.4)
    self.viewer.add_onetime(pad)

    time.sleep(0.4)

    return self.viewer.render()
