"""
The following code was taken and modified from the following source 
https://blog.oyam.dev/python-formulas/
"""
import ast
import operator
import math
from typing import Any, Dict


def byte_offset_to_char_offset(source: str, byte_offset: int) -> int:
    while True:
        try:
            pre_source = source.encode()[:byte_offset].decode()
            break
        except UnicodeDecodeError:
            byte_offset -= 1
            continue
    return len(pre_source)


class FormulaError(Exception):
    pass


class FormulaSyntaxError(FormulaError):
    def __init__(self, msg: str, lineno: int, offset: int):
        self.msg = msg
        self.lineno = lineno
        self.offset = offset

    @classmethod
    def from_ast_node(cls, source: str, node: ast.AST, msg: str) -> "FormulaSyntaxError":
        lineno = node.lineno
        col_offset = node.col_offset
        offset = byte_offset_to_char_offset(source, col_offset)
        return cls(msg=msg, lineno=lineno, offset=offset + 1)

    @classmethod
    def from_syntax_error(cls, error: SyntaxError, msg: str) -> "FormulaSyntaxError":
        return cls(msg=f"{msg}: {error.msg}", lineno=error.lineno, offset=error.offset)

    def __str__(self):
        return f"{self.lineno}:{self.offset}: {self.msg}"


class FormulaRuntimeError(FormulaError):
    pass


def evaluate_formula(formula: str, vars: Dict[str, Any]) -> float:
    MAX_FORMULA_LENGTH = 255
    
    if len(formula) > MAX_FORMULA_LENGTH:
        raise FormulaSyntaxError(f"The formula is too long: {formula}", 1, 1)

    if ('if' or 'else') in formula:
        raise FormulaSyntaxError(f"Invalid ternary expression: {formula}. Use JS notation 'condition ? expr_if_true : expr_if_false'", 1, 1)

    #NOTE JS turnery expression converted to python type
    if ('?' and ':') in formula:
        formula = formula.replace('?', ' if ')
        formula = formula.replace(':', ' else ')


    #NOTE changing from JS/scientific notation to python notation
    if '**' in formula: 
        raise FormulaSyntaxError(f"Invalid power expression: {formula}. Use JS/scientific notation '^' for the power notation", 1, 1)
    formula = formula.replace('^', '**')

    try:
        node = ast.parse(formula, "<string>", mode="eval")
    except SyntaxError as e:
        raise FormulaSyntaxError.from_syntax_error(e, "Could not parse")

    try:
        return __eval_node(formula, node, vars)
    except FormulaSyntaxError:
        raise
    except Exception as e:
        raise FormulaRuntimeError(f"Evaluation failed: {e}")


def __eval_node(source: str, node: ast.AST, vars: Dict[str, Any]) -> float:
    EVALUATORS = {
        ast.Expression: __eval_expression,
        ast.Constant: __eval_constant,
        ast.Name: __eval_name,
        ast.BinOp: __eval_binop,
        ast.UnaryOp: __eval_unaryop,
        ast.Compare: __eval_compare,
        ast.Call: __eval_call, 
        ast.IfExp: __eval_ifexp, 
    }

    for ast_type, evaluator in EVALUATORS.items():
        if isinstance(node, ast_type):
            return evaluator(source, node, vars)

    raise FormulaSyntaxError.from_ast_node(source, node, "This syntax is not supported")


def __eval_expression(source: str, node: ast.Expression, vars: Dict[str, Any]) -> float:
    return __eval_node(source, node.body, vars)


def __eval_constant(source: str, node: ast.Constant, vars: Dict[str, Any]) -> float:
    if isinstance(node.value, int) or isinstance(node.value, float):
        return float(node.value)
    else:
        raise FormulaSyntaxError.from_ast_node(source, node, "Literals of this type are not supported")


def __eval_name(source: str, node: ast.Name, vars: Dict[str, Any]) -> float:
    constants = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
    }

    if node.id in constants:
        return float(constants[node.id])

    try:
        return float(vars[node.id])
    except KeyError:
        raise FormulaSyntaxError.from_ast_node(source, node, f"Undefined variable: {node.id}")


