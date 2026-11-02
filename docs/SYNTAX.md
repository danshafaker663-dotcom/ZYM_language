# ZYM 语言语法规范

版本：0.1 草案  
状态：解释器实现前的基线规范

## 1. 设计目标

ZYM 是一门动态类型、解释执行、面向脚本任务的通用语言。语法强调直接表达行为，并保持足够小的实现规模，使词法分析、语法分析和运行时都可以在课程项目中完整实现。

ZYM 的关键字组合、句点终止符及输入输出写法构成其主要语法特色。它会吸收多种语言的常见设计，但不完全复制任何一种现有语言。

## 2. 源文件

- 推荐扩展名：`.zym`
- 源文件编码：UTF-8
- 标识符区分大小写
- 换行只用于排版，不自动终止语句
- 变量声明、赋值、表达式、输出、输入、返回和循环跳转以 `.` 结束
- 代码块由 `{` 和 `}` 包围，块结束后不写句点

## 3. 注释

单行注释以 `#` 开始，直到当前行末结束。

```zym
# 这是注释
set answer := 42. # 行尾注释
```

0.1 版本不支持多行注释。

## 4. 标识符与关键字

标识符以 Unicode 字母或下划线开头，后续可以包含 Unicode 字母、数字或下划线。

有效示例：

```text
score
player_name
玩家
item2
```

保留关键字：

```text
set true false null
output input
when otherwise
while loop in
break continue
declare makeFunction return
and or not
```

## 5. 数据类型

### 5.1 整数

整数使用十进制表示。0.1 版本不支持浮点数。

```zym
set zero := 0.
set positive := 128.
set negative := -32.
```

整数采用宿主 Python 的任意精度整数语义，不发生固定宽度溢出。

### 5.2 字符串

字符串使用双引号包围，支持以下转义：

```text
\n    换行
\t    制表符
\"    双引号
\\    反斜杠
```

```zym
set message := "hello\nZYM".
```

### 5.3 布尔值与空值

```zym
set enabled := true.
set finished := false.
set missing := null.
```

### 5.4 数组

数组是有序、可变、从 0 开始索引的值序列。一个数组可以保存不同类型的值。

```zym
set values := [10, "ZYM", true].
output values[0].
values[1] := "language".
push(values, 99).
```

访问负数索引或超出范围的索引会产生运行时错误。

### 5.5 结构类型

`declare` 声明一种结构类型及其固定字段。创建实例时必须为所有字段赋值，且不得提供未知字段。

```zym
declare Student {
    name,
    score
}.

set student := Student {
    name: "小明",
    score: 95
}.

output student.name.
student.score := 96.
```

字段可变。访问不存在的字段会产生运行时错误。

### 5.6 函数

函数是一等运行时值，但 0.1 版本主要通过函数名调用。函数可以递归调用，并使用词法作用域。

## 6. 变量与赋值

变量必须先声明后使用。

```zym
set count := 1.
count := count + 1.
```

同一作用域内重复声明同名变量属于运行时错误。内层作用域可以遮蔽外层变量。

可赋值目标包括：

- 普通变量
- 数组元素
- 结构字段

```zym
name := "new name".
items[0] := 100.
player.health := 80.
```

## 7. 运算符

运算符优先级从低到高如下：

| 级别 | 运算符 | 含义 |
| --- | --- | --- |
| 1 | `or` | 逻辑或 |
| 2 | `and` | 逻辑与 |
| 3 | `== !=` | 相等与不等 |
| 4 | `< <= > >=` | 大小比较 |
| 5 | `+ -` | 加、减、字符串连接 |
| 6 | `* / %` | 乘、整数除、取余 |
| 7 | `not -` | 逻辑非、数值取负 |
| 8 | `()` `[]` `.` | 调用、索引、字段访问 |

除法 `/` 为向零截断的整数除法。除数为 0 会产生运行时错误。

`+` 支持两个整数相加或两个字符串连接，不执行隐式类型转换。

逻辑运算要求操作数为布尔值，并采用短路求值。

## 8. 真值规则

`when`、`while`、`and`、`or` 和 `not` 只接受布尔值。ZYM 不把整数、字符串、数组或空值隐式转换为布尔值。

```zym
when length(items) > 0 {
    output "not empty".
}
```

## 9. 输入输出

### 9.1 输出

`output` 计算表达式并向标准输出写入其文本形式和换行符。

```zym
output "hello".
output 1 + 2.
```

数组和结构实例使用稳定、可读的格式输出，以便黑盒测试比较结果。

### 9.2 输入

`input` 先输出提示文本，再从标准输入读取一行字符串，并赋给目标变量。目标变量由 `input` 声明，因此此前不需要 `set`。

```zym
input "请输入姓名：" -> name.
input "请输入年龄：" -> age_text.
set age := toInt(age_text).
```

测试环境可以使用空提示文本，避免提示内容干扰预期输出：

```zym
input "" -> value.
```

读取到文件末尾时产生运行时错误。

## 10. 条件分支

```zym
when score >= 90 {
    output "优秀".
} otherwise when score >= 60 {
    output "通过".
} otherwise {
    output "未通过".
}
```

条件必须为布尔值。每个代码块创建新的词法作用域。

## 11. 循环

### 11.1 while 循环

```zym
while count > 0 {
    output count.
    count := count - 1.
}
```

### 11.2 loop 范围循环

范围表达式 `start..end` 包含起点，不包含终点。

