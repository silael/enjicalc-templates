import sys, os
import pytest
from math import pi, tau

sys.path.append(
    os.path.join(os.getcwd(), 'src')
)
from ast_evaluator import evaluate_formula, FormulaSyntaxError, FormulaRuntimeError

def test_single_formula():
    assert round(evaluate_formula("a * b / c", {"a": 1.0, "b": 3, "c": 91, "unused": 100}), 2) == 0.03

def test_negative_test():
    assert evaluate_formula("a * b / c", {"a": 1.0, "b": 3, "c": 91}) != 0.03

def test_formula_error():
    with pytest.raises(FormulaSyntaxError):
        evaluate_formula("''", {})

TEST_CASES = [
    (("a ? pi : tau", {'a': 1}), pi), 
    (("a ? pi : tau", {'a': 0}), tau), 
    (("f_cm <= 35 ? 1 : 0",  {'f_cm': 35}), 1), 
    (("f_cm == 35 ? 1 : 0",  {'f_cm': 35}), 1), 
    (("f_cm >= 35 ? 1 : 0",  {'f_cm': 35}), 1), 
    (("f_cm != 35 ? 1 : 0",  {'f_cm': 35}), 0), 
    (("f_cm < 35 ? 1 : 0",  {'f_cm': 35}), 0), 
    (("f_cm > 35 ? 1 : 0",  {'f_cm': 35}), 0), 
    (("1 ? True : 0", {}) , 1),
    (("min(a,b)", {"a":2 , "b": 3}), 2), 
    (("ceil(tan(radians(a)))", {'a': 45}), 1),
    (("0" * 5, {}), 0),  # NOTE the following cant be defined in JSON 
    (("3^2", {}), 9),
    (("1 + 2 + 3^2", {}), 12),
    (("y004Ip90T", {"y004Ip90T":2}), 2),
    (("2", {}), 2),
    (("2.0", {}), 2),
    (("2e-1", {}), 0.2),
    (("1 + 2 * (3.0 / 4.0)", {}), 2.5), 
    (("1 - 2 * (3.0 / 4.0)", {}), -0.5), 
    (("a * b / c", {"a": 1.0, "b": 3, "c": 91}), 0.03296703296703297),
    (("(points - 100 * bans) / gamesPlayed", {"points": 1200, "bans": 3, "gamesPlayed": 23}), 39.130434782608695)
]

@pytest.mark.parametrize("test_input, expected", TEST_CASES)
def test_cases(test_input, expected):
    assert evaluate_formula(*test_input) == expected

TEST_FAIL_CASES = [
    (("2", {}), 3),
    (("2.0", {}), 1),
    (("2e-1", {}), 0.3),
    (("1 + 2 * (3.0 / 4.0)", {}), 1.5), 
    (("a * b / c", {"a": 1.0, "b": 3, "c": 91}), 0.03),
    (("(points - 100 * bans) / gamesPlayed", {"points": 1200, "bans": 3, "gamesPlayed": 23}), 39.13)
]

@pytest.mark.parametrize("test_input, expected", TEST_FAIL_CASES)
def test_failcases(test_input, expected):
    assert evaluate_formula(*test_input) != expected

TEST_CASES_ERRORS = [
    (("1 if True else 0", {}), FormulaSyntaxError), 
    (("1 ** 2", {}), FormulaSyntaxError), 
    (("1 // 2", {}), FormulaSyntaxError),
    (("''", {}), FormulaSyntaxError),
    (("not 2", {}), FormulaSyntaxError),
    (("und", {}), FormulaSyntaxError),
    (("and and", {}), FormulaSyntaxError),
    (("0" * 256, {}), FormulaSyntaxError),  
    (("lambda a:" * 28, {}), FormulaSyntaxError),
    (("a", {1}), FormulaRuntimeError),
    (("1/0", {}), FormulaRuntimeError)
]

@pytest.mark.parametrize("test_input, expected", TEST_CASES_ERRORS)
def test_error_cases(test_input, expected):
    with pytest.raises(expected):
        evaluate_formula(*test_input)

TEST_CASES_CALL = [
    (("min(1,2)", {}) , 1),
    (("max(a,b)", {'a': 10, 'b': 20}) , 20),
    (("cos(a)", {'a': 0}) , 1),
    (("cos(a) + 1", {'a': 0}) , 2),
    (("sin(radians(a))", {'a': 90}) , 1),
]

@pytest.mark.parametrize("test_input, expected", TEST_CASES_CALL)
def test_eval_call(test_input, expected):
    assert evaluate_formula(*test_input) == expected
