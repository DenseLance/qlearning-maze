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
# OLD: -1 if no new tile discovered (which means that the agent is walking backwards/further away from goal + discourage walking into dead ends)
# WALL: -10 if hit wall (wastes a move)
# WIN: +1000 if reach endpoint (highest reward to signify completion)
REWARDS = {"NEW": 1, "OLD": -1, "WALL": -10, "WIN": 1000}

def calculate_q_value(reward, old_q_value, expected_q_values): # expected_q_values: q-values of resultant state, obtained from regression models/q-table
    return (1 - LEARNING_RATE) * old_q_value + LEARNING_RATE * (reward + DISCOUNT_FACTOR * max(expected_q_values))

def create_q_table():
    db = sqlite3.connect("qtable.db")

    query = "DROP TABLE IF EXISTS QTable"
    db.execute(query)

    query = """
            CREATE TABLE QTable(
            'x' INTEGER NOT NULL,
            'y' INTEGER NOT NULL,
            'LEFT' INTEGER NOT NULL,
            'RIGHT' INTEGER NOT NULL,
            'UP' INTEGER NOT NULL,
            'DOWN' INTEGER NOT NULL,
            'action' INTEGER NOT NULL,
            'q_value' REAL NOT NULL
            )
            """

    db.execute(query)
    db.commit()
    db.close()

def get_q_value(state, action): # state: empty_tiles_from_coor, action: action
    db = sqlite3.connect("qtable.db")
    
    query = """
            SELECT q_value
            FROM QTable
            WHERE x = ?
            AND y = ?
            AND LEFT = ?
            AND RIGHT = ?
            AND UP = ?
            AND DOWN = ?
            AND action = ?
            """

    result = list(db.execute(query, list(state.values()) + [action]))
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
            WHERE x = ?
            AND y = ?
            AND LEFT = ?
            AND RIGHT = ?
            AND UP = ?
            AND DOWN = ?
            """

    result = list(db.execute(query, list(state.values())))
    for i in range(4): # actions: LEFT, RIGHT, UP, DOWN
        if i not in [item[0] for item in result]: # state action pair not in q-table
            result.append((i, INITIAL_Q_VALUE))
    result = sorted(result, key = lambda x: x[0])
    q_values = [item[1] for item in result]
    db.close()
    return q_values

def evaluate_action(state): # returns best action to take
    q_values = get_q_values_for_all_actions(state)
    max_q_value = max(q_values)
    action = choice([i for i in range(len(q_values)) if q_values[i] == max_q_value])
    return action

def update_q_table(state, action, reward, resultant_state): # state: empty_tiles_from_coor, action: action
    old_q_value = get_q_value(state, action)
    expected_q_values = get_q_values_for_all_actions(resultant_state)
    
    db = sqlite3.connect("qtable.db")
    if old_q_value != None: # state and action present in q_table
        new_q_value = calculate_q_value(reward, old_q_value, expected_q_values)
        query = """
                UPDATE QTable
                SET q_value = ?
                WHERE x = ?
                AND y = ?
                AND LEFT = ?
                AND RIGHT = ?
                AND UP = ?
                AND DOWN = ?
                AND action = ?
                """
    else:
        new_q_value = calculate_q_value(reward, INITIAL_Q_VALUE, expected_q_values)
        query = "INSERT INTO QTable(q_value, x, y, LEFT, RIGHT, UP, DOWN, action) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"

    try: # Windows sync issues
        db.execute(query, [new_q_value] + list(state.values()) + [action])
    except:
        time.sleep(5)
        db.execute(query, [new_q_value] + list(state.values()) + [action])
    db.commit()
    db.close()
    return new_q_value
