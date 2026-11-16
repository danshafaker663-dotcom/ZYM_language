"""Tree-walking interpreter for ZYM abstract syntax trees."""

from __future__ import annotations

from dataclasses import dataclass
import random
import sys
from typing import Any, Callable, TextIO

from zym import ast_nodes as ast
from zym.errors import SemanticError, ZymRuntimeError
from zym.runtime import Environment, StructureInstance, StructureType
from zym.token import Token, TokenType


class _BreakSignal(Exception):
    """Internal control-flow signal for break."""


class _ContinueSignal(Exception):
    """Internal control-flow signal for continue."""


class _ReturnSignal(Exception):
    """Internal control-flow signal carrying a function return value."""

    def __init__(self, value: Any) -> None:
        super().__init__()
        self.value = value


@dataclass(frozen=True)
class NativeFunction:
    """A standard-library function implemented in Python."""

    name: str
    parameter_count: int
    implementation: Callable[[Token, list[Any]], Any]

    @property
    def arity(self) -> int:
        return self.parameter_count

    def call(self, token: Token, arguments: list[Any]) -> Any:
        return self.implementation(token, arguments)


@dataclass(frozen=True)
class UserFunction:
    """A ZYM function declaration together with its lexical closure."""

    declaration: ast.FunctionDeclaration
    closure: Environment

    @property
    def name(self) -> str:
        return self.declaration.name.lexeme

    @property
    def arity(self) -> int:
        return len(self.declaration.parameters)


