
# 007, 2 players, 3 actions, max 3 bullets
# actions: reload, shoot, shield

# shoot-shoot: 0 points, keep bullets
# reload-reload: 0 points, both get bullets
# shield-shield: 0 points
# shoot-shield: 0 points, shooter loses bullet
# shoot-reload: shooter 1 point, loses bullet, restart game
# reload-shield: 0 points, reloader gets bullet

import random
import numpy as np


def outcome(a, b, abullets=0, bbullets=0):
  if a == 'shoot' and abullets == 0:
    print('a doesnt have bullets')
    return 0, 1, abullets, bbullets, False # a point, b point, abullets, bbullets, restart
  elif b == 'shoot' and bbullets == 0:
    print('b doesnt have bullets')
    return 1, 0, abullets, bbullets, False 
  elif a == 'shoot' and b == 'reload':
    print('shoot and reload, a wins')
    return 1, 0, 0, 0, True 
  elif a == 'reload' and b == 'shoot':
    print('reload and shoot, b wins')
    return 0, 1, 0, 0, True
  elif a == 'shoot' and b == 'shoot':
    print('both shoot`')
    return 0, 0, abullets, bbullets, False
  elif a == 'shoot' and b == 'shield':
    print('shoot and shield')
    return 0, 0, abullets - 1, bbullets, False
  elif a == 'shield' and b == 'shoot':
    print('shield and shoot')
    return 0, 0, abullets, bbullets - 1, False
  elif a == 'reload' and b == 'reload':
    print('both reload')
    return 0, 0, abullets + 1, bbullets + 1, False
  elif a == 'reload' and b == 'shield':
    print('reload and shield')
    return 0, 0, abullets + 1, bbullets, False
  elif a == 'shield' and b == 'reload':
    print('shield and reload')
    return 0, 0, abullets, bbullets + 1, False
  elif a == 'shield' and b == 'shield':
    print('both shield')
    return 0, 0, abullets, bbullets, False


# print(outcome('shoot', 'reload', 1, 1))

actions = ['shoot', 'shield', 'reload']
keys = ['b', 's', 'r'] # b for bullet

# we define different bots and a human that can play each other

class RandomBot():
  def __init__(self):
    self.bullets = 0
    self.points = 0
  def move(self):
    if self.bullets > 0:
      return np.random.choice(actions, 1)[0]
    else:
      return np.random.choice(['shield', 'reload'], 1)[0]

class CleverBot():
  def __init__(self):
    self.bullets = 0
    self.points = 0
  def move(self, oppbullets):
    if self.bullets > 0 and oppbullets == 0:
      return np.random.choice(['shoot', 'reload'], 1)[0]
    elif self.bullets + oppbullets == 0:
      return 'reload'
    elif self.bullets < oppbullets:
      return np.random.choice(actions, 1, p=[.05, .75, .20])[0]
      # return 'shield'
    elif self.bullets == oppbullets and self.bullets > 0:
      return np.random.choice(actions, 1, p=[.05, .75, .20])[0]
      # return 'shield'
    elif self.bullets > oppbullets > 0:
      return 'shoot'

def cap(x, c=2):
  return np.minimum(x, c)

class LearnBot():
  def __init__(self):
    self.bullets = 0
    self.points = 0
    self.data = {}
  def update(self, prevmove, oppmove, oppbullets):
    # map (prevmove, oppbullets) -> oppmove
    key = (prevmove, cap(oppbullets))
    if key not in self.data:
      self.data[key] = {}
    if oppmove not in self.data[key]:
      self.data[key][oppmove] = 0
    self.data[key][oppmove] += 1
  def move(self, prevmove, oppbullets):
    # predict what opp will do, use the most frequent move
    key = (prevmove, cap(oppbullets))
    pred = ''
    best = 0
    if key in self.data:
      data = self.data[key]
      for act in data.keys():
        if data[act] > best:
          pred = act
          best = data[act]
      # print(data, pred)
    # find optimal action
    if pred == '' and self.bullets > 0:
      return np.random.choice(actions, 1)[0]
    elif pred == '':
      return np.random.choice(['shield', 'reload'], 1)[0]      
    elif pred == 'shield':
      return 'reload'
    elif pred == 'reload' and self.bullets > 0:
      return 'shoot'
    elif pred == 'reload':
      return 'reload'
    elif pred == 'shoot' and oppbullets > 0:
      return 'shield'
    elif pred == 'shoot':
      return 'reload'

class Human():
  def __init__(self):
    self.bullets = 0
    self.points = 0
  def move(self):
    print('please give me action: b, s, r')
    act = raw_input()
    if act == 'b':
      assert self.bullets > 0, 'you have no bullets'
      return 'shoot'
    elif act == 's':
      return 'shield'
    elif act == 'r':
      return 'reload'
    else:
      print('wrong action', act)


# create instances
rbot = RandomBot()
cbot = CleverBot()
cbot2 = CleverBot()
lbot = LearnBot()
felix = Human()
rounds = 0 
prevmove = ''

# play until you have 7 points
while cbot.points < 7 and lbot.points < 7:
  amove = lbot.move(prevmove, cbot.bullets)
  bmove = cbot.move(lbot.bullets)
  rounds += 1
  print('round', rounds)
  apoints, bpoints, abullets, bbullets, restart = outcome(amove, bmove, lbot.bullets, cbot.bullets)
  # update lbot data
  lbot.update(prevmove, bmove, cbot.bullets)
  prevmove = bmove
  # update points and bullets
  lbot.points = lbot.points + apoints
  cbot.points = cbot.points + bpoints
  lbot.bullets = abullets
  cbot.bullets = bbullets
  print('points', lbot.points, ':', cbot.points)
  print('bullets', lbot.bullets, ':', cbot.bullets)

