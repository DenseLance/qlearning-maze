from random import random

from maze import *
from log_manager import *

# FUNCTIONS
def main(epochs = 100, create_new_qtable = False, regressor = False):
    end = False
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)

    if create_new_qtable: # reset all
        reset_epoch()
        update_exploration_rate(EXPLORATION_MAX)
        create_q_table()
        create_log()
        
    if regressor:
        model = fit_model()

    # Additional information
    initial_epoch = get_epoch()
    exploration_rate = get_exploration_rate()
    
    for epoch in range(initial_epoch + 1, initial_epoch + epochs + 1):
        pygame.display.set_caption(f"Maze {epoch}")
        maze = create_maze(WIDTH, HEIGHT)
        player_coor = START_COOR
        passed_by, player_maze, new_coors_found, empty_tiles_from_coor = player_perspective(maze, player_coor, [END_COOR] + [coor for coor in maze if coor[0] == 0 or coor[0] == WIDTH + 1 or coor[1] == 0 or coor[1] == HEIGHT + 1])

        # Additional information
        win = False
        number_of_actions = 0
        history = [] # LIST of TUPLES(state, action, reward, resultant_state)
        
        done = False
        while not done and number_of_actions < MAX_ACTIONS:
            screen.fill(WHITE)

            # Tile + Player rendering (based on player perspective)
            tile_rects = []
            for coor in player_maze:
                if player_maze[coor] == 1:
                    tile_rects.append(pygame.draw.rect(screen, BLACK, pygame.Rect((coor[0] * TILE_SIZE[0], coor[1] * TILE_SIZE[1]), TILE_SIZE)))
                elif player_maze[coor] == 2:
                    tile_rects.append(pygame.draw.rect(screen, BLUE, pygame.Rect((coor[0] * TILE_SIZE[0], coor[1] * TILE_SIZE[1]), TILE_SIZE)))
                elif player_maze[coor] == 3:
                    tile_rects.append(pygame.draw.rect(screen, RED, pygame.Rect((coor[0] * TILE_SIZE[0], coor[1] * TILE_SIZE[1]), TILE_SIZE)))
                elif player_maze[coor] == 4:
                    tile_rects.append(pygame.draw.rect(screen, GRAY, pygame.Rect((coor[0] * TILE_SIZE[0], coor[1] * TILE_SIZE[1]), TILE_SIZE)))
                    
            # Event manager
            for event in pygame.event.get():
                if event.type == QUIT:
                    done = True
                    end = True
            
            # Bot actions
            # ACTIONS: 0: LEFT, 1: RIGHT, 2: UP, 3: DOWN
            if random() < exploration_rate: # explore
                action = randint(0, 3)
            else:
                action = evaluate_action(empty_tiles_from_coor)
            state = empty_tiles_from_coor.copy()
            if action == 0:
                maze, player_maze, player_coor, hit_wall = move(maze, player_maze, player_coor, x = -1)
            elif action == 1:
                maze, player_maze, player_coor, hit_wall = move(maze, player_maze, player_coor, x = 1)
            elif action == 2:
                maze, player_maze, player_coor, hit_wall = move(maze, player_maze, player_coor, y = -1)
            elif action == 3:
                maze, player_maze, player_coor, hit_wall = move(maze, player_maze, player_coor, y = 1)
            
            passed_by, player_maze, new_coors_found, empty_tiles_from_coor = player_perspective(maze, player_coor, passed_by)

            # Rewards
            # REWARDS: NEW: 1, OLD: -1, WALL: -10, WIN: 100
            reward = 0
            if new_coors_found > 0:
                reward += REWARDS["NEW"]
            else:
                reward += REWARDS["OLD"]
            if hit_wall:
                reward += REWARDS["WALL"]
                
            # Win condition, 3 has been replaced by 2
            if 3 not in maze.values():
                reward += int(REWARDS["WIN"] * (2 - number_of_actions / MAX_ACTIONS)) # to reward taking shorter route, multiply reward by factor of 1.x
                win = True
                done = True
            
            # Update Q-table
            resultant_state = empty_tiles_from_coor.copy()
            history.append((state, action, reward, resultant_state))
            for experience in history[::-1]:
                update_q_table(experience[0], experience[1], experience[2], experience[3])
            number_of_actions += 1

            # Regressor
            if regressor:
                model = fit_model()
            
            pygame.display.update()
            clock.tick(60) # 60 fps

        # Decay functions
        exploration_rate = max(exploration_rate * EXPLORATION_DECAY, EXPLORATION_MIN)
        
        # Log manager
        append_to_log(epoch, number_of_actions, win)
        update_exploration_rate(exploration_rate)
        add_epoch(epoch)
        
        if end: # end all epoch
            break

    pygame.quit()

regressor = False
if regressor:
    from edit_qtable_regressor import *
else:
    from edit_qtable import *

main(epochs = 100, create_new_qtable = True, regressor = regressor)
