# 从一个成绩单开始写 ZYM

在 PowerShell 进入项目根目录，执行下面两行验证环境。本文示例使用 Python 3.12 启动仓库里的解释器。

```powershell
Set-Location -LiteralPath "D:\学习\网存作业"
python -m zym --version
```

版本应显示 `ZYM 0.1.0`。新建 UTF-8 文本文件 `grades.zym`，写入下面的完整程序。

```zym
declare Grade { name, scores }.

makeFunction average(scores) {
    when length(scores) == 0 { return 0. }
    set total := 0.
    loop i in 0..length(scores) {
        total := total + scores[i].
    }
    return total / length(scores).
}

input "Name? " -> name.
set student := Grade { name: name, scores: [85, 90] }.
output student.name + " " + toText(average(student.scores)).
```

先运行 `python -m zym check grades.zym` 检查词法和语法，再运行 `python -m zym grades.zym`。出现提示后输入 `Ming` 并回车，程序输出 `Ming 87`。数组从 0 开始，范围循环不含右端点，所以两次读到的分数分别为 85、90。整数除法向零截断，175 除以 2 得到 87。

试着把数组换成 `[]` 并重新运行。函数会提前返回 0。要增加分数，在输出前加入 `push(student.scores, 95).`，它会修改原数组。结构字段也可以直接赋值，例如 `student.name := "Lin".`。

## 写下一段程序时

- `set n := 1.` 在当前作用域声明变量，`n := n + 1.` 更新最近的同名变量。代码块可以遮蔽外层变量。
- `input` 声明的变量保存字符串。读取数字后用 `toInt(text)` 转换。字符串拼接前用 `toText(value)` 转换其他类型。
- 已知次数用 `loop`，按条件重复用 `while n > 0 { n := n - 1. }`。分支和循环条件必须为布尔值。循环中用 `break.` 退出，用 `continue.` 跳过本轮剩余语句。
- 简单语句以英文句点结束，结构声明以 ` }.` 结束，函数和控制块以 `}` 结束。访问字段时把字段名紧接在句点后。
- `check` 通过后仍需实际运行。若看到 `RuntimeError`，用文件名、行号、列号定位表达式，检查类型、数组下标或除数。

全部语法见 [语法规范](SYNTAX.md)。可直接运行的综合示例见 [syntax_tour.zym](../examples/syntax_tour.zym)。
