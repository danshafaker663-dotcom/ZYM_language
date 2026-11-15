"""Tests for ZYM runtime environments and structure values."""

import unittest

from zym.errors import SemanticError, ZymRuntimeError
from zym.runtime import Environment, StructureType
from zym.token import Token, TokenType


def identifier(name: str, line: int = 1, column: int = 1) -> Token:
    return Token(TokenType.IDENTIFIER, name, None, line, column)


class EnvironmentTests(unittest.TestCase):
    def test_define_and_get_local_variable(self) -> None:
        environment = Environment(filename="runtime_test.zym")
        environment.define(identifier("score"), 95)
        self.assertEqual(environment.get(identifier("score")), 95)

    def test_nested_scope_reads_enclosing_variable(self) -> None:
        global_environment = Environment(filename="runtime_test.zym")
        global_environment.define(identifier("name"), "ZYM")
        local_environment = Environment(global_environment)
        self.assertEqual(local_environment.get(identifier("name")), "ZYM")

    def test_assignment_updates_nearest_existing_scope(self) -> None:
        global_environment = Environment(filename="runtime_test.zym")
        global_environment.define(identifier("count"), 1)
        local_environment = Environment(global_environment)
        local_environment.assign(identifier("count"), 2)
        self.assertEqual(global_environment.get(identifier("count")), 2)

    def test_local_declaration_shadows_enclosing_name(self) -> None:
        global_environment = Environment(filename="runtime_test.zym")
        global_environment.define(identifier("value"), "global")
        local_environment = Environment(global_environment)
        local_environment.define(identifier("value"), "local")
        self.assertEqual(local_environment.get(identifier("value")), "local")
        self.assertEqual(global_environment.get(identifier("value")), "global")

    def test_duplicate_local_declaration_is_rejected(self) -> None:
        environment = Environment(filename="runtime_test.zym")
        environment.define(identifier("value"), 1)
        with self.assertRaisesRegex(SemanticError, "already declared"):
            environment.define(identifier("value", 3, 7), 2)

    def test_undefined_name_reports_source_position(self) -> None:
        with self.assertRaisesRegex(
            ZymRuntimeError,
            r"runtime_test\.zym:4:9: RuntimeError: undefined name 'missing'",
        ):
            Environment(filename="runtime_test.zym").get(identifier("missing", 4, 9))


class StructureValueTests(unittest.TestCase):
    def test_create_read_and_update_structure(self) -> None:
        student_type = StructureType(
            "Student", ("name", "score"), filename="runtime_test.zym"
        )
        student = student_type.create(
            {"score": 90, "name": "小明"},
            identifier("Student"),
        )
        self.assertEqual(student.get(identifier("name")), "小明")
        student.set(identifier("score"), 96)
        self.assertEqual(student.get(identifier("score")), 96)
        self.assertEqual(tuple(student.values), ("name", "score"))

    def test_missing_and_unknown_fields_are_rejected(self) -> None:
        point_type = StructureType(
            "Point", ("x", "y"), filename="runtime_test.zym"
        )
        with self.assertRaisesRegex(ZymRuntimeError, "missing field.*y"):
            point_type.create({"x": 1}, identifier("Point"))
        with self.assertRaisesRegex(ZymRuntimeError, "unknown field.*z"):
            point_type.create({"x": 1, "y": 2, "z": 3}, identifier("Point"))

    def test_unknown_field_access_is_rejected(self) -> None:
        point = StructureType(
            "Point", ("x",), filename="runtime_test.zym"
        ).create(
            {"x": 1},
            identifier("Point"),
        )
        with self.assertRaisesRegex(ZymRuntimeError, "has no field 'y'"):
            point.get(identifier("y", 8, 4))


if __name__ == "__main__":
    unittest.main()
