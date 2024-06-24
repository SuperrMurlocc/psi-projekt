from psi_environment.data.car import Car
from psi_environment.data.action import Action
from psi_environment.data.map_state import MapState
from psi_environment.environment import Environment


class MyCar(Car):
    def get_action(self, map_state: MapState) -> Action:
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
