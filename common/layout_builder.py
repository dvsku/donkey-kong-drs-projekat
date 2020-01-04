import numpy as np

from client.globals import SCENE_WIDTH, SCENE_GRID_BLOCK_WIDTH, SCENE_HEIGHT, SCENE_GRID_BLOCK_HEIGHT
from common.enums import LayoutBlock


def get_level_layout(level: str):
    layout = np.full(300, None).reshape(int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT),
                                        int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH))

    with open(level) as file:
        line = file.readline()
        row = 0
        while line:
            for column in range(int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH)):
                if line[column] == "P":
                    layout[row][column] = LayoutBlock.Platform
                elif line[column] == "L":
                    layout[row][column] = LayoutBlock.Ladder

            row += 1
            line = file.readline()

    return layout
