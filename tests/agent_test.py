from psi_environment.environment import Environment
import pandas as pd


def init_enviroment(agent_type, n_bots=10, n_points=3, traffic_lights_percentage=0.4, traffic_lights_length=10, random_seed=2137):
    env = Environment(
        agent_type=agent_type,
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


def calc_dist(movement_array, road_conditions):
    if len(movement_array) <= 2:
        return 0, 0, 0

    distance = 0
    stop_at_lights = 0
    stuck_in_traffic = 0

    prevMove = movement_array[0]
    prevRoadCondition = road_conditions[0]
    for move, road_condition in zip(movement_array[1:], road_conditions[1:]):
        if prevMove[0] != move[0]:
            distance += 1
        elif prevMove[0] == move[0] and prevMove[1] != move[1]:
            distance += 1

        if prevMove[1] == move[1]:
            stop_at_lights += 1

        if prevMove[1] == move[1] and prevRoadCondition == road_condition:
            stuck_in_traffic += 1

        prevMove = move
        prevRoadCondition = road_condition

    return distance, stop_at_lights, stuck_in_traffic


#class TestEnvironment(unittest.TestCase):
def run_single_test(agent_type, n_bots, n_points, traffic_lights_percentage, max_steps=500):
    env, params = init_enviroment(agent_type=agent_type, n_bots=n_bots, n_points=n_points,
                                  traffic_lights_percentage=traffic_lights_percentage)

    total_cost = 0
    movement = []
    road_conditions = []
    user_agent = [
        env._map._agents[key] for key in env._map._agents if isinstance(env._map._agents[key], agent_type)
    ][0]

    current_cost = 0

    while env.is_running() and current_cost < max_steps:
        current_cost, is_running = env.step()

        movement.append((user_agent.get_road_key(), user_agent.get_road_pos()))

        road = env._map._map_state.get_road(user_agent.get_road_key())
        road_conditions.append(road.get_number_of_cars())

    distance_traveled, stop_at_lights, stuck_in_traffic = calc_dist(movement, road_conditions)

    param_data = pd.DataFrame([params])

    result_data = {
        "Total Cost": [current_cost],
        "Distance Traveled": [distance_traveled],
        "Stop at Lights": [stop_at_lights],
        "Stuck in Traffic": [stuck_in_traffic],
        "Simulation Finished": [not env.is_running()],
        "Success": [not current_cost >= max_steps]
    }

    result_df = pd.DataFrame(result_data)

    print("Parametry symulacji:")
    print(param_data)

    print("Wyniki symulacji:")
    print(result_df)

    with open(f'simulation_results_{n_bots}_{n_points}_{traffic_lights_percentage}.txt', 'w') as f:
        f.write(f"Agent: {agent_type.__name__}")
        f.write("\nParametry symulacji:\n")
        f.write(param_data.to_string(index=False))
        f.write("\n\nWyniki symulacji:\n")
        f.write(result_df.to_string(index=False))


def run_multiple_tests(agent_type):
    n_bots_values = [5, 10, 15]
    n_points_values = [5, 10, 15]
    traffic_lights_percentages = [0.2, 0.4, 0.6]

    for n_bots in n_bots_values:
        for n_points in n_points_values:
            for traffic_lights_percentage in traffic_lights_percentages:
                print(
                    f"\nRunning simulation with n_bots={n_bots}, n_points={n_points}, traffic_lights_percentage={traffic_lights_percentage}")
                run_single_test(agent_type, n_bots, n_points, traffic_lights_percentage)


if __name__ == "__main__":

    # Import your own agent here
    agent = None
    run_multiple_tests(agent)