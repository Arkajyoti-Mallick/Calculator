"""
Unit Test Suite for Python Calculator Engine
Tests arithmetic operations, precedence, scientific functions, trigonometry, memory, and error handling.
"""

import math
import unittest
from calculator_engine import CalculatorEngine, CalculationError


class TestCalculatorEngine(unittest.TestCase):

    def setUp(self):
        self.engine = CalculatorEngine(angle_mode="DEG")

    # ------------------ Basic Arithmetic Tests ------------------ #

    def test_basic_addition(self):
        self.assertEqual(self.engine.evaluate("2 + 3"), 5)
        self.assertEqual(self.engine.evaluate("10.5 + 4.5"), 15)
        self.assertEqual(self.engine.evaluate("-5 + 12"), 7)

    def test_basic_subtraction(self):
        self.assertEqual(self.engine.evaluate("10 - 4"), 6)
        self.assertEqual(self.engine.evaluate("4 - 10"), -6)
        self.assertEqual(self.engine.evaluate("3.5 - 1.2"), 2.3)

    def test_multiplication_and_division(self):
        self.assertEqual(self.engine.evaluate("6 * 7"), 42)
        self.assertEqual(self.engine.evaluate("6 × 7"), 42)
        self.assertEqual(self.engine.evaluate("84 / 2"), 42)
        self.assertEqual(self.engine.evaluate("84 ÷ 2"), 42)
        self.assertEqual(self.engine.evaluate("15 // 4"), 3)
        self.assertEqual(self.engine.evaluate("15 % 4"), 3)

    def test_operator_precedence(self):
        self.assertEqual(self.engine.evaluate("2 + 3 * 4"), 14)
        self.assertEqual(self.engine.evaluate("(2 + 3) * 4"), 20)
        self.assertEqual(self.engine.evaluate("10 - 2 * 3 + 4 / 2"), 6)
        self.assertEqual(self.engine.evaluate("2 ^ 3 * 2"), 16)
        self.assertEqual(self.engine.evaluate("2 ** 3 + 1"), 9)

    def test_implicit_multiplication(self):
        self.assertEqual(self.engine.evaluate("2(3 + 4)"), 14)
        self.assertEqual(self.engine.evaluate("(2)(3)"), 6)
        self.assertEqual(self.engine.evaluate("3(4)"), 12)

    def test_percentage_and_factorial(self):
        self.assertEqual(self.engine.evaluate("50%"), 0.5)
        self.assertEqual(self.engine.evaluate("200 * 15%"), 30)
        self.assertEqual(self.engine.evaluate("5!"), 120)
        self.assertEqual(self.engine.evaluate("0!"), 1)
        self.assertEqual(self.engine.evaluate("(3 + 2)!"), 120)

    # ------------------ Scientific & Trigonometric Tests ------------------ #

    def test_trigonometry_degrees(self):
        self.assertEqual(self.engine.evaluate("sin(0)"), 0)
        self.assertEqual(self.engine.evaluate("sin(30)"), 0.5)
        self.assertEqual(self.engine.evaluate("sin(90)"), 1)
        self.assertEqual(self.engine.evaluate("cos(0)"), 1)
        self.assertEqual(self.engine.evaluate("cos(60)"), 0.5)
        self.assertEqual(self.engine.evaluate("cos(90)"), 0)
        self.assertEqual(self.engine.evaluate("tan(45)"), 1)

    def test_trigonometry_radians(self):
        self.engine.set_angle_mode("RAD")
        self.assertEqual(self.engine.evaluate("sin(0)"), 0)
        self.assertAlmostEqual(self.engine.evaluate("sin(pi / 2)"), 1.0, places=7)
        self.assertAlmostEqual(self.engine.evaluate("cos(pi)"), -1.0, places=7)

    def test_hyperbolic_functions(self):
        self.assertEqual(self.engine.evaluate("sinh(0)"), 0)
        self.assertEqual(self.engine.evaluate("cosh(0)"), 1)
        self.assertEqual(self.engine.evaluate("tanh(0)"), 0)

    def test_inverse_trig(self):
        self.assertEqual(self.engine.evaluate("asin(1)"), 90)
        self.assertEqual(self.engine.evaluate("acos(1)"), 0)
        self.assertEqual(self.engine.evaluate("atan(1)"), 45)

    def test_powers_roots_logs(self):
        self.assertEqual(self.engine.evaluate("sqrt(144)"), 12)
        self.assertEqual(self.engine.evaluate("cbrt(27)"), 3)
        self.assertEqual(self.engine.evaluate("cbrt(-27)"), -3)
        self.assertEqual(self.engine.evaluate("log(100)"), 2)
        self.assertEqual(self.engine.evaluate("log10(1000)"), 3)
        self.assertEqual(self.engine.evaluate("log2(8)"), 3)
        self.assertAlmostEqual(self.engine.evaluate("ln(e)"), 1.0, places=7)
        self.assertEqual(self.engine.evaluate("abs(-42)"), 42)
        self.assertEqual(self.engine.evaluate("floor(4.9)"), 4)
        self.assertEqual(self.engine.evaluate("ceil(4.1)"), 5)
        self.assertEqual(self.engine.evaluate("round(4.6)"), 5)

    def test_constants(self):
        self.assertAlmostEqual(self.engine.evaluate("pi"), math.pi, places=7)
        self.assertAlmostEqual(self.engine.evaluate("e"), math.e, places=7)
        self.assertAlmostEqual(self.engine.evaluate("tau"), math.tau, places=7)

    def test_nested_complex_expressions(self):
        expr = "sqrt(3^2 + 4^2) + sin(30) * 10"
        self.assertEqual(self.engine.evaluate(expr), 10.0)

    def test_number_formatting(self):
        self.assertEqual(CalculatorEngine.format_number(5.0), "5")
        self.assertEqual(CalculatorEngine.format_number(5.123456789), "5.12345679")
        self.assertEqual(CalculatorEngine.format_number(1e15), "1.000000e+15")

    # ------------------ Memory and State Tests ------------------ #

    def test_memory_operations(self):
        self.assertEqual(self.engine.memory_store(50), 50.0)
        self.assertEqual(self.engine.memory_recall(), 50.0)
        self.assertEqual(self.engine.memory_add(25), 75.0)
        self.assertEqual(self.engine.memory_subtract(15), 60.0)
        self.assertEqual(self.engine.memory_clear(), 0.0)
        self.assertEqual(self.engine.memory_recall(), 0.0)

    def test_history_and_ans(self):
        self.engine.evaluate("10 + 20")
        self.assertEqual(self.engine.last_result, 30)
        self.assertEqual(self.engine.evaluate("ans * 2"), 60)
        history = self.engine.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["expression"], "10 + 20")
        self.assertEqual(history[0]["result"], 30)
        self.assertEqual(history[1]["expression"], "ans * 2")
        self.assertEqual(history[1]["result"], 60)

    # ------------------ Error Handling & Security Tests ------------------ #

    def test_division_by_zero(self):
        with self.assertRaises(CalculationError):
            self.engine.evaluate("10 / 0")
        with self.assertRaises(CalculationError):
            self.engine.evaluate("10 // 0")
        with self.assertRaises(CalculationError):
            self.engine.evaluate("10 % 0")

    def test_domain_errors(self):
        with self.assertRaises(CalculationError):
            self.engine.evaluate("sqrt(-1)")
        with self.assertRaises(CalculationError):
            self.engine.evaluate("log(-10)")
        with self.assertRaises(CalculationError):
            self.engine.evaluate("asin(2)")

    def test_syntax_errors(self):
        with self.assertRaises(CalculationError):
            self.engine.evaluate("2 ++ 3 *")
        with self.assertRaises(CalculationError):
            self.engine.evaluate("(2 + 3")
        with self.assertRaises(CalculationError):
            self.engine.evaluate("")

    def test_security_disallowed_code(self):
        # Ensure arbitrary python functions or attributes cannot be executed
        with self.assertRaises(CalculationError):
            self.engine.evaluate("__import__('os').system('dir')")
        with self.assertRaises(CalculationError):
            self.engine.evaluate("open('test.txt', 'w')")
        with self.assertRaises(CalculationError):
            self.engine.evaluate("[x for x in range(10)]")


if __name__ == "__main__":
    unittest.main()
