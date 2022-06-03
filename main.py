import pygame
import enum
import os
import random
from typing import Tuple, Optional

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
  def getStopOffsets(cls, shape, type: int, rotation: int) -> int:
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
    if type in (0, 1): return (offsetsRight if type == 0 else offsetsBottom)[shape][rotation] * interval

  @classmethod
  def getRectOffset(cls, shape, rotation: int) -> tuple:
    posOffsets = {
      cls.LONG: (
        (
          (0, 0),
          (1, 0),
          (2, 0),
          (3, 0)
        ),
        (),
        (),
        (
          (0, 0),
          (0, 1),
          (0, 2),
          (0, 3)
        )
      ),
      cls.T: (
        (
          (0, 0),
          (1, 0),
          (2, 0),
          (1, 1)
        ),
        (
          (0, 0),
          (0, 1),
          (1, 1),
          (0, 2)
        ),
        (
          (1, 0),
          (0, 1),
          (1, 1),
          (2, 1)
        ),
        (
          (1, 0),
          (0, 1),
          (1, 1),
          (1, 2)
        )
      ),
      cls.SQUARE: [
        (
          (0, 0),
          (1, 0),
          (0, 1),
          (1, 1)
        )
      ],
      cls.Z_LEFT: (
        (
          (1, 0),
          (2, 0),
          (0, 1),
          (1, 1),
        ),
        (),
        (),
        (
          (0, 0),
          (0, 1),
          (1, 1),
          (1, 2),
        )
      ),
      cls.Z_RIGHT: (
        (
          (0, 0),
          (1, 0),
          (1, 1),
          (2, 1)
        ),
        (),
        (),
        (
          (1, 0),
          (0, 1),
          (1, 1),
          (0, 2)
        )
      ),
      cls.L_LEFT: (
        (
          (0, 0),
          (1, 0),
          (2, 0),
          (0, 1)
        ),
        (
          (0, 0),
          (0, 1),
          (1, 1),
          (1, 2)
        ),
        (
          (2, 0),
          (0, 1),
          (1, 1),
          (2, 1)
        ),
        (
          (0, 0),
          (0, 1),
          (0, 2),
          (1, 2)
        )
      ),
      cls.L_RIGHT: (
        (
          (0, 0),
          (1, 0),
          (2, 0),
          (2, 1)
        ),
        (
          (1, 0),
          (1, 1),
          (1, 2),
          (0, 2)
        ),
        (
          (0, 0),
          (0, 1),
          (1, 1),
          (2, 1)
        ),
        (
          (0, 0),
          (1, 0),
          (0, 1),
          (0, 2)
        )
      )
    }
    return posOffsets[shape][rotation]

class pieceDirection(enum.Enum):
  LEFT = 0
  RIGHT = 1
  DOWN = 2
  UP = 3

class gameState(enum.Enum):
  NORMAL = 0
  LOST = 1

class AwaitingPiece(pygame.sprite.Sprite):
  """
  AwaitingPiece is used to summon a sprite at (350, 350) in the screen to show the user what the next piece will be. It is destroyed and converted to a Piece when the awaiting piece is ready to be called to the top of the game screen.
  """
  def __init__(self, shape: pieceShape) -> None:
    pygame.sprite.Sprite.__init__(self)
    self.shape = shape
    
    self.image = pygame.transform.scale(
      pygame.image.load(os.path.join(self.shape.value)),
      pieceShape.getSize(self.shape)
    )

    self.rect = self.image.get_rect()
    (self.rect[0], self.rect[1]) = (350, 350)

  def getShape(self) -> pieceShape:
    return self.shape

