import pygame
import enum
import os
import random
from typing import Tuple

class pieceShape(enum.Enum):
  LONG = 'long.png'
  T = 't.png'
  SQUARE = 'square.png'
  Z_LEFT = 'left_z.png'
  Z_RIGHT = 'right_z.png'
  L_LEFT = 'left_l.png'
  L_RIGHT = 'right_l.png'

  @classmethod
  def getSize(cls, shape) -> Tuple[int, int]:
    sizes = {
      cls.LONG: (120, 30),
      cls.T: (90, 60),
      cls.SQUARE: (60, 60),
      cls.Z_LEFT: (90, 60),
      cls.Z_RIGHT: (90, 60),
      cls.L_LEFT: (90, 60),
      cls.L_RIGHT: (90, 60)
    }
    return sizes[shape]

  @classmethod
  def getStopOffsets(cls, shape, rotation: int, isBottom: bool) -> int:
    offsetsRight = {
      cls.LONG: (4, 1, 4, 1),
      cls.T: (3, 2, 3, 2),
      cls.SQUARE: (2, 2, 2, 2),
      cls.Z_LEFT: (3, 2, 3, 2),
      cls.Z_RIGHT: (3, 2, 3, 2),
      cls.L_LEFT: (3, 2, 3, 2),
      cls.L_RIGHT: (3, 2, 3, 2)
    }
    offsetsBottom = {
      cls.LONG: (1, 4, 1, 4),
      cls.T: (2, 3, 2, 3),
      cls.SQUARE: (2, 2, 2, 2),
      cls.Z_LEFT: (2, 3, 2, 3),
      cls.Z_RIGHT: (2, 3, 2, 3),
      cls.L_LEFT: (2, 3, 2, 3),
      cls.L_RIGHT: (2, 3, 2, 3)
    }
    return (offsetsRight if not isBottom else offsetsBottom)[shape][rotation] * interval

class pieceDirection(enum.Enum):
  LEFT = 0
  RIGHT = 1
  DOWN = 2
  UP = 3

class AwaitingPiece(pygame.sprite.Sprite):
  def __init__(self, shape: pieceShape) -> None:
    pygame.sprite.Sprite.__init__(self)
    self.shape = shape
    
    self.image = pygame.transform.scale(
      pygame.image.load(os.path.join(self.shape.value)),
      pieceShape.getSize(self.shape)
    )

    self.rect = self.image.get_rect()
    (self.rect[0], self.rect[1]) = (400, 400)

  def getShape(self) -> pieceShape:
    return self.shape

class Piece(pygame.sprite.Sprite):
  def __init__(self, shape: pieceShape) -> None:
    pygame.sprite.Sprite.__init__(self)
    self.shape = shape

    self.image = pygame.transform.scale(
      pygame.image.load(os.path.join(self.shape.value)),
      [i-0 for i in pieceShape.getSize(self.shape)]
    )
    self.mask = pygame.mask.from_surface(self.image) # collision mask
    self.mask = self.mask.scale((self.image.get_width() + 15, self.image.get_height() + 15))
    self.rotationState = 0
    self.rightStopOffset = pieceShape.getStopOffsets(self.shape, self.rotationState, False)
    self.bottomStopOffset = pieceShape.getStopOffsets(self.shape, self.rotationState, True)
    
    # rect is the actual position of the piece
    self.rect = self.image.get_rect()
    (self.rect[0], self.rect[1]) = gridPos[0]
  
  def touchingBottom(self) -> bool:
    return self.rect[1] >= gridPos[1][1] - self.bottomStopOffset
  
  def rotate(self) -> None:
    rotation = 90
    # TODO: shapes can clip through the right wall if rotated incorrectly
    if self.shape == pieceShape.SQUARE:
      return # Squares cause funky things to occur, so they are skipped
    elif self.shape == pieceShape.Z_LEFT:
      if self.rotationState == 0:
        # These values need to be tweaked as there is a weird behavior when in the 1st position when trying to place
        rotation = 270 # wrap around back to state 0
        self.rotationState = 2 # set to state 2 (incremented to 3 later)
    self.image = pygame.transform.rotate(self.image, rotation) # Rotate image 90 degrees
    self.mask = pygame.mask.from_surface(self.image) # apply collision mask to sprite
    self.rotationState += 1 if self.rotationState != 3 else -3 # increment rotation state (or reset if overflow)
    self.rightStopOffset = pieceShape.getStopOffsets(self.shape, self.rotationState, False)
    self.bottomStopOffset = pieceShape.getStopOffsets(self.shape, self.rotationState, True)

  def move(self, direction: pieceDirection) -> None:
    if direction == pieceDirection.LEFT:
      if self.rect[0] > gridPos[0][0]: # make sure to not go beyond a "wall"
        self.rect[0] -= interval
    elif direction == pieceDirection.RIGHT:
      if self.rect[0] < gridPos[1][0] - self.rightStopOffset: # rightStopOffset is to prevent pieces from going out of bounds
        self.rect[0] += interval
    elif direction == pieceDirection.DOWN:
      self.rect[1] += interval
    elif direction == pieceDirection.UP: # should only be called if it has clipped into another sprite
      self.rect[1] -= interval

