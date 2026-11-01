# ZYM Language

ZYM 是一门为“程序设计实践”课程大作业设计的解释型通用脚本语言。工作名称取自 `zhangyuming` 的首字母；如需使用其他姓名缩写，可在正式发布前统一改名。

项目目标是从零实现一套可读、可测试、对编程 Agent 友好的脚本语言及其工具链。解释器使用 Python 3 编写，但不会调用 Python 的 `eval` 或 `exec` 执行 ZYM 源代码。

## 作业交付范围

- 整数、字符串、布尔值和空值
- 数组与用户定义的结构类型
- 标准输入与标准输出
- 条件分支和循环控制
- 函数定义、调用、返回及递归
- 命令行解释器和清晰的错误诊断
- 使用 ZYM 编写的完整黑盒测试集
- 与等价 Python 程序对比的性能测试
- 面向开发者和编程 Agent 的开发指南
- 不少于 200 行的完整 ZYM 应用程序
- 可追溯的 Git 历史和系统介绍 PPT

## 语言特色

ZYM 使用动词式关键字表达程序行为：

- `let` 声明变量
- `say` 输出内容
- `ask` 读取输入
- `when / otherwise` 表达分支
- `repeat / while` 表达循环
- `shape` 定义结构类型
- `craft / give` 定义函数和返回结果
- 简单语句以句点 `.` 结束，代码块使用 `{}`

示例：

```zym
craft factorial(n) {
    when n <= 1 {
        give 1.
    }
    give n * factorial(n - 1).
}

say "5! = " + toText(factorial(5)).
```

## 当前状态

当前处于第 1 阶段：语言需求与语法规范已经建立，解释器尚未实现。

完整语法见 [docs/SYNTAX.md](docs/SYNTAX.md)，开发阶段见 [docs/ROADMAP.md](docs/ROADMAP.md)。

## 计划中的命令行接口

```powershell
python zym.py run examples/hello.zym
python zym.py check examples/hello.zym
python zym.py --version
python tests/run_tests.py
python benchmark/run_benchmark.py
```

## 实现原则

1. 先固定语言规范，再实现解释器。
2. 每个功能都必须有对应的黑盒测试。
3. 错误必须报告文件名、行号、列号和错误类别。
4. 正常结果写入 stdout，诊断信息写入 stderr。
5. 每个开发阶段形成独立、可解释的 Git 提交。

