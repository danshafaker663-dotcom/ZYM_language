# ZYM Language

ZYM 是一门为“程序设计实践”课程大作业设计的解释型通用脚本语言。

项目将从零实现词法分析器、语法分析器、抽象语法树和解释执行器，并提供完整的黑盒测试、性能测试、开发文档、编程 Agent 指南和示例应用。

解释器使用 Python 3 实现，但不会使用 Python 的 `eval` 或 `exec` 直接执行 ZYM 源代码。

## 项目信息

- 课程：程序设计实践
- 项目名称：ZYM 解释型通用脚本语言
- 作者：张煜鸣
- 学号：2024211206
- 实现语言：Python 3
- ZYM 源文件扩展名：`.zym`
- GitHub：https://github.com/danshafaker663-dotcom/ZYM_language
- 开发方式：学生负责设计、实现和验收，编程 Agent 提供规划、代码审查、测试设计和排错辅助

## 项目目标

本项目需要完成以下内容：

1. 设计一门具有个人特色的解释型通用脚本语言。
2. 使用 Python 实现 ZYM 语言解释器。
3. 使用 ZYM 编写覆盖全部语言功能的黑盒测试。
4. 使用一个命令运行全部自动化测试。
5. 编写 ZYM 与 Python 的性能对比程序。
6. 编写面向开发者和编程 Agent 的开发指南。
7. 使用编程 Agent 辅助开发一个不少于 200 行的 ZYM 应用。
8. 使用 Git 保存完整、真实、可追溯的开发历史。
9. 制作系统介绍和课程答辩 PPT。

## 语言功能

ZYM 计划支持以下功能：

- 整数、字符串、布尔值和空值
- 数组
- 用户自定义结构类型
- 变量声明与赋值
- 标准输入和标准输出
- 条件分支
- 范围循环和条件循环
- 函数定义与调用
- 函数参数与返回值
- 递归调用
- 词法作用域
- 基础标准库
- 带文件名、行号和列号的错误诊断

## 语言特色

ZYM 使用动词式关键字表达程序行为：

- `set`：声明变量
- `output`：输出内容
- `input`：读取输入
- `when / otherwise`：条件分支
- `loop`：范围循环
- `while`：条件循环
- `break / continue`：控制循环
- `declare`：定义结构类型
- `makeFunction`：定义函数
- `return`：返回函数结果

ZYM 的简单语句使用句点 `.` 结束，代码块使用 `{}` 包围。

## 语法示例

```zym
# 定义学生结构类型
declare Student {
    name,
    scores
}.

# 定义数组求和函数
makeFunction sum(values) {
    set total := 0.

    loop i in 0..length(values) {
        total := total + values[i].
    }

    return total.
}

# 定义阶乘函数
makeFunction factorial(n) {
    when n <= 1 {
        return 1.
    }

    return n * factorial(n - 1).
}

# 创建结构实例
set student := Student {
    name: "小明",
    scores: [88, 95, 76]
}.

# 输出内容
output "学生：" + student.name.
output "总分：" + toText(sum(student.scores)).
output "5! = " + toText(factorial(5)).

# 读取用户输入
input "请输入姓名：" -> userName.
output "你好，" + userName.

# 条件循环
set count := 3.

while count > 0 {
    output count.
    count := count - 1.
}
```

## 解释器架构

ZYM 解释器采用以下处理流程：

```text
ZYM 源代码
    ↓
词法分析器 Lexer
    ↓
Token 序列
    ↓
语法分析器 Parser
    ↓
抽象语法树 AST
    ↓
解释执行器 Interpreter
    ↓
程序运行结果
```

解释器主要由以下模块组成：

- Token 定义
- 词法分析器
- 抽象语法树节点
- 递归下降语法分析器
- 运行时值
- 变量作用域
- 解释执行器
- 内置函数
- 错误诊断
- 命令行接口

## 项目目录

