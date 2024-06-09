from psi_environment.data.car import Car, Action
from psi_environment.data.map_state import MapState
from psi_environment.environment import Environment


class MyCar(Car):
    def get_action(self, map_state: MapState) -> Action:
        return Action.FORWARD


if __name__ == "__main__":
    env = Environment(2137, MyCar)
    while True:
        if not env.step():
            break
