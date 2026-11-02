# ZYM 编程 Agent 开发记录

## 1. 基本信息

- 项目名称：ZYM 解释型通用脚本语言
- 课程：程序设计实践
- 学生姓名：张煜鸣
- 学号：2024211206
- GitHub：https://github.com/danshafaker663-dotcom/ZYM_language
- 使用的编程 Agent：OpenAI Codex
- 开发方式：学生负责需求确认、语言设计、代码实现、测试和验收；编程 Agent 提供规划、文档草案、代码审查、Git 指导和排错辅助

## 2. 记录原则

本文件记录编程 Agent 在项目中的实际使用过程。每条记录包含任务目标、学生决策、Agent 辅助内容、实际产出、验证方法和对应 Git 提交。

Agent 提供的内容必须经过学生检查，不能直接视为正确结果。项目核心代码必须由学生理解，并能够在课程验收时解释。

---

## 3. 开发记录

### 记录 001：分析课程要求

- 日期：2026-10-28
- 任务：分析课程大作业要求并制定实施路线。
- 学生输入：提供完整作业要求，并说明课程课件位于本地文件夹。
- Agent 辅助：
  - 阅读课程简介、Git 工作流和测试课件。
  - 将作业拆分为语言设计、解释器、黑盒测试、性能测试、Agent 指南、示例应用和系统介绍 PPT。
  - 建议使用 Python 实现 Lexer、Parser、AST 和 Interpreter 分层的树遍历解释器。
- 学生决策：采用 ZYM 作为语言名称，使用 Python 实现解释器。
- 产出：项目总体实施路线。
- 验证：逐项对照作业要求，确认计划覆盖所有交付物。
- Git 提交：此时尚未创建仓库。

### 记录 002：初始化项目和语言规范

- 日期：2026-11-01
- 任务：建立项目目录、Git 仓库和第一版语言规范。
- Agent 辅助：
  - 创建项目目录结构并初始化本地 Git 仓库。
  - 起草 README、语法规范、开发路线和语法展示程序。
- 学生决策：项目目录使用 `D:\学习\网存作业`，主分支使用 `main`，初始文档作为后续修改的草案。
- 修改文件：
  - `.gitignore`
  - `README.md`
  - `docs/SYNTAX.md`
  - `docs/ROADMAP.md`
  - `examples/syntax_tour.zym`
- 验证：执行 `git diff --check`、`git status` 和 `git log`。
- 对应提交：`48a9d7c chore: initialize ZYM language project and specification`
- 说明：本阶段的目录结构和文档初稿由 Agent 辅助生成，后续解释器核心代码由学生逐步实现。

### 记录 003：连接 GitHub

- 日期：2026-11-01
- 任务：将本地 Git 仓库连接到 GitHub。
- 学生操作：在 GitHub 创建空仓库，进入本地项目目录，添加远程仓库并执行首次推送。
- Agent 辅助：解释本地仓库、远程仓库、`origin` 和上游分支的含义，提供连接和推送命令。
- 远程仓库：`https://github.com/danshafaker663-dotcom/ZYM_language.git`
- 验证：执行 `git remote -v`、`git status`，并在 GitHub 页面检查提交和项目文件。
- Git 提交：本步骤未产生新的文件提交。

### 记录 004：修改语言关键词并完善 README

- 日期：2026-11-01
- 任务：根据学生的个人设计修改 ZYM 关键词并完善项目说明。
- 学生决策：

| 功能 | 关键词 |
| --- | --- |
| 声明变量 | `set` |
| 输出内容 | `output` |
| 读取输入 | `input` |
| 范围循环 | `loop` |
| 条件循环 | `while` |
| 定义结构类型 | `declare` |
| 定义函数 | `makeFunction` |
| 返回结果 | `return` |

- Agent 辅助：整理关键词映射，指出 `makeFuntion` 的拼写问题，提供完整 README 草案，并指导检查暂存区差异。
- 学生操作：手动修改 README，填写真实姓名、学号和 GitHub 地址，依次检查、暂存和提交修改。
- 验证：执行 `git diff --check`、`git diff`、`git diff --cached --check` 和 `git diff --cached --stat`。
- 对应提交：`1c5bae7 docs: expand README and update ZYM language design`

