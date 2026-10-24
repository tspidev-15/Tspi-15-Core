"""Automated tests for the TSPI-15 v0.1 interpreter."""

import unittest

from tspi15.interpreter import TSPIError, run_source


class InterpreterTests(unittest.TestCase):
    def execute(self, source):
        output = []
        run_source(source, output=output.append)
        return output

    def test_variables_and_output(self):
        self.assertEqual(
            self.execute(
                'var name = "Alex"\n'
                'var score = 12\n'
                'show name\n'
                'show score\n'
            ),
            ["Alex", "12"],
        )

    def test_arithmetic_precedence(self):
        self.assertEqual(
            self.execute(
                "show 2 + 3 * 4\n"
                "show (2 + 3) * 4\n"
            ),
            ["14", "20"],
        )

    def test_string_and_numeric_addition(self):
        self.assertEqual(
            self.execute(
                'show "hello " + "world"\n'
                'show 10 + "5"\n'
            ),
            ["hello world", "15"],
        )

    def test_comparison_coercion(self):
        self.assertEqual(
            self.execute('show 10 == "10"\n'),
            ["true"],
        )

    def test_conditions_and_truthiness(self):
        self.assertEqual(
            self.execute(
                'when 0:\n'
                '    show "bad"\n'
                'otherwise:\n'
                '    show "good"\n'
            ),
            ["good"],
        )

    def test_redeclaration_changes_global_type(self):
        source = (
            'var value = 10\n'
            'when true:\n'
            '    var value = "ready"\n'
            'show value\n'
        )
        self.assertEqual(self.execute(source), ["ready"])

    def test_typed_variable(self):
        self.assertEqual(
            self.execute(
                "var points: number\n"
                "points = 5\n"
                "show points\n"
            ),
            ["5"],
        )

        with self.assertRaisesRegex(
            TSPIError,
            "has not been initialized",
        ):
            self.execute(
                "var points: number\n"
                "show points\n"
            )

    def test_function_return(self):
        self.assertEqual(
            self.execute(
                "function answer:\n"
                "    return 42\n"
                "var result = answer\n"
                "show result\n"
            ),
            ["42"],
        )

    def test_missing_function_return(self):
        with self.assertRaisesRegex(
            TSPIError,
            "without returning a value",
        ):
            self.execute(
                'function broken:\n'
                '    show "hello"\n'
                'broken\n'
            )

    def test_return_outside_function(self):
        with self.assertRaisesRegex(
            TSPIError,
            "only be used inside a function",
        ):
            self.execute("return 5\n")

    def test_division_by_zero(self):
        with self.assertRaisesRegex(
            TSPIError,
            "Division by zero",
        ):
            self.execute("show 1 / 0\n")

    def test_invalid_conversion(self):
        with self.assertRaisesRegex(
            TSPIError,
            "Cannot convert",
        ):
            self.execute('show "hello" - 2\n')

    def test_escapes(self):
        self.assertEqual(
            self.execute('show "one\\ntwo"\n'),
            ["one\ntwo"],
        )

    def test_comments_inside_strings(self):
        self.assertEqual(
            self.execute('show "a # b" # comment\n'),
            ["a # b"],
        )

    def test_bad_indentation(self):
        with self.assertRaisesRegex(
            TSPIError,
            "multiples of four",
        ):
            self.execute(
                'when true:\n'
                '  show "bad"\n'
            )


if __name__ == "__main__":
    unittest.main()