```zym
loop i in 0..3 {
    output i.
}
```

上例依次输出 `0`、`1`、`2`。起点和终点必须是整数。当起点大于或等于终点时，循环执行零次。

循环变量只在循环体作用域内可见。

### 11.3 循环控制

```zym
break.
continue.
```

在循环外使用 `break` 或 `continue` 属于语义错误。

## 12. 函数

函数使用 `makeFunction` 定义，使用 `return` 返回结果。

```zym
makeFunction max(a, b) {
    when a > b {
        return a.
    }
    return b.
}

output max(4, 7).
```

语义规则：

- 参数按值传递；数组和结构值本身是引用语义，因此函数内可修改其内容
- 参数数量必须与定义完全一致
- 每次调用创建独立的局部作用域
- 函数可以调用自身或其他已经定义的函数
- 没有执行 `return` 的函数返回 `null`
- `return` 只能出现在函数内部

0.1 版本不支持默认参数、可变参数和函数重载。

## 13. 内置函数

计划提供以下最小标准库：

| 函数 | 说明 |
| --- | --- |
| `length(value)` | 返回字符串或数组长度 |
| `toInt(text)` | 将十进制字符串转换为整数 |
| `toText(value)` | 返回值的稳定文本形式 |
| `push(array, value)` | 在数组尾部加入值，返回 `null` |
| `pop(array)` | 删除并返回数组末尾值 |
| `randInt(min, max)` | 返回闭区间内的随机整数 |
| `typeOf(value)` | 返回值的类型名称字符串 |

所有内置函数都检查参数数量和参数类型。

## 14. 作用域

ZYM 使用词法作用域。

- 程序顶层形成全局作用域
- 函数调用形成函数作用域
- 分支和循环体形成块作用域
- 名称查找从当前作用域逐层向外进行
- 对变量赋值时，修改最近一层已经存在的同名变量
- `set` 总是在当前作用域创建新变量

## 15. 错误类别

解释器需要区分以下错误：

| 类别 | 建议退出码 | 示例 |
| --- | ---: | --- |
| `LexError` | 2 | 非法字符、未终止字符串 |
| `ParseError` | 3 | 缺少句点、括号不匹配 |
| `SemanticError` | 4 | 循环外使用 `break` |
| `RuntimeError` | 5 | 除零、越界、类型错误 |
| `FileError` | 6 | 源文件不存在或无法读取 |

错误格式必须稳定：

```text
文件名:行号:列号: ErrorType: 错误说明
```

例如：

```text
demo.zym:3:12: RuntimeError: division by zero
```

错误写入 stderr，正常程序输出写入 stdout。

## 16. 形式文法

下面是 0.1 版本的简化 EBNF。词法分析必须优先识别双字符或多字符符号，例如 `:=`、`->`、`..`、`<=`。

```ebnf
program        = declaration* EOF ;

declaration    = structure_decl
               | function_decl
               | statement ;

structure_decl = "declare" IDENT "{" field_list? "}" "." ;
field_list     = IDENT ("," IDENT)* ","? ;

function_decl  = "makeFunction" IDENT "(" parameters? ")" block ;
parameters     = IDENT ("," IDENT)* ;

statement      = set_stmt
               | assignment_stmt
               | output_stmt
               | input_stmt
               | when_stmt
               | while_stmt
               | loop_stmt
               | break_stmt
               | continue_stmt
               | return_stmt
               | expression_stmt
               | block ;

set_stmt       = "set" IDENT ":=" expression "." ;
assignment_stmt= assign_target ":=" expression "." ;
assign_target  = IDENT ("[" expression "]" | "." IDENT)* ;
output_stmt    = "output" expression "." ;
input_stmt     = "input" expression "->" IDENT "." ;

when_stmt      = "when" expression block
                 ("otherwise" "when" expression block)*
                 ("otherwise" block)? ;
while_stmt     = "while" expression block ;
loop_stmt      = "loop" IDENT "in" expression ".." expression block ;

break_stmt     = "break" "." ;
continue_stmt  = "continue" "." ;
return_stmt    = "return" expression? "." ;
expression_stmt= expression "." ;
block          = "{" declaration* "}" ;

expression     = logic_or ;
logic_or       = logic_and ("or" logic_and)* ;
logic_and      = equality ("and" equality)* ;
equality       = comparison (("==" | "!=") comparison)* ;
comparison     = term (("<" | "<=" | ">" | ">=") term)* ;
term           = factor (("+" | "-") factor)* ;
factor         = unary (("*" | "/" | "%") unary)* ;
unary          = ("not" | "-") unary | postfix ;
postfix        = primary (("(" arguments? ")")
                         | ("[" expression "]")
                         | ("." IDENT))* ;
arguments      = expression ("," expression)* ;

primary        = INTEGER
               | STRING
               | "true"
               | "false"
               | "null"
               | IDENT
               | array_literal
               | structure_literal
               | "(" expression ")" ;

array_literal  = "[" arguments? "]" ;
structure_literal = IDENT "{" field_values? "}" ;
field_values   = field_value ("," field_value)* ","? ;
field_value    = IDENT ":" expression ;
```

## 17. 暂不支持的功能

为控制课程项目规模，0.1 版本暂不支持：

- 浮点数
- 类与继承
- 模块导入
- 异常捕获
- 闭包的显式函数值语法
- 文件和网络标准库
- 并发

这些内容可以在答辩的“局限与未来工作”中说明，不应在核心功能完成前扩展。

