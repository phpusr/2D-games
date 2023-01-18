from queue import Queue
import random
from dataclasses import dataclass
from enum import Enum


class SnakeDirection(Enum):
    up = 'U'
    down = 'D'
    left = 'L'
    right = 'R'

    @staticmethod
    def can_change(old_direction, new_direction):
        if old_direction is None or new_direction is None:
            return False

        access = { 
            SnakeDirection.up: [SnakeDirection.left, SnakeDirection.right],
            SnakeDirection.down: [SnakeDirection.left, SnakeDirection.right],
            SnakeDirection.left: [SnakeDirection.up, SnakeDirection.down],
            SnakeDirection.right: [SnakeDirection.up, SnakeDirection.down]
        }
        
        return new_direction in access[old_direction]


@dataclass
class SnakeBlock:
    xcor: int
    ycor: int
    direction: SnakeDirection
    directions: list


class SnakeError(RuntimeError):
    pass


class CrossError(SnakeError):
    pass


class Snake:
    def __init__(self, field_width: int, field_height: int, direction: SnakeDirection = SnakeDirection.left):
        self.prev_direction = SnakeDirection.left
        self.direction = direction
        self.speed = 1
        self.current_block_index = 0
        self.blocks = []
        self.step = 0
        padding = 5
        start_xcor = random.randint(padding, field_width - padding)
        start_ycor = random.randint(padding, field_height - padding)

        for index in range(10):
            self.blocks.append(SnakeBlock(
                xcor=start_xcor + index,
                ycor=start_ycor,
                direction=self.direction,
                directions=[]
            ))

    def change_direction(self, direction: SnakeDirection):
        for block_index, block in enumerate(self.blocks):
            block.directions.append((direction, self.step + 1 + block_index))

    def move(self):
        self.step += 1
        
        for block in self.blocks:
            if len(block.directions) > 0:
                direction, step = block.directions[0]
                if self.step == step:
                    block.directions.pop(0)
                    block.direction = direction

            if block.direction == SnakeDirection.up:
                xdiff = 0
                ydiff = -1
            elif block.direction == SnakeDirection.down:
                xdiff = 0
                ydiff = 1
            elif block.direction == SnakeDirection.left:
                xdiff = -1
                ydiff = 0
            else:
                xdiff = 1
                ydiff = 0

            block.xcor += xdiff
            block.ycor += ydiff

        # Checking block intersection
        for index in range(len(self.blocks) - 1):
            for index2 in range(index + 1, len(self.blocks)):
                #print(f'Check cross: {index}:{index2}')
                if self.blocks[index].xcor == self.blocks[index2].xcor and self.blocks[index].ycor == self.blocks[index2].ycor:
                    raise CrossError()
