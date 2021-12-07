## **Res**ults

* First set of states S
  * **Random mazes, vanilla Q-learning:** 6 wins out of 240 episodes, 1st win on 39th episode.

* Second set of states S
  * **Same maze, vanilla Q-learning:** 48 wins out of 100 episodes, 1st win on 25th episode, 1 loss from 76th to 100th episode.
  * **Random mazes, vanilla Q-learning:** 49 wins out of 500 episodes, 1st win on 30th episode, 12 wins from 401st to 500th episode.
  * **Random mazes, Q-learning + Random Forest:** 7 wins out of 100 episodes, 1st win on 30th episode.Takes way longer time than vanilla Q-learning as all memory from all episodes need to be fit to the model, and the model is refitted at every time step.

## **Additional Information**

[Important Information]: https://drive.google.com/file/d/1xKVEjbnlA0dPOcXOg9w-yIffEzXRQWkm/view?usp=sharing

* Run learn.py to learn without simulation, and visualise.py to learn with simulation. *epochs* refers to number of episodes, *create_new_qtable* resets past experiences, and *regressor* would be used to predict the Q-values instead of using the values in the Q-table.

```python
regressor = False # edit this
if regressor:
    from edit_qtable_regressor import *
else:
    from edit_qtable import *

main(epochs = 100, create_new_qtable = True, regressor = regressor) # edit this
```

* If you set regressor as True, then you can change the regressor used in edit_qtable_regressor.py.

  ```python
  MODELS = {"LINEAR REGRESSION": LinearRegression(),
            "DECISION TREE": DecisionTreeRegressor(),
            "RANDOM FOREST": RandomForestRegressor()}
  ```

  ```python
  model = MODELS["LINEAR REGRESSION"] # edit this
  ```

  