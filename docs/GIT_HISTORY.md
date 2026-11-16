# ZYM Git 历史记录

## 1. 文档说明

Git 的权威历史保存在本地仓库的 `.git` 目录及 GitHub 远程仓库中。本文件是课程提交使用的可读历史快照，记录 ZYM 项目从初始化到完整应用开发的主要过程。

- 项目作者：张煜鸣（学号：2024211206）
- 本地仓库：`D:\学习\网存作业`
- 远程仓库：<https://github.com/danshafaker663-dotcom/ZYM_language>
- 主分支：`main`
- Git 作者：`13135856270 <2024211206@bupt.cn>`
- 快照日期：2026-11-16
- 快照截止提交：`f85a1a5`（`feat: add ZYM dungeon game application`）
- 截止该提交的历史数量：19 个提交

本仓库采用小步提交方式保存设计、编码、测试、优化和应用开发过程。提交信息使用 `chore`、`docs`、`feat`、`test` 和 `perf` 等前缀区分修改类型。

## 2. 完整提交历史

以下记录按时间从早到晚排列。短哈希可以通过 `git show <短哈希>` 查看对应的完整修改。

| 序号 | 日期 | 提交 | 类型 | 原始提交信息 | 主要内容 |
| ---: | --- | --- | --- | --- | --- |
| 1 | 2026-11-01 22:29 | `48a9d7c` | 初始化 | `chore: initialize ZYM language project and specification` | 创建仓库目录、README、初始语法规范、开发路线和示例。 |
| 2 | 2026-11-01 22:56 | `1c5bae7` | 文档 | `docs: expand README and update ZYM language design` | 完善项目信息、系统架构和语言关键词设计。 |
| 3 | 2026-11-02 08:14 | `13e53e9` | 实验 | `test: add temporary rollback marker` | 添加临时错误标记，模拟已经推送的错误提交。 |
| 4 | 2026-11-02 08:17 | `867fbd1` | 回滚 | `Revert "test: add temporary rollback marker"` | 使用 `git revert` 安全撤销临时内容，保留公共历史。 |
| 5 | 2026-11-02 08:27 | `92224bb` | 文档 | `docs: add agent development and Git history logs` | 增加 Agent 开发记录和 Git 历史说明。 |
| 6 | 2026-11-02 08:46 | `e499fb3` | 文档 | `docs: align syntax specification with final keywords` | 将规范统一为 `set`、`output`、`input`、`loop`、`declare`、`makeFunction`、`return` 等最终关键词。 |
| 7 | 2026-11-02 08:56 | `5f7d1ff` | 功能 | `feat: define ZYM token model and keyword table` | 定义 Token 类型、源码位置和关键词映射表。 |
| 8 | 2026-11-02 09:10 | `73c9601` | 功能 | `feat: implement ZYM lexer and lexical diagnostics` | 实现手写词法分析器及带行列位置的词法错误诊断。 |
| 9 | 2026-11-02 09:34 | `e236bfd` | 功能 | `feat: define ZYM abstract syntax tree nodes` | 定义程序、语句、表达式、函数和结构类型等 AST 节点。 |
| 10 | 2026-11-15 13:22 | `49437f3` | 功能 | `feat: implement recursive descent parser` | 实现递归下降语法分析器和表达式优先级解析。 |
| 11 | 2026-11-15 13:22 | `3e89a87` | 测试 | `test: add automated test and performance logs` | 增加自动测试及测试、性能执行日志基础设施。 |
| 12 | 2026-11-15 13:27 | `0362114` | 功能 | `feat: add runtime environments and structure values` | 实现链式作用域、变量环境和结构实例运行时模型。 |
| 13 | 2026-11-15 13:40 | `4872352` | 功能 | `feat: implement tree-walking interpreter` | 实现树遍历解释执行、控制流、函数、数组、结构和内置函数。 |
| 14 | 2026-11-15 13:40 | `dfc7d1d` | 功能 | `feat: add ZYM command-line interface` | 增加 `run`、`check`、`--help`、`--version` 和分类退出码。 |
| 15 | 2026-11-15 13:56 | `73acbde` | 测试 | `test: add complete ZYM black-box suite` | 增加覆盖全部语言功能和主要错误路径的黑盒测试集。 |
| 16 | 2026-11-15 14:00 | `cefe45c` | 性能 | `perf: compare ZYM and Python prime sieve` | 使用等价质数筛脚本比较 ZYM 与 Python 的执行性能。 |
| 17 | 2026-11-16 10:57 | `5639efe` | 性能 | `perf: optimize interpreter hot paths` | 优化作用域查询、AST 分派、块执行和内置函数调用热点。 |
| 18 | 2026-11-16 11:04 | `b81e150` | 文档 | `docs: add ZYM guides for developers and agents` | 增加面向开发者和编程 Agent 的语言指南、项目规则与 Skill。 |
| 19 | 2026-11-16 11:16 | `f85a1a5` | 应用 | `feat: add ZYM dungeon game application` | 增加 399 行终端地牢 RPG、应用说明、冒烟测试和 Agent 开发记录。 |