### 记录 005：Git 安全回滚实验

- 日期：2026-11-02
- 任务：验证已经推送到 GitHub 的错误提交能否安全撤销。
- 实验过程：
  1. 在 README 中加入 `ROLLBACK_TEST` 临时内容。
  2. 创建临时提交并推送到 GitHub。
  3. 执行 `git revert --no-edit 13e53e9` 创建反向提交。
  4. 使用 `Select-String` 验证 README 中已不存在临时内容。
  5. 将回滚提交推送到 GitHub。
- Agent 辅助：解释 `git revert` 与 `git reset --hard` 的区别，并逐步指导检查、提交、推送和回滚。
- 临时提交：`13e53e9 test: add temporary rollback marker`
- 回滚提交：`867fbd1 Revert "test: add temporary rollback marker"`
- 排错记录：第一次推送回滚提交时发生 SSL/TLS 握手失败。没有关闭 SSL 验证，再次执行 `git push` 后成功。
- 验证：本地 `main` 与 `origin/main` 指向同一提交，README 中不存在临时标记，GitHub 历史保留临时提交和回滚提交。
- 结论：公开分支上的错误提交应优先使用 `git revert` 撤销，避免使用强制推送重写公共历史。

### 记录 006：定义 Token 数据模型

- 日期：2026-11-02
- 任务：开始解释器核心实现，定义词法分析阶段使用的 Token 类型和数据结构。
- 学生输入：授权 Agent 创建并提交 Token 模块，同时要求解释 Token 类的作用。
- Agent 辅助：
  - 根据最终语法规范整理标点、运算符、字面量和关键字 Token。
  - 创建 ZYM 包入口和 `zym/token.py`。
  - 提供关键字文本到 Token 类型的映射表。
  - 使用不可变数据类保存 Token 的类型、原文、值和源码位置。
- 学生需要掌握：Token 是 Lexer 输出、Parser 输入的最小语法单位；行列信息用于错误诊断。
- 修改文件：
  - `zym/__init__.py`
  - `zym/token.py`
  - `docs/AGENT_DEVELOPMENT_LOG.md`
- 验证：导入模块，构造整数 Token，检查关键字映射，并执行 Python 字节码编译检查。
- 对应提交：`feat: define ZYM token model and keyword table`（哈希以 Git 历史为准）。

### 记录 007：实现词法分析器

- 日期：2026-11-02
- 任务：实现 ZYM Lexer 和词法错误诊断，并在提交前交由学生审核。
- 学生输入：授权 Agent 实现代码，但要求先查看和审核代码，不立即提交。
- Agent 辅助：
  - 实现源码游标、行列位置跟踪和 EOF Token。
  - 实现标点、算术运算符、多字符运算符和比较运算符扫描。
  - 实现整数、字符串转义、Unicode 标识符和关键字识别。
  - 实现 `#` 单行注释和空白字符处理。
  - 实现包含文件名、行号和列号的 `LexError`。
  - 使用 Python 标准库 `unittest` 添加 Lexer 单元测试。
- 修改文件：
  - `zym/errors.py`
  - `zym/lexer.py`
  - `tests/test_lexer.py`
  - `docs/AGENT_DEVELOPMENT_LOG.md`
- 验证：运行字节码编译检查、Lexer 单元测试和 `git diff --check`。
- 对应提交：`feat: implement ZYM lexer and lexical diagnostics`（哈希以 Git 历史为准）。

---

## 4. 后续记录要求

后续使用编程 Agent 时继续追加记录，包括：

- Token 和词法分析器设计
- AST 和语法分析器设计
- 解释执行器开发
- 黑盒测试设计
- 性能测试设计与结果分析
- Agent Skill 开发
- 200 行以上 ZYM 应用开发
- 系统介绍 PPT 制作
- Bug 排查和修复过程

每条记录都需要写明学生自己的决定、Agent 的辅助内容、测试结果和对应 Git 提交，不能只记录最终结果。