```text
ZYM_language/
├─ README.md
├─ zym.py
├─ zym/
│  ├─ token.py
│  ├─ lexer.py
│  ├─ ast_nodes.py
│  ├─ parser.py
│  ├─ environment.py
│  ├─ interpreter.py
│  ├─ builtins.py
│  ├─ errors.py
│  └─ cli.py
├─ docs/
│  ├─ SYNTAX.md
│  ├─ ROADMAP.md
│  ├─ LANGUAGE_GUIDE.md
│  ├─ INTERPRETER_DESIGN.md
│  ├─ TEST_REPORT.md
│  ├─ PERFORMANCE_REPORT.md
│  ├─ AGENT_DEVELOPMENT_LOG.md
│  └─ DEMO_GUIDE.md
├─ examples/
│  ├─ hello.zym
│  └─ syntax_tour.zym
├─ tests/
│  ├─ cases/
│  ├─ expected/
│  └─ run_tests.py
├─ benchmark/
│  ├─ prime_sieve.zym
│  ├─ prime_sieve.py
│  ├─ run_benchmark.py
│  └─ results/
├─ app/
│  └─ dungeon_game.zym
├─ skills/
│  └─ zym-language/
│     └─ SKILL.md
├─ scripts/
└─ presentation/
```

部分文件将在后续开发阶段逐步创建。

## 计划中的命令行接口

运行 ZYM 程序：

```powershell
python zym.py run examples/hello.zym
```

仅检查语法：

```powershell
python zym.py check examples/hello.zym
```

查看版本：

```powershell
python zym.py --version
```

运行全部黑盒测试：

```powershell
python tests/run_tests.py
```

执行性能测试：

```powershell
python benchmark/run_benchmark.py
```

以上命令是计划中的最终接口。当前阶段解释器尚未完成，部分命令暂时不可用。

## 黑盒测试设计

测试用例主体使用 ZYM 语言编写。

测试驱动程序将通过命令行启动解释器，并比较：

- 标准输出
- 标准错误
- 进程退出码

测试将覆盖：

- 基本数据类型
- 运算符优先级
- 数组操作
- 结构类型
- 输入输出
- 条件分支
- 两种循环
- 函数调用
- 递归
- 作用域
- 语法错误
- 类型错误
- 数组越界
- 除零错误
- 未定义变量

## 性能测试设计

性能测试将使用 ZYM 和 Python 分别实现相同的质数筛选算法。

测试过程包括：

1. 验证两个程序输出相同。
2. 使用多组输入规模。
3. 每组输入重复运行多次。
4. 统计最小值、中位数和最大值。
5. 保存原始测试数据。
6. 分析解释器与 Python 的性能差异。

## Agent 辅助开发

项目允许编程 Agent 参与以下工作：

- 分析课程要求
- 制定开发计划
- 检查语言设计
- 审查代码
- 生成测试思路
- 协助定位错误
- 整理开发文档
- 辅助开发示例应用

学生本人负责：

- 确定语言设计
- 编写和理解核心代码
- 审查 Agent 建议
- 执行测试
- 判断实现是否正确
- 完成课程验收和答辩

Agent 的使用过程记录在：

```text
docs/AGENT_DEVELOPMENT_LOG.md
```

## Git 工作流

项目使用 Git 进行版本管理。

推荐工作流程：

```text
修改文件
    ↓
git diff 检查修改
    ↓
git add 暂存文件
    ↓
git diff --cached 检查待提交内容
    ↓
git commit 创建本地提交
    ↓
git push 推送到 GitHub
```

已经推送的错误提交优先使用 `git revert` 撤销，以保留完整开发历史。

## 当前进度

当前项目处于语言设计阶段：

- [x] 创建项目目录
- [x] 初始化 Git 仓库
- [x] 连接 GitHub
- [x] 确定项目名称
- [x] 确定主要语言功能
- [x] 确定核心关键字
- [x] 编写第一版语法规范
- [ ] 实现 Token 定义
- [ ] 实现词法分析器
- [ ] 实现抽象语法树
- [ ] 实现语法分析器
- [ ] 实现解释执行器
- [ ] 完成黑盒测试
- [ ] 完成性能测试
- [ ] 编写 Agent 开发指南
- [ ] 完成 200 行以上应用
- [ ] 制作系统介绍 PPT

## 开发原则

1. 先确定语法和语义，再实现解释器。
2. 不使用 Python 的 `eval` 或 `exec` 执行 ZYM 代码。
3. 每项语言功能必须具有对应测试。
4. 测试必须验证输出、错误信息和退出码。
5. 正常结果写入 stdout，错误信息写入 stderr。
6. 错误诊断必须包含源码位置。
7. 每个开发阶段形成独立的 Git 提交。
8. Agent 生成的内容必须经过人工检查。
9. Git 历史和 Agent 开发记录必须真实。
10. 所有核心实现都需要能够在答辩时解释。
ROLLBACK_TEST：这是一条用于验证 Git 回滚的临时内容。