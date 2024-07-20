import unittest
from psi_environment.data.action import Action
from psi_environment.data.map_state import MapState
import pytest


def return_road_end(map_state, road_key):
    return map_state.get_road(road_key).length - 1


def basic_test_setup(roads: list):
    map_state = MapState(0, traffic_light_percentage=0)
    for car_id, road in enumerate(roads):
        map_state._add_car(car_id + 1, road, return_road_end(map_state, road))
    return map_state


def update_actions_and_expected_pos(expected_positions, current_positions, actions):

    cars_id = []
    for road, car_id in expected_positions.intersection(current_positions):
        actions[car_id-1] = (car_id, Action.FORWARD)
        expected_positions.remove((road, car_id))
        cars_id.append(car_id)
    return cars_id


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

    actions = [(1, Action.FORWARD), (2, Action.FORWARD)]

    map_state = basic_test_setup([car1_road, car2_road])

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

    actions = [(1, Action.RIGHT), (2, Action.FORWARD)]

    map_state = basic_test_setup([car1_road, car2_road])

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
def test_two_cars_no_collision_second_turns_right(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):

    actions = [(1, Action.FORWARD), (2, Action.RIGHT)]

    map_state = basic_test_setup([car1_road, car2_road])

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

    actions = [(1, Action.FORWARD), (2, Action.FORWARD)]

    map_state = basic_test_setup([car1_road, car2_road])

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
    actions = [(1, Action.FORWARD), (2, Action.FORWARD)]

    map_state = basic_test_setup([car1_road, car2_road])

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
def test_two_cars_collisions_first_forward_second_turns_left(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):
    actions = [(1, Action.FORWARD), (2, Action.LEFT)]

    map_state = basic_test_setup([car1_road, car2_road])

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
    actions = [(1, Action.LEFT), (2, Action.FORWARD)]

    map_state = basic_test_setup([car1_road, car2_road])

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
    actions = [(1, Action.RIGHT), (2, Action.RIGHT)]

    map_state = basic_test_setup([car1_road, car2_road])

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
def test_two_cars_both_turn_left_car1_moves_first(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):
    actions = [(1, Action.LEFT), (2, Action.LEFT)]

    map_state = basic_test_setup([car1_road, car2_road])

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
def test_two_cars_both_turn_left_car2_moves_first(
    car1_road, car2_road, car1_expected_road, car2_expected_road
):
    actions = [(1, Action.LEFT), (2, Action.LEFT)]

    map_state = basic_test_setup([car1_road, car2_road])

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
    actions = [(1, Action.LEFT), (2, Action.LEFT)]

    map_state = basic_test_setup([car1_road, car2_road])

    map_state.move_cars(actions)

    expected_result = {1: (car1_expected_road, 0), 2: (car2_expected_road, 0)}
    assert map_state._cars == expected_result


