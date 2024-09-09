import unittest
from psi_environment.data.action import Action
from psi_environment.data.map_state import MapState
from psi_environment.environment import Environment
import pandas as pd
import pytest


def init_enviroment(AGENT_TYPE,n_bots=10, n_points=3, traffic_lights_percentage=0.4, traffic_lights_length=10, random_seed=2137):
    env = Environment(
        agent_type=AGENT_TYPE,
        n_bots=n_bots,
        n_points=n_points,
        traffic_lights_percentage=traffic_lights_percentage,
        traffic_lights_length=traffic_lights_length,
        random_seed=random_seed
    )
    return env, {
        "n_bots": n_bots,
        "n_points": n_points,
        "traffic_lights_percentage": traffic_lights_percentage,
        "traffic_lights_length": traffic_lights_length,
        "random_seed": random_seed
    }


def calc_dist(movement_array):
    if len(movement_array) <= 2:
        return 0

    distance = 0
    prevMove = movement_array[0]
    for move in movement_array[1:]:
        if prevMove[0] != move[0]:
            distance += 1
        elif prevMove[0] == move[0] and prevMove[1] != move[1]:
            distance += 1

        prevMove = move

    return distance


def agent_test_env_with_movement(agent_type, max_steps=500):
    env, params = init_enviroment(agent_type)

    movement = []

    user_agent = [
        env._map._agents[key] for key in env._map._agents if isinstance(env._map._agents[key], agent_type)][0]

    current_cost = 0

    while env.is_running() and current_cost < max_steps:
        current_cost, is_running = env.step()

        movement.append((user_agent.get_road_key(), user_agent.get_road_pos()))

    distance_traveled = calc_dist(movement)

    param_data = pd.DataFrame([params])

    result_data = {
        "Total Cost": [current_cost],
        "Distance Traveled": [distance_traveled],
        "Simulation Finished": [not env.is_running()],
        "Success": [not current_cost >= max_steps]
    }

    result_df = pd.DataFrame(result_data)

    print("Parametry symulacji:")
    print(param_data)

    print("Wyniki symulacji:")
    print(result_df)

    with open('simulation_results.txt', 'w') as f:
        f.write(f"Agent: {agent_type.__name__}")
        f.write("\nParametry symulacji:\n")
        f.write(param_data.to_string(index=False))
        f.write("\n\nWyniki symulacji:\n")
        f.write(result_df.to_string(index=False))



if __name__ == "__main__":

    agent_test_env_with_movement(agent_type=None, max_steps=500)