def drawGrid() -> None:
  # grid lines for debug purposes
  if gridLinesEnabled:
    for i in range(1, 21):
      pygame.draw.line(screen, (0, 0, 0), (gridPos[0][0], i*30), (gridPos[1][0], i*30)) # hor
    for i in range(1, 11):
      pygame.draw.line(screen, (0, 0, 0), (i*30, gridPos[0][1]), (i*30, gridPos[1][1])) # ver
  else:
    pygame.draw.line(screen, (0, 0, 0), (gridPos[0][0], gridPos[0][1]), (gridPos[1][0], gridPos[0][1]))
    pygame.draw.line(screen, (0, 0, 0), (gridPos[1][0], gridPos[1][1]), (gridPos[0][0], gridPos[1][1]))
    pygame.draw.line(screen, (0, 0, 0), (gridPos[0][0], gridPos[0][1]), (gridPos[0][0], gridPos[1][1]))
    pygame.draw.line(screen, (0, 0, 0), (gridPos[1][0], gridPos[1][1]), (gridPos[1][0], gridPos[0][1]))

def updatePieces() -> Tuple[Piece, AwaitingPiece]:
  convertedSprite = Piece(newSprite.shape)
  newSprite.kill()
  new = AwaitingPiece(random.choice(list(pieceShape)))
  return convertedSprite, new

gridPos = ((30, 30), (300, 600)) # serves as boundaries which are used pretty much everywhere
gridLinesEnabled = False
interval = 30 # pixels per tetris square

pygame.init()
screen = pygame.display.set_mode([500, 630])
screenRect = screen.get_rect()
clock = pygame.time.Clock()

# Sprite group for active sprite
currentSprite = Piece(pieceShape.L_LEFT)
groupCurrent = pygame.sprite.GroupSingle()
groupCurrent.add(currentSprite)

# Awaiting sprite
newSprite = AwaitingPiece(pieceShape.L_RIGHT)
groupNew = pygame.sprite.GroupSingle()
groupNew.add(newSprite)

# Sprites which have hit the ground or another sprite
lockedSprites = pygame.sprite.Group()

# block falling mechanics
doFall = 0

while True:
  doFall += clock.get_rawtime()
  clock.tick()
  
  for event in pygame.event.get():
    if event.type == pygame.QUIT: 
      break

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_RIGHT:
        currentSprite.move(pieceDirection.RIGHT)
      elif event.key == pygame.K_LEFT:
        currentSprite.move(pieceDirection.LEFT)
      elif event.key == pygame.K_DOWN:
        currentSprite.move(pieceDirection.DOWN)
      elif event.key == pygame.K_UP:
        currentSprite.rotate()

  if pygame.sprite.spritecollideany(currentSprite, lockedSprites, pygame.sprite.collide_mask) or currentSprite.touchingBottom():
    lockedSprites.add(currentSprite)
    groupCurrent.empty()
    groupNew.empty()
    (currentSprite, newSprite) = updatePieces()
    groupCurrent.add(currentSprite)
    groupNew.add(newSprite)

  if doFall/1000 > 0.27:
    doFall = 0
    currentSprite.move(pieceDirection.DOWN)
  
  screen.fill((255, 255, 255))

  drawGrid()
  
  groupCurrent.draw(screen)
  groupNew.draw(screen)
  lockedSprites.draw(screen)
  
  pygame.display.update()
pygame.quit()