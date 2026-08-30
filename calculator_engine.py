"""
Calculator Engine - Safe AST-based Mathematical Expression Evaluator
Supports basic arithmetic, scientific functions, trigonometry, constants, memory, and calculation history.
"""

import ast
import math
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union


class CalculationError(Exception):
    """Custom exception class for calculator evaluation errors."""
    pass


class CalculatorEngine:
    """Safe mathematical expression evaluator and state manager."""

    def __init__(self, angle_mode: str = "DEG"):
        """
        Initialize calculator engine.
        :param angle_mode: 'DEG' for degrees or 'RAD' for radians.
        """
        self.angle_mode = angle_mode.upper() if angle_mode.upper() in ("DEG", "RAD") else "DEG"
        self.memory: float = 0.0
        self.last_result: Optional[float] = None
        self.history: List[Dict[str, Any]] = []

    def set_angle_mode(self, mode: str) -> str:
        """Set angle mode to 'DEG' or 'RAD'."""
        mode = mode.upper()
        if mode in ("DEG", "RAD"):
            self.angle_mode = mode
            return self.angle_mode
        raise CalculationError("Angle mode must be 'DEG' or 'RAD'.")

    def toggle_angle_mode(self) -> str:
        """Toggle angle mode between DEG and RAD."""
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        return self.angle_mode

    # ------------------ Memory Operations ------------------ #

    def memory_clear(self) -> float:
        """MC: Clear memory."""
        self.memory = 0.0
        return self.memory

    def memory_recall(self) -> float:
        """MR: Recall value from memory."""
        return self.memory

    def memory_store(self, value: Union[int, float]) -> float:
        """MS: Store value into memory."""
        self.memory = float(value)
        return self.memory

    def memory_add(self, value: Union[int, float]) -> float:
        """M+: Add value to memory."""
        self.memory += float(value)
        return self.memory

    def memory_subtract(self, value: Union[int, float]) -> float:
        """M-: Subtract value from memory."""
        self.memory -= float(value)
        return self.memory

    # ------------------ History Operations ------------------ #

    def get_history(self) -> List[Dict[str, Any]]:
        """Return the calculation history."""
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear all calculation history."""
        self.history.clear()

    # ------------------ Trigonometric Wrappers ------------------ #

    def _sin(self, x: float) -> float:
        val = math.radians(x) if self.angle_mode == "DEG" else x
        res = math.sin(val)
        return 0.0 if abs(res) < 1e-15 else res

    def _cos(self, x: float) -> float:
        val = math.radians(x) if self.angle_mode == "DEG" else x
        res = math.cos(val)
        return 0.0 if abs(res) < 1e-15 else res

    def _tan(self, x: float) -> float:
        val = math.radians(x) if self.angle_mode == "DEG" else x
        # Check for undefined tan at 90 + 180k degrees
        if self.angle_mode == "DEG" and abs(x % 180 - 90) < 1e-9:
            raise CalculationError("tan() is undefined for this angle")
        res = math.tan(val)
        return 0.0 if abs(res) < 1e-15 else res

    def _asin(self, x: float) -> float:
        if not -1.0 <= x <= 1.0:
            raise CalculationError("asin domain error: input must be in [-1, 1]")
        res = math.asin(x)
        return math.degrees(res) if self.angle_mode == "DEG" else res

    def _acos(self, x: float) -> float:
        if not -1.0 <= x <= 1.0:
            raise CalculationError("acos domain error: input must be in [-1, 1]")
        res = math.acos(x)
        return math.degrees(res) if self.angle_mode == "DEG" else res

    def _atan(self, x: float) -> float:
        res = math.atan(x)
        return math.degrees(res) if self.angle_mode == "DEG" else res

    def _log(self, x: float, base: float = 10.0) -> float:
        if x <= 0:
            raise CalculationError("log domain error: input must be > 0")
        if base <= 0 or base == 1:
            raise CalculationError("log base must be > 0 and != 1")
        return math.log(x, base)

    def _ln(self, x: float) -> float:
        if x <= 0:
            raise CalculationError("ln domain error: input must be > 0")
        return math.log(x)

    def _sqrt(self, x: float) -> float:
        if x < 0:
            raise CalculationError("sqrt domain error: cannot compute square root of negative number")
        return math.sqrt(x)

    def _cbrt(self, x: float) -> float:
        if x < 0:
            return -((-x) ** (1.0 / 3.0))
        return x ** (1.0 / 3.0)

    def _factorial(self, x: float) -> int:
        if not float(x).is_integer() or x < 0:
            raise CalculationError("factorial error: input must be a non-negative integer")
        if x > 1000:
            raise CalculationError("factorial overflow: input too large (max 1000)")
        return math.factorial(int(x))

    # ------------------ Environment Mapping ------------------ #

    def _get_symbols(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Return allowed constants and functions."""
        constants = {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "ans": self.last_result if self.last_result is not None else 0.0,
        }

        functions = {
            "sin": self._sin,
            "cos": self._cos,
            "tan": self._tan,
            "asin": self._asin,
            "acos": self._acos,
            "atan": self._atan,
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "sqrt": self._sqrt,
            "cbrt": self._cbrt,
            "log": lambda x, b=10.0: self._log(x, b),
            "log10": lambda x: self._log(x, 10.0),
            "log2": lambda x: self._log(x, 2.0),
            "ln": self._ln,
            "exp": math.exp,
            "abs": abs,
            "fact": self._factorial,
            "factorial": self._factorial,
            "floor": math.floor,
            "ceil": math.ceil,
            "round": round,
            "rad": math.radians,
            "deg": math.degrees,
        }
        return constants, functions

    # ------------------ Preprocessing ------------------ #

    def preprocess_expression(self, expr: str) -> str:
        """Clean and normalize mathematical expression for AST parsing."""
        if not expr or not expr.strip():
            raise CalculationError("Expression cannot be empty.")

        cleaned = expr.strip()

        # Replace Unicode multiplication & division symbols
        cleaned = cleaned.replace("×", "*").replace("÷", "/")
        cleaned = cleaned.replace("−", "-").replace("—", "-")
        cleaned = cleaned.replace("π", "pi")

        # Convert power symbol ^ to **
        cleaned = cleaned.replace("^", "**")

        # Convert factorial postfix e.g. 5! or (3+2)! -> fact(5) or fact((3+2))
        # Handle simple number factorials e.g. 5!
        fact_pattern = re.compile(r"(\d+(?:\.\d+)?|\([^\(\)]+\))!")
        while "!" in cleaned:
            match = fact_pattern.search(cleaned)
            if not match:
                break
            target = match.group(1)
            cleaned = cleaned[:match.start()] + f"fact({target})" + cleaned[match.end():]

        # Convert percentage postfix e.g. 50% -> (50/100)
        pct_pattern = re.compile(r"(\d+(?:\.\d+)?|\([^\(\)]+\))%")
        while "%" in cleaned:
            # Check if % is used as modulo vs percentage
            # If immediately followed by number or identifier, it might be modulo, but postfix % is percentage
            match = pct_pattern.search(cleaned)
            if not match:
                break
            target = match.group(1)
            cleaned = cleaned[:match.start()] + f"({target}/100)" + cleaned[match.end():]

        # Handle implicit multiplication carefully without breaking function names like log10, log2
        # 1. Standalone number before parenthesis: 2(3) -> 2*(3), but not log10(100)
        cleaned = re.sub(r"\b(\d+(?:\.\d+)?)\s*\(", r"\1*(", cleaned)

        # 2. Parenthesis before parenthesis: (2)(3) -> (2)*(3)
        cleaned = re.sub(r"\)\s*\(", r")*(", cleaned)

        # 3. Parenthesis before number: (2)3 -> (2)*3
        cleaned = re.sub(r"\)\s*(\d+(?:\.\d+)?)", r")*\1", cleaned)

        # 4. Parenthesis before function/constant: (2)sin(30) -> (2)*sin(30), (2)pi -> (2)*pi
        cleaned = re.sub(r"\)\s*([a-zA-Z_])", r")*\1", cleaned)

        # 5. Standalone number before function or constant: 2pi -> 2*pi, 2sin(x) -> 2*sin(x)
        cleaned = re.sub(r"\b(\d+(?:\.\d+)?)\s*(pi|tau|ans|sin|cos|tan|asin|acos|atan|sinh|cosh|tanh|sqrt|cbrt|log|log10|log2|ln|exp|abs|fact|factorial|rad|deg)\b", r"\1*\2", cleaned)

        # 6. Constant before parenthesis: pi(2) -> pi*(2)
        cleaned = re.sub(r"\b(pi|e|tau|ans)\s*\(", r"\1*(", cleaned)

        return cleaned

    # ------------------ AST Evaluator ------------------ #

    def _eval_node(self, node: ast.AST, constants: Dict[str, Any], functions: Dict[str, Any]) -> Any:
        """Recursively evaluate an AST node safely."""
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body, constants, functions)

        # Numbers / Literals (Python 3.8+ uses ast.Constant)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise CalculationError(f"Unsupported constant type: {type(node.value).__name__}")

        # Identifiers (Constants or Variables)
        if isinstance(node, ast.Name):
            if node.id in constants:
                return constants[node.id]
            if node.id in functions:
                return functions[node.id]
            raise CalculationError(f"Unknown symbol: '{node.id}'")

        # Unary operations (+x, -x)
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, constants, functions)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise CalculationError(f"Unsupported unary operator: {type(node.op).__name__}")

        # Binary operations (x + y, x - y, x * y, x / y, etc.)
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, constants, functions)
            right = self._eval_node(node.right, constants, functions)

            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise CalculationError("Division by zero")
                return left / right
            if isinstance(node.op, ast.FloorDiv):
                if right == 0:
                    raise CalculationError("Division by zero in floor division")
                return left // right
            if isinstance(node.op, ast.Mod):
                if right == 0:
                    raise CalculationError("Division by zero in modulo")
                return left % right
            if isinstance(node.op, ast.Pow):
                # Safety check for massive exponents
                if isinstance(right, (int, float)) and (right > 10000 or (left > 100 and right > 100)):
                    raise CalculationError("Result too large (exponent overflow protection)")
                try:
                    res = left ** right
                    if isinstance(res, complex):
                        raise CalculationError("Complex results are not supported in real mode")
                    return res
                except OverflowError:
                    raise CalculationError("Exponent overflow: number too large")

            raise CalculationError(f"Unsupported binary operator: {type(node.op).__name__}")

        # Function Calls e.g. sin(30), sqrt(16), log(100, 10)
        if isinstance(node, ast.Call):
            func = self._eval_node(node.func, constants, functions)
            if not callable(func):
                raise CalculationError(f"Expression is not callable: {ast.unparse(node.func) if hasattr(ast, 'unparse') else 'function'}")

            args = [self._eval_node(arg, constants, functions) for arg in node.args]
            kwargs = {kw.arg: self._eval_node(kw.value, constants, functions) for kw in node.keywords if kw.arg}

            try:
                return func(*args, **kwargs)
            except CalculationError:
                raise
            except Exception as e:
                raise CalculationError(f"Function error: {str(e)}")

        raise CalculationError(f"Unsupported expression syntax: {type(node).__name__}")

    # ------------------ Main Evaluate Method ------------------ #

    def evaluate(self, expression: str) -> Union[int, float]:
        """
        Safely evaluate a mathematical expression string.
        :param expression: The math expression to evaluate.
        :return: Computed numeric result (int or float).
        """
        preprocessed = self.preprocess_expression(expression)

        try:
            tree = ast.parse(preprocessed, mode="eval")
        except SyntaxError as e:
            raise CalculationError(f"Syntax error in expression: {str(e)}")

        constants, functions = self._get_symbols()
        raw_result = self._eval_node(tree, constants, functions)

        if not isinstance(raw_result, (int, float)):
            raise CalculationError("Evaluation did not result in a numeric value.")

        # Clean float precision artifacts (e.g. 0.1 + 0.2 -> 0.3)
        if isinstance(raw_result, float):
            if raw_result.is_integer():
                result: Union[int, float] = int(raw_result)
            else:
                # Round to 12 decimal places to avoid standard IEEE 754 precision drift
                result = round(raw_result, 12)
        else:
            result = raw_result

        # Update engine state
        self.last_result = float(result)
        self.history.append({
            "expression": expression.strip(),
            "preprocessed": preprocessed,
            "result": result,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        })

        return result

    @staticmethod
    def format_number(val: Union[int, float], max_decimals: int = 8) -> str:
        """Format number nicely for UI display."""
        if isinstance(val, (int, float)):
            if abs(val) >= 1e12 or (0 < abs(val) < 1e-6):
                return f"{val:.6e}"
            if isinstance(val, float) and val.is_integer():
                return str(int(val))
            formatted = f"{round(val, max_decimals):.{max_decimals}f}".rstrip('0').rstrip('.')
            return formatted
        return str(val)
