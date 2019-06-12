import pytest
import os

from main import *
from parser import validate_signature

INPUT_DATA = "stdin_test_data"
RESULTS = "stdout_test_results"


def load_test_data(f_name, input_data):
    data = []
    path = os.path.join(os.getcwd(), input_data, f_name)
    with open(path, 'r') as f:
        for line in f:
            if line.startswith("{"):
                data.append(line)
    return [line.replace('\n', "") for line in data]


NEGATIVE_INIT = load_test_data('1_negative_init.json', INPUT_DATA), load_test_data('1.json', RESULTS)
POSITIVE_INIT = list(zip(load_test_data('2_positive_init.json', INPUT_DATA)[1:], load_test_data('2.json', RESULTS)[1:]))
CALLS = list(zip(load_test_data('3_positive_calls.json', INPUT_DATA)[1:], load_test_data('3.json', RESULTS)[1:])) \
      + list(zip(load_test_data('4_negative_calls.json', INPUT_DATA)[1:], load_test_data('4.json', RESULTS)[1:])) \
      + list(zip(load_test_data('5_active_calls.json', INPUT_DATA)[1:], load_test_data('5.json', RESULTS)[1:]))

ARGUMENTS = list(zip(load_test_data('6_argument_wrong_number.json', INPUT_DATA)[1:], load_test_data('6.json', RESULTS)[1:]))

def test_negative_init():
    reset()
    _, result = run_open(NEGATIVE_INIT[0][0])
    assert result == NEGATIVE_INIT[1][0]


@pytest.mark.parametrize('tcs', POSITIVE_INIT)
def test_positive_init(tcs):
    api = Api({"database": "student", "login": "init", "password": "qwerty"})
    conn, curr = api.get_connection_and_cursor()
    load_sql_into_db(conn, curr)
    command, params = parse_json_object(tcs[0])
    result = run_api_function(api, command=command, params=params)
    reset()
    assert result == tcs[1]


@pytest.mark.parametrize('tcs', CALLS)
def test_calls(prepare_database, tcs):
    command, params = parse_json_object(tcs[0])
    try:
        result = run_api_function(prepare_database, command=command, params=params)
        assert result == tcs[1]
    except CustomException as e:
        assert '{' + '"status": "ERROR", "debug": "{msg}"'.format(msg=e.msg) + '}' == tcs[1]


@pytest.mark.parametrize('tcs', ARGUMENTS)
def test_argument_wrong_number(tcs):
    try:
        command, params = parse_json_object(tcs[0])
        assert False
    except ArgumentError as e:
        assert '{' + '"status": "ERROR", "debug": "{msg}"'.format(msg=e.msg) + '}' == tcs[1]


@pytest.fixture(scope="module")
def prepare_database():
    api = Api({"database": "student", "login": "init", "password": "qwerty"})
    conn, curr = api.get_connection_and_cursor()
    load_sql_into_db(conn, curr)
    for tcs in POSITIVE_INIT:
        command, params = parse_json_object(tcs[0])
        _ = run_api_function(api, command=command, params=params)
    api = Api({"database": "student", "login": "init", "password": "qwerty"})
    return api

