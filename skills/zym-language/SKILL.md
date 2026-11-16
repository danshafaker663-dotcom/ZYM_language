---
name: zym-language
description: 在 ZYM 0.1 仓库中编写、检查、运行和调试 .zym 脚本。适用于交互式应用、函数、结构、数组以及命令行黑盒测试。
---

# 编写 ZYM 脚本

1. 从仓库根目录运行解释器。先确定程序的输入、输出，再查看 [可执行示例](../../examples/syntax_tour.zym) 或 [完整语法](../../docs/SYNTAX.md)。
2. 用 `declare Point { x, y }.` 定义结构，用 `set p := Point { x: 0, y: 1 }.` 提供全部字段。用 `p.x := 3.` 更新字段。数组下标必须满足 `0 <= i` 且 `i < length(items)`。
3. 用 `makeFunction twice(n) { return n * 2. }` 定义函数后再调用。数组和结构作为参数时共享内容。用 `when ... { ... } otherwise { ... }` 分支，用 `loop i in 0..length(items) { ... }` 遍历。条件使用显式布尔表达式。
4. 标准库提供 `length`、`toInt`、`toText`、`push`、`pop`、`randInt`、`typeOf`。随机数包含两端。读取一行用 `input "" -> text.`；读到 EOF 会报错。菜单应用提供明确的退出选项。
5. 执行 `python -m zym check FILE` 和 `python -m zym FILE`。至少试一个普通输入和一个会改变控制流的边界输入，例如空数组或退出选项。按 stdout、stderr、退出码核对。退出码 2、3、4、5、6 分别对应词法、语法、语义、运行时和文件错误。
