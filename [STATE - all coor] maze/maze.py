# VERSION FOR MACHINE LEARNING
import sys
import pygame
from pygame.locals import *
from random import randint

# VAR
BLACK = (0, 0, 0)
GRAY = (127, 127, 127)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

WIDTH = 8
HEIGHT = 8
TILE_SIZE = (20, 20)
WINDOW_SIZE = ((WIDTH + 2) * TILE_SIZE[0], (HEIGHT + 2) * TILE_SIZE[1])

START_COOR = (1, 1)
END_COOR = (WIDTH, HEIGHT)

def print_maze(maze):
    x_coors = [coor[0] for coor in maze]
    y_coors = [coor[1] for coor in maze]
    min_x, max_x = min(x_coors), max(x_coors)
    min_y, max_y = min(y_coors), max(y_coors)

    for y in range(min_y, max_y + 1):
        output = ""
        for x in range(min_x, max_x + 1):
            if maze[(x, y)]:
                output += f"{maze[(x, y)]}"
            else:
                output += " "
        print(output)

def write_maze_to_file(maze, epoch = 1):
    x_coors = [coor[0] for coor in maze]
    y_coors = [coor[1] for coor in maze]
    min_x, max_x = min(x_coors), max(x_coors)
    min_y, max_y = min(y_coors), max(y_coors)

    output = ""
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if maze[(x, y)]:
                output += f"{maze[(x, y)]}"
            else:
                output += " "
        output += "\n"
    with open(f"mazes/maze {epoch}.txt", "w") as f:
        f.write(output)
        f.write("\n")
        f.write(str(maze)) # for future copying to python file and rerun
        f.close()

def create_maze(width = 30, height = 30): # Maze generation via recursive division --> https://en.wikipedia.org/wiki/Maze_generation_algorithm
    def create_wall(area):
        if area:
            x_coors = [coor[0] for coor in area]
            y_coors = [coor[1] for coor in area]
            min_x, max_x = min(x_coors), max(x_coors)
            min_y, max_y = min(y_coors), max(y_coors)
            vertical = bool(randint(0, max_x - min_x + max_y - min_y) < max_x - min_x)
            
            if max_x - min_x > 0 or max_y - min_y > 0: # wall created (width > 1, height > 1)
                if max_y - min_y <= 0 or vertical: # vertical wall
                    x_rand = randint(min_x, max_x)
                    if maze[(x_rand - 1, min_y - 2)] == 1 and maze[(x_rand + 1, min_y - 2)] == 1 and maze[(x_rand, min_y - 2)] == 0:
                        min_y += 1
                    if maze[(x_rand - 1, max_y + 2)] == 1 and maze[(x_rand + 1, max_y + 2)] == 1 and maze[(x_rand, max_y + 2)] == 0:
                        max_y -= 1
                    for y in range(min_y - 1, max_y + 2):
                        maze[(x_rand, y)] = 1
                        
                    y_rand = randint(min_y - 1, max_y + 1)
                    maze[(x_rand, y_rand)] = 0 # gap in wall
                    
                    create_wall({coor: area[coor] for coor in area if coor[0] < x_rand - 1})
                    create_wall({coor: area[coor] for coor in area if coor[0] > x_rand + 1})
                else: # horizontal wall
                    y_rand = randint(min_y, max_y)
                    if maze[(min_x - 2, y_rand - 1)] == 1 and maze[(min_x - 2, y_rand + 1)] == 1 and maze[(min_x - 2, y_rand)] == 0:
                        min_x += 1
                    if maze[(max_x + 2, y_rand - 1)] == 1 and maze[(max_x + 2, y_rand + 1)] == 1 and maze[(max_x + 2, y_rand)] == 0:
                        max_x -= 1
                    for x in range(min_x - 1, max_x + 2):
                        maze[(x, y_rand)] = 1

                    x_rand = randint(min_x - 1, max_x + 1) 
                    maze[(x_rand, y_rand)] = 0 # gap in wall

                    create_wall({coor: area[coor] for coor in area if coor[1] < y_rand - 1})
                    create_wall({coor: area[coor] for coor in area if coor[1] > y_rand + 1})

    def create_start_and_end(width, height):
        maze[(1, 1)] = 2
        maze[(width, height)] = 3

    # 0: empty tile
    # 1: wall
    # 2: start/player
    # 3: end
    # 4: unknown (from player's perspective)
    maze = dict(zip([(x, y) for y in range(height + 2) for x in range(width + 2)], [0 if x > 0 and x < width + 1 and y > 0 and y < height + 1 else 1 for y in range(height + 2) for x in range(width + 2)]))
    create_wall({coor: maze[coor] for coor in maze if coor[0] > 1 and coor[0] < width and coor[1] > 1 and coor[1] < height})
    create_start_and_end(width, height)    
    return maze

def player_perspective(maze, player_coor, coors_viewed = []): # coors_viewed includes passed_by
    new_coors_found = 0
    
    coor = [player_coor[0], player_coor[1]]
    while maze[tuple(coor)] != 1: # left
        coors_viewed.append(tuple(coor))
        coor[0] -= 1
        if tuple(coor) not in coors_viewed:
            new_coors_found += 1
    coors_viewed.append(tuple(coor))
    if tuple(coor) not in coors_viewed:
        new_coors_found += 1
    
    coor = [player_coor[0], player_coor[1]]
    while maze[tuple(coor)] != 1: # right
        coors_viewed.append(tuple(coor))
        coor[0] += 1
        if tuple(coor) not in coors_viewed:
            new_coors_found += 1
    coors_viewed.append(tuple(coor))
    if tuple(coor) not in coors_viewed:
        new_coors_found += 1
    
    coor = [player_coor[0], player_coor[1]]
    while maze[tuple(coor)] != 1: # up
        coors_viewed.append(tuple(coor))
        coor[1] -= 1
        if tuple(coor) not in coors_viewed:
            new_coors_found += 1
    coors_viewed.append(tuple(coor))
    if tuple(coor) not in coors_viewed:
        new_coors_found += 1

    coor = [player_coor[0], player_coor[1]]
    while maze[tuple(coor)] != 1: # down
        coors_viewed.append(tuple(coor))
        coor[1] += 1
        if tuple(coor) not in coors_viewed:
            new_coors_found += 1
    coors_viewed.append(tuple(coor))
    if tuple(coor) not in coors_viewed:
        new_coors_found += 1

    coors_viewed = list(set(coors_viewed))
    return coors_viewed, {coor: maze[coor] if coor in coors_viewed else 4 for coor in maze}, new_coors_found

def move(maze, player_maze, player_coor, x = 0, y = 0):
    final_player_coor = (player_coor[0] + x, player_coor[1] + y)
    if maze[final_player_coor] == 1: # wall
        final_player_coor = player_coor

    maze[player_coor], player_maze[player_coor] = 0, 0
    maze[final_player_coor], player_maze[final_player_coor] = 2, 2
    
    return maze, player_maze, final_player_coor, final_player_coor == player_coor
