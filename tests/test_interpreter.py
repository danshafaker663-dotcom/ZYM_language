"""End-to-end tests for the ZYM tree-walking interpreter."""

from io import StringIO
from pathlib import Path
import random
import unittest

from zym.errors import SemanticError, ZymRuntimeError
from zym.interpreter import Interpreter
from zym.lexer import Lexer
from zym.parser import Parser


def run_source(source: str, input_text: str = "") -> tuple[str, Interpreter]:
    filename = "interpreter_test.zym"
    program = Parser(Lexer(source, filename).scan_tokens(), filename).parse()
    output = StringIO()
    interpreter = Interpreter(
        filename=filename,
        input_stream=StringIO(input_text),
        output_stream=output,
        random_source=random.Random(7),
    )
    interpreter.interpret(program)
    return output.getvalue(), interpreter


class InterpreterTests(unittest.TestCase):
    def test_arithmetic_string_and_boolean_expressions(self) -> None:
        output, _ = run_source(
            """
            output 1 + 2 * 3.
            output -7 / 3.
            output -7 % 3.
            output "ZY" + "M".
            output true and not false.
            output 1 == true.
            """
        )
        self.assertEqual(output, "7\n-2\n-1\nZYM\ntrue\nfalse\n")

    def test_variable_assignment_and_block_shadowing(self) -> None:
        output, _ = run_source(
            """
            set value := 1.
            {
                set value := 2.
                output value.
            }
            value := value + 4.
            output value.
            """
        )
        self.assertEqual(output, "2\n5\n")

    def test_array_index_assignment_and_builtins(self) -> None:
        output, _ = run_source(
            """
            set values := [10, 20].
            values[0] := 11.
            push(values, 30).
            output values.
            output pop(values).
            output length(values).
            output typeOf(values).
            """
        )
        self.assertEqual(output, "[11, 20, 30]\n30\n2\narray\n")

    def test_structure_creation_field_access_and_assignment(self) -> None:
        output, _ = run_source(
            """
            declare Point { x, y }.
            set point := Point { y: 2, x: 1 }.
            point.x := 8.
            output point.x.
            output point.
            """
        )
        self.assertEqual(output, "8\nPoint { x: 8, y: 2 }\n")

    def test_when_while_loop_break_and_continue(self) -> None:
        output, _ = run_source(
            """
            set count := 3.
            while count > 0 {
                output count.
                count := count - 1.
            }
            loop i in 0..6 {
                when i == 2 { continue. }
                when i == 4 { break. }
                output i.
            }
            """
        )
        self.assertEqual(output, "3\n2\n1\n0\n1\n3\n")

    def test_functions_closures_and_recursion(self) -> None:
        output, _ = run_source(
            """
            set offset := 10.
            makeFunction addOffset(value) { return value + offset. }
            makeFunction factorial(number) {
                when number <= 1 { return 1. }
                return number * factorial(number - 1).
            }
            output addOffset(5).
            output factorial(5).
            """
        )
        self.assertEqual(output, "15\n120\n")

    def test_input_and_conversion(self) -> None:
        output, _ = run_source(
            'input "name: " -> name. input "age: " -> age. '
            'output name + ":" + toText(toInt(age) + 1).',
            "小明\n18\n",
        )
        self.assertEqual(output, "name: age: 小明:19\n")

    def test_rand_int_is_in_closed_range(self) -> None:
        output, _ = run_source("output randInt(3, 3).")
        self.assertEqual(output, "3\n")

    def test_syntax_tour_runs_end_to_end(self) -> None:
        source = (Path(__file__).parents[1] / "examples" / "syntax_tour.zym").read_text(
            encoding="utf-8"
        )
        output, _ = run_source(source)
        self.assertEqual(
            output,
            "学生：小明\n总分：259\n平均分：86\n等级：通过\n",
        )

    def test_short_circuit_skips_unneeded_operand(self) -> None:
        output, _ = run_source(
            "output false and (1 / 0 == 0). output true or (1 / 0 == 0)."
        )
        self.assertEqual(output, "false\ntrue\n")

    def test_division_by_zero_reports_runtime_error(self) -> None:
        with self.assertRaisesRegex(
            ZymRuntimeError,
            r"interpreter_test\.zym:1:10: RuntimeError: division by zero",
        ):
            run_source("output 1 / 0.")

    def test_strict_boolean_condition(self) -> None:
        with self.assertRaisesRegex(ZymRuntimeError, "condition must be a boolean"):
            run_source('when 1 { output "wrong". }')

    def test_out_of_bounds_index_is_rejected(self) -> None:
        with self.assertRaisesRegex(ZymRuntimeError, "index 1 is out of bounds"):
            run_source("set values := [1]. output values[1].")

    def test_wrong_function_arity_is_rejected(self) -> None:
        with self.assertRaisesRegex(ZymRuntimeError, "expects 2 argument"):
            run_source("makeFunction add(a, b) { return a + b. } output add(1).")

    def test_break_and_return_outside_valid_context_are_rejected(self) -> None:
        with self.assertRaisesRegex(SemanticError, "break.*inside a loop"):
            run_source("break.")
        with self.assertRaisesRegex(SemanticError, "return.*inside a function"):
            run_source("return 1.")


if __name__ == "__main__":
    unittest.main()
