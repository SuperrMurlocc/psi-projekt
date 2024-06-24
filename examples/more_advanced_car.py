from psi_environment.data.car import Car
from psi_environment.data.action import Action
from psi_environment.data.map_state import MapState
from psi_environment.environment import Environment
from psi_environment.api.environment_api import EnvironmentAPI


class MyCar(Car):
    def get_action(self, map_state: MapState) -> Action:
        my_road_key = self.get_road_key()
        my_road_pos = self.get_road_pos()

        api = EnvironmentAPI(map_state)

        my_road = api.get_road(my_road_key)
        if my_road.is_position_road_end(my_road_pos):
            available_actions = my_road.get_available_actions()
            min_traffic = 9999

            for action in available_actions:
                traffic = api.get_next_road(my_road_key, action).get_traffic()
                if traffic < min_traffic:
                    min_traffic = traffic
                    action = action
                
                if min_traffic == 0:
                    break

            return action

        return Action.FORWARD


if __name__ == "__main__":
    env = Environment(
        agent_type=MyCar,
        ticks_per_second=10,
        n_bots=50,
        n_points=10,
        traffic_lights_length=10,
        random_seed=2137,
    )
    while env.is_running():
        current_cost, is_running = env.step()
        print(current_cost, is_running)