def __eval_binop(source: str, node: ast.BinOp, vars: Dict[str, Any]) -> float:
    OPERATIONS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow, 
    }

    left_value = __eval_node(source, node.left, vars)
    right_value = __eval_node(source, node.right, vars)

    try:
        apply = OPERATIONS[type(node.op)]
    except KeyError:
        raise FormulaSyntaxError.from_ast_node(source, node, "Operations of this type are not supported")

    return apply(left_value, right_value)


def __eval_unaryop(source: str, node: ast.UnaryOp, vars: Dict[str, Any]) -> float:
    OPERATIONS = {
        ast.USub: operator.neg,
    }

    operand_value = __eval_node(source, node.operand, vars)

    try:
        apply = OPERATIONS[type(node.op)]
    except KeyError:
        raise FormulaSyntaxError.from_ast_node(source, node, "Operations of this type are not supported")

    return apply(operand_value)


def __eval_call(source: str, node: ast.Call, vars: Dict[str, Any]) -> float:
    #NOTE other custom functions can be developed
    FUNCTIONS = {
        'acos': math.acos,
        'acosh': math.acosh,
        'asin': math.asin,
        'asinh': math.asinh,
        'atan':  math.atan,
        'atan2':  math.atan2,
        'atanh':  math.atanh,
        'ceil':  math.ceil,
        'copysign': math.copysign,
        'cos': math.cos,
        'cosh':  math.cosh,
        'degrees':  math.degrees,
        'dist':  math.dist,
        'exp':  math.exp,
        'factorial':  math.factorial,
        'floor':  math.floor,
        'fmod':  math.fmod,
        'isclose':  math.isclose,
        'isfinite':  math.isfinite,
        'log':  math.log,
        'log10':  math.log10,
        'log2':  math.log2,
        'radians': math.radians,
        'remainder':  math.remainder,
        'sin':  math.sin,
        'sinh':  math.sinh,
        'sqrt':  math.sqrt,
        'tan':  math.tan,
        'tanh':  math.tanh,
        'abs': abs,
        'min':  min,
        'max':  max,
    }

    function_input = []
    for args in node.args:
        function_input.append(__eval_node(source, args, vars))

    try: 
        apply = FUNCTIONS[node.func.id]
    except BaseException: 
        raise FormulaSyntaxError.from_ast_node(source, node, "Functions of this type are not supported")

    return apply(*function_input)
    

def __eval_ifexp(source: str, node: ast.IfExp, vars: Dict[str, Any]) -> float:
    """
    condition = node.body
    expr_if_true = node.test
    The statement above is correct and is coming from the fact that turnery expressions in JS and Python are different: 

    Python:     expr_if_true if condition else expr_if_false
    JS:         condition ?  expr_if_true : else expr_if_false

    JS seems to be a prefferable option as it is also mimicking Excel formula 
    =IF(condition , expr_if_true, expr_if_false)
    """
    condition = __eval_node(source, node.body, vars)
    expr_if_true = __eval_node(source, node.test, vars)
    expr_if_false = __eval_node(source, node.orelse, vars)

    if condition:
        return float(expr_if_true)
    else:
        return float(expr_if_false)

def __eval_compare(source: str, node: ast.Compare, vars: Dict[str, Any]) -> float:
    """
    need sequences for compare to distinguish between 
    x < 4 < 3 and (x < 4) < 3

    see: https://docs.python.org/3/library/ast.html
    """
    CMPOP = {
        ast.Eq : operator.eq,
        ast.NotEq : operator.ne , 
        ast.Lt : operator.lt , 
        ast.LtE : operator.le , 
        ast.Gt : operator.gt , 
        ast.GtE : operator.ge , 
    }

    left = __eval_node(source, node.left, vars)
    ops_list = node.ops
    comparators = node.comparators

    evaluated_comparators = []
    for comparator in comparators:
        evaluated_comparators.append(__eval_node(source, comparator, vars))

    try:
        for i in range(len(evaluated_comparators)):
            apply = CMPOP[type(ops_list[i])]
            left = apply(left, evaluated_comparators[i])
    except KeyError:
        raise FormulaSyntaxError.from_ast_node(source, node, "Operations of this type are not supported")

    return float(left)