class Interpreter:
    """Execute a parsed ZYM Program using lexical environments."""

    def __init__(
        self,
        *,
        filename: str = "<source>",
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
        random_source: random.Random | None = None,
    ) -> None:
        self.filename = filename
        self.input_stream = input_stream or sys.stdin
        self.output_stream = output_stream or sys.stdout
        self.random_source = random_source or random.Random()
        self.globals = Environment(filename=filename)
        self.environment = self.globals
        self._loop_depth = 0
        self._function_depth = 0
        self._block_scope_cache: dict[int, bool] = {}
        self._install_builtins()

    def interpret(self, program: ast.Program) -> None:
        """Execute every top-level declaration in source order."""

        self._block_scope_cache.clear()
        for declaration in program.declarations:
            self._execute(declaration)

    def _execute(self, statement: ast.Stmt) -> None:
        statement_type = type(statement)

        if statement_type is ast.Block:
            cache_key = id(statement)
            try:
                needs_scope = self._block_scope_cache[cache_key]
            except KeyError:
                declaration_types = (
                    ast.VariableDeclaration,
                    ast.InputStatement,
                    ast.StructureDeclaration,
                    ast.FunctionDeclaration,
                )
                needs_scope = any(
                    type(declaration) in declaration_types
                    for declaration in statement.declarations
                )
                self._block_scope_cache[cache_key] = needs_scope
            if needs_scope:
                self._execute_block(
                    statement.declarations,
                    Environment(self.environment),
                )
            else:
                self._execute_declarations(statement.declarations)
            return

        if statement_type is ast.ExpressionStatement:
            self._evaluate(statement.expression)
            return

        if statement_type is ast.VariableDeclaration:
            value = self._evaluate(statement.initializer)
            self.environment.define(statement.name, value)
            return

        if statement_type is ast.Assignment:
            self._execute_assignment(statement)
            return

        if statement_type is ast.OutputStatement:
            value = self._evaluate(statement.expression)
            self.output_stream.write(f"{self.format_value(value)}\n")
            return

        if statement_type is ast.InputStatement:
            self._execute_input(statement)
            return

        if statement_type is ast.IfStatement:
            condition = self._evaluate(statement.condition)
            self._require_boolean(condition, statement.keyword, "when condition")
            if condition:
                self._execute(statement.then_branch)
            elif statement.else_branch is not None:
                self._execute(statement.else_branch)
            return

        if statement_type is ast.WhileStatement:
            self._execute_while(statement)
            return

        if statement_type is ast.LoopStatement:
            self._execute_loop(statement)
            return

        if statement_type is ast.BreakStatement:
            if self._loop_depth == 0:
                raise self._semantic_error(
                    statement.keyword,
                    "'break' can only be used inside a loop",
                )
            raise _BreakSignal()

        if statement_type is ast.ContinueStatement:
            if self._loop_depth == 0:
                raise self._semantic_error(
                    statement.keyword,
                    "'continue' can only be used inside a loop",
                )
            raise _ContinueSignal()

        if statement_type is ast.ReturnStatement:
            if self._function_depth == 0:
                raise self._semantic_error(
                    statement.keyword,
                    "'return' can only be used inside a function",
                )
            value = None if statement.value is None else self._evaluate(statement.value)
            raise _ReturnSignal(value)

        if statement_type is ast.StructureDeclaration:
            field_names = tuple(field.lexeme for field in statement.fields)
            if len(set(field_names)) != len(field_names):
                raise self._semantic_error(
                    statement.name,
                    f"structure '{statement.name.lexeme}' contains duplicate fields",
                )
            structure_type = StructureType(
                statement.name.lexeme,
                field_names,
                filename=self.filename,
            )
            self.environment.define(statement.name, structure_type)
            return

        if statement_type is ast.FunctionDeclaration:
            parameter_names = [parameter.lexeme for parameter in statement.parameters]
            if len(set(parameter_names)) != len(parameter_names):
                raise self._semantic_error(
                    statement.name,
                    f"function '{statement.name.lexeme}' contains duplicate parameters",
                )
            function = UserFunction(statement, self.environment)
            self.environment.define(statement.name, function)
            return

        raise TypeError(f"unsupported statement node: {type(statement).__name__}")

    def _execute_block(
        self,
        declarations: tuple[ast.Stmt, ...],
        environment: Environment,
    ) -> None:
        previous = self.environment
        try:
            self.environment = environment
            self._execute_declarations(declarations)
        finally:
            self.environment = previous

    def _execute_declarations(self, declarations: tuple[ast.Stmt, ...]) -> None:
        for declaration in declarations:
            self._execute(declaration)

    def _execute_assignment(self, statement: ast.Assignment) -> None:
        value = self._evaluate(statement.value)
        target = statement.target
        target_type = type(target)

        if target_type is ast.Variable:
            self.environment.assign(target.name, value)
            return

        if target_type is ast.IndexAccess:
            collection = self._evaluate(target.collection)
            index = self._evaluate(target.index)
            self._set_index(collection, index, value, target.bracket)
            return

        if target_type is ast.FieldAccess:
            instance = self._evaluate(target.object)
            if not isinstance(instance, StructureInstance):
                raise self._runtime_error(
                    target.name,
                    "field assignment requires a structure instance",
                )
            instance.set(target.name, value)
            return

        raise TypeError(f"unsupported assignment target: {type(target).__name__}")

    def _execute_input(self, statement: ast.InputStatement) -> None:
        prompt = self._evaluate(statement.prompt)
        if not isinstance(prompt, str):
            raise self._runtime_error(
                statement.keyword,
                "input prompt must be a string",
            )
        self.output_stream.write(prompt)
        self.output_stream.flush()
        line = self.input_stream.readline()
        if line == "":
            raise self._runtime_error(statement.keyword, "input reached end of file")
        value = line.removesuffix("\n").removesuffix("\r")
        self.environment.define(statement.name, value)

    def _execute_while(self, statement: ast.WhileStatement) -> None:
        self._loop_depth += 1
        try:
            while True:
                condition = self._evaluate(statement.condition)
                self._require_boolean(
                    condition,
                    statement.keyword,
                    "while condition",
                )
                if not condition:
                    break
                try:
                    self._execute(statement.body)
                except _ContinueSignal:
                    continue
                except _BreakSignal:
                    break
        finally:
            self._loop_depth -= 1

    def _execute_loop(self, statement: ast.LoopStatement) -> None:
        start = self._evaluate(statement.start)
        end = self._evaluate(statement.end)
        self._require_integer(start, statement.keyword, "loop range start")
        self._require_integer(end, statement.keyword, "loop range end")

        loop_environment = Environment(self.environment)
        loop_environment.define(statement.variable, start)
        previous_environment = self.environment
        self.environment = loop_environment
        self._loop_depth += 1
        try:
            for current in range(start, end):
                loop_environment.assign(statement.variable, current)
                try:
                    self._execute(statement.body)
                except _ContinueSignal:
                    continue
                except _BreakSignal:
                    break
        finally:
            self._loop_depth -= 1
            self.environment = previous_environment

    def _evaluate(self, expression: ast.Expr) -> Any:
        expression_type = type(expression)

        if expression_type is ast.Literal:
            return expression.value

        if expression_type is ast.Variable:
            return self.environment.get(expression.name)

        if expression_type is ast.Grouping:
            return self._evaluate(expression.expression)

        if expression_type is ast.Unary:
            return self._evaluate_unary(expression)

        if expression_type is ast.Binary:
            return self._evaluate_binary(expression)

        if expression_type is ast.Logical:
            return self._evaluate_logical(expression)

        if expression_type is ast.ArrayLiteral:
            return [self._evaluate(element) for element in expression.elements]

        if expression_type is ast.StructureLiteral:
            return self._evaluate_structure_literal(expression)

        if expression_type is ast.IndexAccess:
            collection = self._evaluate(expression.collection)
            index = self._evaluate(expression.index)
            return self._get_index(collection, index, expression.bracket)

        if expression_type is ast.FieldAccess:
            instance = self._evaluate(expression.object)
            if not isinstance(instance, StructureInstance):
                raise self._runtime_error(
                    expression.name,
                    "field access requires a structure instance",
                )
            return instance.get(expression.name)

        if expression_type is ast.Call:
            return self._evaluate_call(expression)

        raise TypeError(f"unsupported expression node: {type(expression).__name__}")

    def _evaluate_unary(self, expression: ast.Unary) -> Any:
        operand = self._evaluate(expression.operand)
        if expression.operator.type is TokenType.MINUS:
            self._require_integer(operand, expression.operator, "unary '-'")
            return -operand
        if expression.operator.type is TokenType.NOT:
            self._require_boolean(operand, expression.operator, "'not'")
            return not operand
        raise TypeError(f"unsupported unary operator: {expression.operator.type}")

    def _evaluate_binary(self, expression: ast.Binary) -> Any:
        left = self._evaluate(expression.left)
        right = self._evaluate(expression.right)
        operator = expression.operator
        operator_type = operator.type

        if operator_type is TokenType.EQUAL_EQUAL:
            return self._values_equal(left, right)
        if operator_type is TokenType.BANG_EQUAL:
            return not self._values_equal(left, right)

        if operator_type is TokenType.PLUS:
            if type(left) is int and type(right) is int:
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise self._runtime_error(
                operator,
                "'+' requires two integers or two strings",
            )

        self._require_integer(left, operator, f"'{operator.lexeme}' left operand")
        self._require_integer(right, operator, f"'{operator.lexeme}' right operand")

        if operator_type is TokenType.MINUS:
            return left - right
        if operator_type is TokenType.STAR:
            return left * right
        if operator_type is TokenType.SLASH:
            if right == 0:
                raise self._runtime_error(operator, "division by zero")
            return self._truncating_division(left, right)
        if operator_type is TokenType.PERCENT:
            if right == 0:
                raise self._runtime_error(operator, "remainder by zero")
            quotient = self._truncating_division(left, right)
            return left - quotient * right
        if operator_type is TokenType.LESS:
            return left < right
        if operator_type is TokenType.LESS_EQUAL:
            return left <= right
        if operator_type is TokenType.GREATER:
            return left > right
        if operator_type is TokenType.GREATER_EQUAL:
            return left >= right

        raise TypeError(f"unsupported binary operator: {operator_type}")

    def _evaluate_logical(self, expression: ast.Logical) -> bool:
        left = self._evaluate(expression.left)
        self._require_boolean(left, expression.operator, "logical left operand")

        if expression.operator.type is TokenType.OR and left:
            return True
        if expression.operator.type is TokenType.AND and not left:
            return False

        right = self._evaluate(expression.right)
        self._require_boolean(right, expression.operator, "logical right operand")
        return right

    def _evaluate_structure_literal(self, expression: ast.StructureLiteral) -> Any:
        structure_type = self.environment.get(expression.name)
        if not isinstance(structure_type, StructureType):
            raise self._runtime_error(
                expression.name,
                f"'{expression.name.lexeme}' is not a structure type",
            )

        values: dict[str, Any] = {}
        for field in expression.fields:
            if field.name.lexeme in values:
                raise self._runtime_error(
                    field.name,
                    f"duplicate field '{field.name.lexeme}'",
                )
            values[field.name.lexeme] = self._evaluate(field.value)
        return structure_type.create(values, expression.name)

    def _evaluate_call(self, expression: ast.Call) -> Any:
        callee = self._evaluate(expression.callee)
        arguments = [self._evaluate(argument) for argument in expression.arguments]
        callee_type = type(callee)
        if callee_type is NativeFunction:
            arity = callee.parameter_count
        elif callee_type is UserFunction:
            arity = len(callee.declaration.parameters)
        else:
            raise self._runtime_error(expression.paren, "value is not callable")
        if len(arguments) != arity:
            raise self._runtime_error(
                expression.paren,
                f"{callee.name} expects {arity} argument(s), got {len(arguments)}",
            )
        if callee_type is NativeFunction:
            return callee.implementation(expression.paren, arguments)
        return self._call_user_function(callee, arguments)

    def _call_user_function(
        self,
        function: UserFunction,
        arguments: list[Any],
    ) -> Any:
        call_environment = Environment(function.closure)
        for parameter, argument in zip(
            function.declaration.parameters,
            arguments,
            strict=True,
        ):
            call_environment.define(parameter, argument)

        previous_loop_depth = self._loop_depth
        self._loop_depth = 0
        self._function_depth += 1
        try:
            self._execute_block(
                function.declaration.body.declarations,
                call_environment,
            )
        except _ReturnSignal as signal:
            return signal.value
        finally:
            self._function_depth -= 1
            self._loop_depth = previous_loop_depth
        return None

    def _get_index(self, collection: Any, index: Any, token: Token) -> Any:
        if not isinstance(collection, list):
            raise self._runtime_error(token, "indexing requires an array")
        self._require_integer(index, token, "array index")
        if index < 0 or index >= len(collection):
            raise self._runtime_error(token, f"array index {index} is out of bounds")
        return collection[index]

    def _set_index(
        self,
        collection: Any,
        index: Any,
        value: Any,
        token: Token,
    ) -> None:
        if not isinstance(collection, list):
            raise self._runtime_error(token, "indexed assignment requires an array")
        self._require_integer(index, token, "array index")
        if index < 0 or index >= len(collection):
            raise self._runtime_error(token, f"array index {index} is out of bounds")
        collection[index] = value

    def _install_builtins(self) -> None:
        builtins = (
            NativeFunction("length", 1, self._builtin_length),
            NativeFunction("toInt", 1, self._builtin_to_int),
            NativeFunction("toText", 1, self._builtin_to_text),
            NativeFunction("push", 2, self._builtin_push),
            NativeFunction("pop", 1, self._builtin_pop),
            NativeFunction("randInt", 2, self._builtin_rand_int),
            NativeFunction("typeOf", 1, self._builtin_type_of),
        )
        for function in builtins:
            self.globals.define_builtin(function.name, function)

    def _builtin_length(self, token: Token, arguments: list[Any]) -> int:
        value = arguments[0]
        if not isinstance(value, (str, list)):
            raise self._runtime_error(token, "length expects a string or array")
        return len(value)

    def _builtin_to_int(self, token: Token, arguments: list[Any]) -> int:
        value = arguments[0]
        if not isinstance(value, str):
            raise self._runtime_error(token, "toInt expects a string")
        digits = value[1:] if value.startswith(("+", "-")) else value
        if not digits or not digits.isascii() or not digits.isdigit():
            raise self._runtime_error(token, f"cannot convert {value!r} to integer")
        return int(value)

    def _builtin_to_text(self, _token: Token, arguments: list[Any]) -> str:
        return self.format_value(arguments[0])

    def _builtin_push(self, token: Token, arguments: list[Any]) -> None:
        array = arguments[0]
        if not isinstance(array, list):
            raise self._runtime_error(token, "push expects an array as its first argument")
        array.append(arguments[1])
        return None

    def _builtin_pop(self, token: Token, arguments: list[Any]) -> Any:
        array = arguments[0]
        if not isinstance(array, list):
            raise self._runtime_error(token, "pop expects an array")
        if not array:
            raise self._runtime_error(token, "cannot pop an empty array")
        return array.pop()

    def _builtin_rand_int(self, token: Token, arguments: list[Any]) -> int:
        minimum, maximum = arguments
        self._require_integer(minimum, token, "randInt minimum")
        self._require_integer(maximum, token, "randInt maximum")
        if minimum > maximum:
            raise self._runtime_error(token, "randInt minimum exceeds maximum")
        return self.random_source.randint(minimum, maximum)

    def _builtin_type_of(self, _token: Token, arguments: list[Any]) -> str:
        value = arguments[0]
        if value is None:
            return "null"
        if type(value) is bool:
            return "boolean"
        if type(value) is int:
            return "integer"
        if isinstance(value, str):
            return "string"
        if isinstance(value, list):
            return "array"
        if isinstance(value, StructureInstance):
            return "structure"
        if isinstance(value, StructureType):
            return "structureType"
        if isinstance(value, (NativeFunction, UserFunction)):
            return "function"
        raise TypeError(f"unknown ZYM runtime value: {type(value).__name__}")

    def format_value(self, value: Any) -> str:
        """Return the stable user-visible text representation of a ZYM value."""

        if value is None:
            return "null"
        if type(value) is bool:
            return "true" if value else "false"
        if type(value) is int:
            return str(value)
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return "[" + ", ".join(self.format_value(item) for item in value) + "]"
        if isinstance(value, StructureInstance):
            fields = ", ".join(
                f"{name}: {self.format_value(field_value)}"
                for name, field_value in value.values.items()
            )
            return f"{value.structure_type.name} {{ {fields} }}"
        if isinstance(value, StructureType):
            return f"<structure {value.name}>"
        if isinstance(value, (NativeFunction, UserFunction)):
            return f"<function {value.name}>"
        raise TypeError(f"unknown ZYM runtime value: {type(value).__name__}")

    def _require_boolean(self, value: Any, token: Token, context: str) -> None:
        if type(value) is not bool:
            raise self._runtime_error(token, f"{context} must be a boolean")

    def _require_integer(self, value: Any, token: Token, context: str) -> None:
        if type(value) is not int:
            raise self._runtime_error(token, f"{context} must be an integer")

    @staticmethod
    def _truncating_division(left: int, right: int) -> int:
        magnitude = abs(left) // abs(right)
        return -magnitude if (left < 0) != (right < 0) else magnitude

    @staticmethod
    def _values_equal(left: Any, right: Any) -> bool:
        if type(left) is not type(right):
            return False
        return left == right

    def _runtime_error(self, token: Token, message: str) -> ZymRuntimeError:
        return ZymRuntimeError(
            message,
            filename=self.filename,
            line=token.line,
            column=token.column,
        )

    def _semantic_error(self, token: Token, message: str) -> SemanticError:
        return SemanticError(
            message,
            filename=self.filename,
            line=token.line,
            column=token.column,
        )