class Piece(pygame.sprite.Sprite):
  def __init__(self, shape: pieceShape) -> None:
    pygame.sprite.Sprite.__init__(self)
    self.shape = shape
    self.image = pygame.transform.scale(
      pygame.image.load(os.path.join(self.shape.value)),
      pieceShape.getSize(self.shape)
    )
    self.mask = pygame.mask.from_surface(self.image) # collision mask
    self.mask = self.mask.scale((self.image.get_width() - 10, self.image.get_height() + 15))
    self.rotationState = 0
    self.rightStopOffset = pieceShape.getStopOffsets(self.shape, 0, self.rotationState)
    self.bottomStopOffset = pieceShape.getStopOffsets(self.shape, 1, self.rotationState)
    self.rectPartial = pieceShape.getRectOffset(self.shape, self.rotationState)
    
    # rect is the actual position of the piece (does not include collision mask)
    self.rect = self.image.get_rect()
    (self.rect[0], self.rect[1]) = gridPos[0]
  
  def touchingBottom(self) -> bool:
    """
    Returns a bool if the current object's Y rect position is below the bottom stop limit
    """
    return self.rect[1] >= gridPos[1][1] - self.bottomStopOffset

  def getCoords(self) -> tuple:    
    self.rectPartial = pieceShape.getRectOffset(self.shape, self.rotationState)
    currentPos = (self.rect[0], self.rect[1])
    partialPieceCoords = tuple([(currentPos[0] + i[0] * interval, currentPos[1] + i[1] * interval) for i in self.rectPartial])
    print(partialPieceCoords)
    return partialPieceCoords
  
  def crop(self):
    return
    
    (width, height) = self.image.get_size()
    newImage = pygame.Surface((width, height))
    newImage.set_colorkey((0, 0, 0))
    self.image.blit(newImage, (0, 0), (0, 0, width, 30))
    pygame.mask.from_surface(newImage)
    #self.image.kill()
    #self.rect.update(0, 30, width, height)

    
    
  def rotate(self) -> None:
    rotation = -90
    # TODO: shapes can clip through the right wall if rotated incorrectly
    if self.shape == pieceShape.SQUARE:
      return # Squares cause funky things to occur, so they are skipped
    elif self.shape in (pieceShape.Z_LEFT, pieceShape.Z_RIGHT, pieceShape.LONG):
      if self.rotationState == 0:
        # These values need to be tweaked as there is a weird behavior when in the 1st position when trying to place a Z piece
        rotation = 90 # wrap around back to state 0
        self.rotationState = 2
    
    self.image = pygame.transform.rotate(self.image, rotation) # Rotate image 90 degrees
    self.mask = pygame.mask.from_surface(self.image) # apply collision mask to sprite
    self.mask = self.mask.scale((self.image.get_width() - 10, self.image.get_height() + 15))
    self.rotationState += 1 if self.rotationState != 3 else -3 # increment rotation state (or reset if overflow)
    self.rightStopOffset = pieceShape.getStopOffsets(self.shape, 0, self.rotationState)
    self.bottomStopOffset = pieceShape.getStopOffsets(self.shape, 1, self.rotationState)

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
  pygame.draw.line(screen, (0, 0, 0), (gridPos[0][0], gridPos[0][1]), (gridPos[1][0], gridPos[0][1]))
  pygame.draw.line(screen, (0, 0, 0), (gridPos[1][0], gridPos[1][1]), (gridPos[0][0], gridPos[1][1]))
  pygame.draw.line(screen, (0, 0, 0), (gridPos[0][0], gridPos[0][1]), (gridPos[0][0], gridPos[1][1]))
  pygame.draw.line(screen, (0, 0, 0), (gridPos[1][0], gridPos[1][1]), (gridPos[1][0], gridPos[0][1]))

def updatePieces(awaitingPiece) -> Tuple[Piece, AwaitingPiece]:
  convertedSprite = Piece(awaitingPiece.shape)
  awaitingPiece.kill()
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
currentSprite = Piece(random.choice(list(pieceShape)))
groupCurrent = pygame.sprite.GroupSingle()
groupCurrent.add(currentSprite)

# Awaiting sprite
newSprite = AwaitingPiece(random.choice(list(pieceShape)))
groupNew = pygame.sprite.GroupSingle()
groupNew.add(newSprite)

# Sprites which have hit the ground or another sprite
lockedSprites = pygame.sprite.Group()

# block falling mechanics
doFall = 0

pygame.display.set_caption('Tetris')
font = pygame.font.Font('freesansbold.ttf', 32)

score = 0


def text():
  scoreText = font.render(("Score:"), True, (0, 0, 0))
  scoreTextRect = scoreText.get_rect()
  scoreTextRect.center = (400, 150)
  
  scoreAmountText = font.render(str(score), True, (0, 0, 0))
  scoreAmountTextRect = scoreAmountText.get_rect()
  scoreAmountTextRect.center = (400, 200)

  nextPieceText = font.render("Next Piece", True, (0, 0, 0))
  nextPieceTextRect = nextPieceText.get_rect()
  nextPieceTextRect.center = (400, 300)

  screen.blit(scoreText, scoreTextRect)
  screen.blit(scoreAmountText, scoreAmountTextRect)
  screen.blit(nextPieceText, nextPieceTextRect)

def lineCheck(lockedPieces) -> Optional[gameState]:
  potentialLines = [0 for _ in range(20)]
  detectedLines = []
  for lockedPiece in lockedPieces:
    pieceY = (lockedPiece.rect[1] - gridPos[0][1]) / interval
    if pieceY <= 1: return gameState.LOST
    partialPieceCoords = lockedPiece.getCoords()
    for coord in partialPieceCoords:
      potentialLines[int((coord[1] - gridPos[0][1]) / interval)] += 1
  print(potentialLines)
  for i in range(len(potentialLines)):
    if potentialLines[i] >= 9:
      detectedLines.append(i)
  if any(detectedLines): print(f"LINE(S) AT {detectedLines}")

pause = False
while True:
  if pause:
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        pause = False
    continue
  
  doFall += clock.get_rawtime()
  clock.tick()
  addY = 0
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
        score += 1
      elif event.key == pygame.K_UP:
        currentSprite.rotate()
      elif event.key == pygame.K_ESCAPE:
        pause = True

  if pygame.sprite.spritecollideany(currentSprite, lockedSprites, pygame.sprite.collide_mask) or currentSprite.touchingBottom():
    #currentSprite.mask = currentSprite.mask.scale((currentSprite.image.get_width(), currentSprite.image.get_height()))
    currentSprite.crop()
    lockedSprites.add(currentSprite)
    groupCurrent.empty()
    groupNew.empty()
    (currentSprite, newSprite) = updatePieces(newSprite)
    groupCurrent.add(currentSprite)
    groupNew.add(newSprite)

    state = lineCheck(lockedSprites)
    if state == gameState.LOST: break

  if doFall/1000 > 0.27:
    doFall = 0
    score += 1
    currentSprite.move(pieceDirection.DOWN)
  
  screen.fill((255, 255, 255))
  drawGrid()
  
  groupCurrent.draw(screen)
  groupNew.draw(screen)
  text()  
    
  lockedSprites.draw(screen)
  pygame.display.update()
pygame.quit()