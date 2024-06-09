from psi_environment.data.car import Car, Action
from psi_environment.data.map_state import MapState
from psi_environment.environment import Environment
from time import sleep


class MyCar(Car):
    def get_action(self, map_state: MapState) -> Action:
        return Action.FORWARD


if __name__ == "__main__":
    env = Environment(2137, MyCar, ticks_per_second=1, n_bots=50)
    while True:
        if not env.step():
            break