@pytest.mark.parametrize(
    "car1_road,car2_road,car3_road,car1_expected_road,car2_expected_road,car3_expected_road",
    [
        ((6, 7), (1, 7), (8, 7), (7, 8), (7, 13), (7, 13)),
        ((13, 7), (6, 7), (1, 7), (7, 1), (7, 8), (7, 8)),
        ((1, 7), (8, 7), (13, 7), (7, 13), (7, 6), (7, 6)),
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
    """
    Test case where car 1 moves first, then car 2 and then car 3
    """
    actions = [
        (1, Action.FORWARD),
        (2, Action.FORWARD),
        (3, Action.LEFT),
    ]

    map_state = basic_test_setup([car1_road, car2_road, car3_road])

    map_state.move_cars(actions)

    assert map_state._cars[1] == (car1_expected_road, 0)
    assert map_state._cars[2] == (car2_road, return_road_end(map_state, car2_road))
    assert map_state._cars[3] == (car3_road, return_road_end(map_state, car3_road))

    map_state.move_cars(actions)

    assert map_state._cars[2] == (car2_expected_road, 0)
    assert map_state._cars[3] == (car3_road, return_road_end(map_state, car3_road))

    map_state.move_cars(actions)

    assert map_state._cars[3] == (car3_expected_road, 0)


@pytest.mark.parametrize(
    "car1_road,car2_road,car3_road,car1_expected_road,car2_expected_road,car3_expected_road",
    [
        ((1, 7), (8, 7), (6, 7), (7, 13), (7, 6), (7, 1)),
        ((13, 7), (6 ,7), (8, 7), (7,1), (7,8), (7, 13)),
    ],
)
def test_three_deadlock_cars_c1_forward_c2_forward_c3_left(
    car1_road,
    car2_road,
    car3_road,
    car1_expected_road,
    car2_expected_road,
    car3_expected_road,
):
    """
    Test case where all cars wait for each other
    """
    actions = [
        (1, Action.FORWARD),
        (2, Action.FORWARD),
        (3, Action.LEFT),
    ]
    map_state = basic_test_setup([car1_road, car2_road, car3_road])
    expected_roads = {
        (car1_expected_road, 1),
        (car2_expected_road, 2),
        (car3_expected_road, 3),
    }
    map_state.move_cars(actions)
    curr_pos = set(
        [(map_state.get_cars()[k][0], k) for k in map_state.get_cars().keys()]
    )

    assert (
        len(expected_roads.intersection(curr_pos)) >= 1
    ), "cars did not move to their goal"
    update_actions_and_expected_pos(expected_roads, curr_pos,  actions)
    map_state.move_cars(actions)

    curr_pos = set(
        [(map_state.get_cars()[k][0], k) for k in map_state.get_cars().keys()]
    )
    assert (
        len(expected_roads.intersection(curr_pos)) >= 1
    ), "car did not move to their goal"
    update_actions_and_expected_pos(expected_roads, curr_pos, actions)

    map_state.move_cars(actions)
    curr_pos = set(
        [(map_state.get_cars()[k][0], k) for k in map_state.get_cars().keys()]
    )
    assert (
        len(expected_roads.intersection(curr_pos)) == 1 or len(expected_roads) == 0
    ), "car did not move to their goal"


@pytest.mark.parametrize(
    "car1_road,car2_road,car3_road,car1_expected_road,car2_expected_road,car3_expected_road",
    [
        ((13, 7), (6, 7), (8, 7), (7, 6), (7, 8), (7, 13)),
        ((1, 7), (13, 7), (8, 7), (7, 8), (7, 1), (7, 13)),
        #((6, 7), (13, 7), (8, 7), (7, 1), (7, 1), (7, 13)), - working case
    ],
)
def test_three_deadlock_two_c1_c3_left_c2_forward(
    car1_road,
    car2_road,
    car3_road,
    car1_expected_road,
    car2_expected_road,
    car3_expected_road,
):
    actions = [
        (1, Action.LEFT),
        (2, Action.FORWARD),
        (3, Action.LEFT),
    ]

    map_state = basic_test_setup([car1_road, car2_road, car3_road])
    expected_roads = {
        (car1_expected_road, 1),
        (car2_expected_road, 2),
        (car3_expected_road, 3),
    }

    map_state.move_cars(actions)
    curr_pos = set([(map_state.get_cars()[k][0], k) for k in map_state.get_cars().keys()])

    assert (len(expected_roads.intersection(curr_pos)) >= 1), "cars did not move to their goal"
    update_actions_and_expected_pos(expected_roads, curr_pos, actions)

    map_state.move_cars(actions)

    curr_pos = set(
        [(map_state.get_cars()[k][0], k) for k in map_state.get_cars().keys()]
    )
    assert (
        len(expected_roads.intersection(curr_pos)) >= 1
    ), "car did not move to their goal"
    update_actions_and_expected_pos(expected_roads, curr_pos, actions)

    map_state.move_cars(actions)
    curr_pos = set(
        [(map_state.get_cars()[k][0], k) for k in map_state.get_cars().keys()]
    )
    assert (
        len(expected_roads.intersection(curr_pos)) == 1 or len(expected_roads) == 0
    ), "car did not move to their goal"


@pytest.mark.parametrize(
    "car1_road,car2_road,car3_road,car1_expected_road,car2_expected_road,car3_expected_road",
    [
        ((6, 7), (13, 7), (8, 7), (7, 13), (7, 1), (7, 13)),
        ((13, 7), (8, 7), (1, 7), (7, 8), (7, 6), (7, 8)),
    ],
)
def test_three_c1_right_c2_forward_c3_left_with_col(
    car1_road,
    car2_road,
    car3_road,
    car1_expected_road,
    car2_expected_road,
    car3_expected_road,
):
    """
    Tests check if cars moves in the correct order (1, 3, 2)
    """
    actions = [
        (1, Action.RIGHT),
        (2, Action.FORWARD),
        (3, Action.LEFT),
    ]

    map_state = basic_test_setup([car1_road, car2_road, car3_road])
    map_state.move_cars(actions)

    assert map_state._cars[1] == (car1_expected_road, 0)
    assert map_state._cars[2] == (car2_road, return_road_end(map_state, car2_road))
    assert map_state._cars[3] == (car3_road, return_road_end(map_state, car3_road))
    actions = [
        (1, Action.FORWARD),
        (2, Action.FORWARD),
        (3, Action.LEFT),
    ]
    map_state.move_cars(actions)
    assert map_state._cars[2] == (car2_road, return_road_end(map_state, car2_road))
    assert map_state._cars[3] == (car3_expected_road, 0)

    actions = [
        (1, Action.FORWARD),
        (2, Action.FORWARD),
        (3, Action.FORWARD),
    ]
    map_state.move_cars(actions)
    assert map_state._cars[2] == (car2_expected_road, 0)


@pytest.mark.parametrize(
    "car1_road,car2_road,car3_road,car1_expected_road,car2_expected_road,car3_expected_road",
    [
        ((13, 7), (8, 7), (6, 7), (7, 8), (7, 6), (7, 1)),
        ((8, 7), (1, 7), (13, 7), (7, 1), (7, 13), (7, 6)),
        ((6, 7), (13, 7), (1, 7), (7, 13), (7, 1), (7, 8)),
        ((1, 7), (6, 7), (8, 7), (7, 6), (7, 8), (7, 13)),
    ],
)
def test_three_c1_right_c2_forward_c3_left_with_col(
    car1_road,
    car2_road,
    car3_road,
    car1_expected_road,
    car2_expected_road,
    car3_expected_road,
):
    """
    Tests check case where car 1 and car 2 move in the same time and car 3 will move after them
    """
    actions = [
        (1, Action.RIGHT),
        (2, Action.FORWARD),
        (3, Action.LEFT),
    ]

    map_state = basic_test_setup([car1_road, car2_road, car3_road])
    map_state.move_cars(actions)

    assert map_state._cars[1] == (car1_expected_road, 0)
    assert map_state._cars[2] == (car2_expected_road, 0)
    assert map_state._cars[3] == (car3_road, return_road_end(map_state, car3_road))
    actions = [
        (1, Action.FORWARD),
        (2, Action.FORWARD),
        (3, Action.LEFT),
    ]
    map_state.move_cars(actions)
    assert map_state._cars[3] == (car3_expected_road, 0)


if __name__ == "__main__":

    unittest.main()
