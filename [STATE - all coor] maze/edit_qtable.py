import time
import sqlite3
from random import choice
from maze import *

# HYPERPARAMETERS
INITIAL_Q_VALUE = 0.0
MAX_ACTIONS = WIDTH * HEIGHT # limit maximum number of actions player can take to prevent infinite loop

DISCOUNT_FACTOR = 0.95
LEARNING_RATE = 0.05

EXPLORATION_MIN = 0.10
EXPLORATION_MAX = 0.95
EXPLORATION_DECAY = 0.995

# NEW: +1 if new tile discovered
# OLD: -1 if no new tile discovered
# WALL: -10 if hit wall
# WIN: +1000 if reach endpoint
REWARDS = {"NEW": 1, "OLD": -1, "WALL": -10, "WIN": 1000}

def calculate_q_value(reward, old_q_value, expected_q_values): # expected_q_values: q-values of resultant state, obtained from regression models/q-table
    return (1 - LEARNING_RATE) * old_q_value + LEARNING_RATE * (reward + DISCOUNT_FACTOR * max(expected_q_values))

def create_q_table():
    db = sqlite3.connect("qtable.db")

    query = "DROP TABLE IF EXISTS QTable"
    db.execute(query)

    query = "CREATE TABLE QTable(\n"
    for y in range(1, HEIGHT + 1): # does not include border of maze
        for x in range(1, WIDTH + 1):
            query += f"'{(x, y)}' INTEGER NOT NULL,\n"
    query += "'action' INTEGER NOT NULL,\n"
    query += "'q_value' REAL NOT NULL)"

    db.execute(query)
    db.commit()
    db.close()

def get_q_value(state, action): # state: player_maze, action: action
    db = sqlite3.connect("qtable.db")
    
    query = f"""
            SELECT q_value
            FROM QTable
            WHERE action = {action}
            """

    for y in range(1, HEIGHT + 1): # does not include border of maze
        for x in range(1, WIDTH + 1):
            query += f"AND \"{(x, y)}\" = {state[(x, y)]}\n"

    result = list(db.execute(query))
    if result:
        result = result[0][0]
    else:
        result = None
    db.close()
    return result

def get_q_values_for_all_actions(state):
    db = sqlite3.connect("qtable.db")
    
    query = """
            SELECT action, q_value
            FROM QTable
            """

    for y in range(1, HEIGHT + 1): # does not include border of maze
        for x in range(1, WIDTH + 1):
            if (x, y) == (1, 1):
                query += f"WHERE \"{(x, y)}\" = {state[(x, y)]}\n"
            else:
                query += f"AND \"{(x, y)}\" = {state[(x, y)]}\n"

    query += "ORDER BY action ASC"

    result = list(db.execute(query))
    q_values = []
    for i in range(4): # actions: LEFT, RIGHT, UP, DOWN
        if i not in [item[0] for item in result]: # state action pair not in q-table
            result.append((i, INITIAL_Q_VALUE))
    result = sorted(result, key = lambda x: x[0])
    for item in result:
        q_values.append(item[1])
    db.close()
    return q_values

def evaluate_action(state): # returns best action to take
    q_values = get_q_values_for_all_actions(state)
    max_q_value = max(q_values)
    actions = []
    for i in range(len(q_values)):
        if q_values[i] == max_q_value:
            actions.append(i)
    action = choice(actions)
    return action

def update_q_table(state, action, reward, resultant_state): # state: player_maze, action: action
    old_q_value = get_q_value(state, action)
    expected_q_values = get_q_values_for_all_actions(resultant_state)
    
    db = sqlite3.connect("qtable.db")
    if old_q_value != None: # state and action present in q_table
        new_q_value = calculate_q_value(reward, old_q_value, expected_q_values)
        query = f"""
                UPDATE QTable
                SET q_value = {new_q_value}
                WHERE action = {action}
                """
        
        for y in range(1, HEIGHT + 1): # does not include border of maze
            for x in range(1, WIDTH + 1):
                query += f"AND \"{(x, y)}\" = {state[(x, y)]}\n"
    else:
        new_q_value = calculate_q_value(reward, INITIAL_Q_VALUE, expected_q_values)
        query = "INSERT INTO QTable VALUES("
        
        for y in range(1, HEIGHT + 1): # does not include border of maze
            for x in range(1, WIDTH + 1):
                query += f"{state[(x, y)]}, "
        query += f"{action}, "
        query += f"{new_q_value})"

    try: # Windows sync issues
        db.execute(query)
    except:
        time.sleep(5)
        db.execute(query)
    db.commit()
    db.close()
    return new_q_value