## 3. 分阶段开发轨迹

### 3.1 项目设计阶段

提交 `48a9d7c` 至 `e499fb3` 完成项目初始化、语言定位、最终关键词设计、开发记录模板及 Git 回滚实验。该阶段先确定语法和交付结构，再开始解释器编码。

### 3.2 编译前端阶段

提交 `5f7d1ff` 至 `49437f3` 依次实现 Token 模型、词法分析、AST 节点和递归下降语法分析器，形成如下处理流程：

```text
ZYM 源代码 -> Token 序列 -> AST 语法树
```

### 3.3 运行时与命令行阶段

提交 `0362114`、`4872352` 和 `dfc7d1d` 实现运行环境、树遍历解释器和命令行入口，形成完整执行流程：

```text
源文件 -> 词法分析 -> 语法分析 -> AST -> 解释执行 -> 输出
```

### 3.4 测试与性能阶段

提交 `3e89a87`、`73acbde`、`cefe45c` 和 `5639efe` 建立自动测试、黑盒测试和性能对比体系，并根据性能分析结果优化解释器热点路径。当前测试包含 63 项单元及集成测试和 53 项黑盒测试，共 116 项检查。

### 3.5 文档与应用阶段

提交 `b81e150` 和 `f85a1a5` 完成人类开发指南、Agent Skill 及 399 行终端地牢 RPG，验证 ZYM 可以用于编写具有输入输出、结构类型、数组、函数、分支和循环的完整应用。

## 4. Git 回滚实验

本项目通过一次真实提交验证了 GitHub 公共分支上的安全回滚过程：

```text
48a9d7c  初始化项目
    |
1c5bae7  完善 README 和语言设计
    |
13e53e9  添加临时错误内容，并推送到 GitHub
    |
867fbd1  使用 git revert 生成反向提交
```

执行的核心命令为：

```powershell
git revert --no-edit 13e53e9
git push
```

验证结果：README 中的临时标记已经消失，但错误提交 `13e53e9` 和撤销提交 `867fbd1` 都保留在历史中。这说明 `git revert` 不会重写已经共享的历史，适合撤销已推送到 GitHub 的提交。

## 5. 当前仓库状态

更新本历史快照前，分支状态如下：

```text
main -> f85a1a5
origin/main -> f85a1a5
```

这表示本地 `main` 与 GitHub 的 `origin/main` 已同步。更新本文件后会产生新的未提交修改，需要经过审核、提交并推送后再次保持同步。

## 6. 历史核验命令

查看图形化简洁历史：

```powershell
git log --oneline --graph --decorate --all
```

查看全部提交的作者、时间和完整哈希：

```powershell
git log --pretty=format:"提交：%H%n作者：%an <%ae>%n时间：%ad%n说明：%s%n" --date=iso
```

查看某次提交的具体修改：

```powershell
git show 5639efe
```

核对本地分支与 GitHub 的同步状态：

```powershell
git status -sb
git branch -vv
git remote -v
```

导出可随作业保存的完整历史文本：

```powershell
git log --oneline --graph --decorate --all > git-history.txt
```

最终提交作业时，应同时保留 `.git` 目录、GitHub 仓库、本说明文档和各阶段开发日志，以便验收时展示完整开发过程。
