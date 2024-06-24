import unittest
from psi_environment.data.action import Action
from psi_environment.data.map_state import MapState
import pytest


def return_road_end(map_state, road_key):
    return map_state.get_road(road_key).length - 1


@pytest.mark.parametrize(
    "car1_road,car2_road,car1_expected_road,car2_expected_road",
    [
        ((6, 7), (8, 7), (7, 8), (7, 6)),
        ((1, 7), (13, 7), (7, 13), (7, 1)),
    ],
)
def test_both_cars_move_forward_no_collisions(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):

    actions = [(1, Action.FORWARD, False), (2, Action.FORWARD, False)]

    map_state = MapState(0, traffic_light_percentage=0)

    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))

    map_state.move_cars(actions)
    expected_result = {1: (car1_expected_road, 0), 2: (car2_expected_road, 0)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car1_expected_road,car2_expected_road",
    [
        ((13, 7), (1, 7), (7, 8), (7, 13)),
        ((8, 7), (1, 7), (7, 1), (7, 13)),
        ((1, 7), (13, 7), (7, 6), (7, 1)),
        ((6, 7), (13, 7), (7, 13), (7, 1)),
    ],
)
def test_two_cars_no_collisions_first_turns_right(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):

    actions = [(1, Action.RIGHT, False), (2, Action.FORWARD, False)]

    map_state = MapState(0, traffic_light_percentage=0)
    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))

    map_state.move_cars(actions)
    expected_result = {1: (car1_expected_road, 0), 2: (car2_expected_road, 0)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car1_expected_road,car2_expected_road",
    [
        ((1, 7), (13, 7), (7, 13), (7, 8)),
        ((1, 7), (8, 7), (7, 13), (7, 1)),
        ((13, 7), (1, 7), (7, 1), (7, 6)),
        ((13, 7), (6, 7), (7, 1), (7, 13)),
    ],
)
def test_two_cars_no_collision_second_turn_right(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):

    actions = [(1, Action.FORWARD, False), (2, Action.RIGHT, False)]

    map_state = MapState(0, traffic_light_percentage=0)
    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))

    map_state.move_cars(actions)
    expected_result = {1: (car1_expected_road, 0), 2: (car2_expected_road, 0)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car1_expected_road,car2_expected_road",
    [
        ((6, 7), (1, 7), (7, 8), (7, 13)),
        ((8, 7), (13, 7), (7, 6), (7, 1)),
        ((13, 7), (6, 7), (7, 1), (7, 8)),
        ((1, 7), (8, 7), (7, 13), (7, 6)),
    ],
)
def test_two_cars_forward_with_collisions_car1_moves_first(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):

    actions = [(1, Action.FORWARD, False), (2, Action.FORWARD, False)]

    map_state = MapState(0, traffic_light_percentage=0)
    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))

    map_state.move_cars(actions)
    expected_result = {
        1: (car1_expected_road, 0),
        2: (car2_road, return_road_end(map_state, car2_road)),
    }
    assert map_state._cars == expected_result

    map_state.move_cars(actions)
    expected_result = {1: (car1_expected_road, 1), 2: (car2_expected_road, 0)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car1_expected_road,car2_expected_road",
    [
        ((6, 7), (13, 7), (7, 8), (7, 1)),
        ((8, 7), (1, 7), (7, 6), (7, 13)),
        ((13, 7), (8, 7), (7, 1), (7, 6)),
        ((1, 7), (6, 7), (7, 13), (7, 8)),
    ],
)
def test_two_cars_forward_with_collisions_car2_moves_first(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):
    actions = [(1, Action.FORWARD, False), (2, Action.FORWARD, False)]

    map_state = MapState(0, traffic_light_percentage=0)
    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))

    map_state.move_cars(actions)
    expected_result = {
        1: (car1_road, return_road_end(map_state, car1_road)),
        2: (car2_expected_road, 0),
    }
    assert map_state._cars == expected_result

    map_state.move_cars(actions)
    expected_result = {1: (car1_expected_road, 0), 2: (car2_expected_road, 1)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car1_expected_road,car2_expected_road",
    [
        ((1, 7), (13, 7), (7, 13), (7, 6)),
        ((1, 7), (8, 7), (7, 13), (7, 13)),
        ((6, 7), (8, 7), (7, 8), (7, 13)),
        ((6, 7), (1, 7), (7, 8), (7, 8)),
        ((13, 7), (1, 7), (7, 1), (7, 8)),
        ((13, 7), (6, 7), (7, 1), (7, 1)),
        ((8, 7), (6, 7), (7, 6), (7, 1)),
        ((8, 7), (13, 7), (7, 6), (7, 6)),
    ],
)
def test_two_cars_collisions_first_forward_second_turn_left(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):
    actions = [(1, Action.FORWARD, False), (2, Action.LEFT, False)]

    map_state = MapState(0, traffic_light_percentage=0)
    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))

    map_state.move_cars(actions)
    expected_result = {
        1: (car1_expected_road, 0),
        2: (car2_road, return_road_end(map_state, car2_road)),
    }
    assert map_state._cars == expected_result

    map_state.move_cars(actions)
    expected_result = {1: (car1_expected_road, 1), 2: (car2_expected_road, 0)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car1_expected_road,car2_expected_road",
    [
        ((1, 7), (13, 7), (7, 8), (7, 1)),
        ((1, 7), (6, 7), (7, 8), (7, 8)),
        ((6, 7), (8, 7), (7, 1), (7, 6)),
        ((6, 7), (13, 7), (7, 1), (7, 1)),
        ((13, 7), (1, 7), (7, 6), (7, 13)),
        ((13, 7), (8, 7), (7, 6), (7, 6)),
        ((8, 7), (6, 7), (7, 13), (7, 8)),
        ((8, 7), (1, 7), (7, 13), (7, 13)),
    ],
)
def test_two_cars_collisions_first_turns_left_second_forward(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):
    actions = [(1, Action.LEFT, False), (2, Action.FORWARD, False)]

    map_state = MapState(0, traffic_light_percentage=0)
    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))

    map_state.move_cars(actions)
    expected_result = {
        1: (car1_road, return_road_end(map_state, car1_road)),
        2: (car2_expected_road, 0),
    }
    assert map_state._cars == expected_result

    map_state.move_cars(actions)
    expected_result = {1: (car1_expected_road, 0), 2: (car2_expected_road, 1)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car1_expected_road,car2_expected_road",
    [
        ((1, 7), (6, 7), (7, 6), (7, 13)),
        ((1, 7), (13, 7), (7, 6), (7, 8)),
        ((1, 7), (8, 7), (7, 6), (7, 1)),
        ((6, 7), (13, 7), (7, 13), (7, 8)),
        ((6, 7), (8, 7), (7, 13), (7, 1)),
        ((6, 7), (1, 7), (7, 13), (7, 6)),
        ((13, 7), (8, 7), (7, 8), (7, 1)),
        ((13, 7), (1, 7), (7, 8), (7, 6)),
        ((13, 7), (6, 7), (7, 8), (7, 13)),
        ((8, 7), (1, 7), (7, 1), (7, 6)),
        ((8, 7), (6, 7), (7, 1), (7, 13)),
        ((8, 7), (13, 7), (7, 1), (7, 8)),
    ],
)
def test_two_cars_both_turn_right(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):
    actions = [(1, Action.RIGHT, False), (2, Action.RIGHT, False)]

    map_state = MapState(0, traffic_light_percentage=0)
    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))

    map_state.move_cars(actions)
    expected_result = {1: (car1_expected_road, 0), 2: (car2_expected_road, 0)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car1_expected_road,car2_expected_road",
    [
        ((1, 7), (8, 7), (7, 8), (7, 13)),
        ((6, 7), (1, 7), (7, 1), (7, 8)),
        ((13, 7), (6, 7), (7, 6), (7, 1)),
        ((8, 7), (13, 7), (7, 13), (7, 6)),
    ],
)
def test_two_cars_both_turns_left_car1_moves_first(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):
    actions = [(1, Action.LEFT, False), (2, Action.LEFT, False)]

    map_state = MapState(0, traffic_light_percentage=0)
    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))

    map_state.move_cars(actions)
    expected_result = {
        1: (car1_expected_road, 0),
        2: (car2_road, return_road_end(map_state, car2_road)),
    }
    assert map_state._cars == expected_result

    map_state.move_cars(actions)
    expected_result = {1: (car1_expected_road, 0), 2: (car2_expected_road, 0)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car1_expected_road,car2_expected_road",
    [
        ((1, 7), (6, 7), (7, 8), (7, 1)),
        ((6, 7), (13, 7), (7, 1), (7, 6)),
        ((13, 7), (8, 7), (7, 6), (7, 13)),
        ((8, 7), (1, 7), (7, 13), (7, 8)),
    ],
)
def test_two_cars_both_turns_left_car2_moves_first(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):
    actions = [(1, Action.LEFT, False), (2, Action.LEFT, False)]

    map_state = MapState(0, traffic_light_percentage=0)
    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))

    map_state.move_cars(actions)
    expected_result = {
        1: (car1_road, return_road_end(map_state, car1_road)),
        2: (car2_expected_road, 0),
    }
    assert map_state._cars == expected_result

    map_state.move_cars(actions)
    expected_result = {1: (car1_expected_road, 0), 2: (car2_expected_road, 0)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car1_expected_road,car2_expected_road",
    [
        ((1, 7), (13, 7), (7, 8), (7, 6)),
        ((6, 7), (8, 7), (7, 1), (7, 13)),
        ((13, 7), (1, 7), (7, 6), (7, 8)),
        ((8, 7), (6, 7), (7, 13), (7, 1)),
    ],
)
def test_two_cars_both_turn_left_both_pass(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):
    actions = [(1, Action.LEFT, False), (2, Action.LEFT, False)]

    map_state = MapState(0, traffic_light_percentage=0)
    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))

    map_state.move_cars(actions)

    expected_result = {1: (car1_expected_road, 0), 2: (car2_expected_road, 0)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car3_road,car1_expected_road,car2_expected_road,car3_expected_road",
    [
        ((6, 7), (1, 7), (8, 7), (7, 8), (7, 13), (7, 13)),
        ((13, 7), (6, 7), (1, 7), (7, 1), (7, 8), (7, 8)),
    ],
)
def test_three_cars_c1_forward_c2_forward_c3_left(
    car1_road,
    car2_road,
    car3_road,
    car1_expected_road,
    car2_expected_road,
    car3_expected_road,
):
    actions = [
        (1, Action.FORWARD, False),
        (2, Action.FORWARD, False),
        (3, Action.LEFT, False),
    ]
    map_state = MapState(0, traffic_light_percentage=0)
    map_state._add_car(1, car1_road, return_road_end(map_state, car1_road))
    map_state._add_car(2, car2_road, return_road_end(map_state, car2_road))
    map_state._add_car(3, car3_road, return_road_end(map_state, car3_road))

    map_state.move_cars(actions)

    assert map_state._cars[1] == (car1_expected_road, 0)
    assert map_state._cars[2] == (car2_road, return_road_end(map_state, car2_road))
    assert map_state._cars[3] == (car3_road, return_road_end(map_state, car3_road))

    map_state.move_cars(actions)

    assert map_state._cars[2] == (car2_expected_road, 0)
    assert map_state._cars[3] == (car3_road, return_road_end(map_state, car3_road))

    map_state.move_cars(actions)

    assert map_state._cars[3] == (car3_expected_road, 0)


if __name__ == "__main__":

    unittest.main()
