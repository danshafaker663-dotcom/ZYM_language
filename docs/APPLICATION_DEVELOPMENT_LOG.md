# 星火地下城 Agent开发记录

## 项目任务

- 日期：2026-11-16
- 开发者：张煜鸣
- 编程Agent：Codex
- 目标：使用ZYM开发功能完整、有效代码不少于200行的应用程序，并保存Agent辅助过程。

## 需求与设计

学生完成解释器、测试、性能对比和Agent指南后要求继续下一阶段。Agent依据课程要求和项目ZYM Skill选择终端地下城RPG，确定以下验收点：

1. 应用必须能通过公开命令行入口运行；
2. 使用结构、数组、输入输出、分支、两种循环、函数和内置函数；
3. 提供明确退出选项，便于人工演示和自动测试；
4. 包含完整游戏循环，而不是只展示语法；
5. 有固定输入的冒烟测试和可复现开发记录。

Agent设计了 `Player`、`Monster`、`Room` 三种结构。游戏循环包括探索、随机事件、战斗、药水、逃跑、经验升级、金币与商店。玩家达到5级获胜，生命归零失败，也可以从菜单主动退出。

## Agent生成与检查过程

1. Agent阅读项目 `AGENTS.md`、`skills/zym-language/SKILL.md` 和语法规范，确认ZYM 0.1的类型、作用域和内置函数。
2. Agent生成 `app/dungeon_game.zym` 初稿，使用菜单字符串避免无效数字转换导致程序中断。
3. 解释器执行 `check`，语法检查一次通过。
4. Agent用固定输入运行三条路径：直接退出、查看状态后退出、进入商店后退出，三条路径退出码均为0。
5. 统计得到总行数399，去除空行和注释后代码行368。
6. 审查时发现菜单“保存战绩并退出”暗示文件存档，但ZYM 0.1没有文件写入功能，因此改为“结束冒险并退出”。
7. Agent新增子进程冒烟测试、应用README，并运行项目全部自动测试。

## 功能与源码对应

| 功能 | 实现位置 |
| --- | --- |
| 数据模型 | `Player`、`Monster`、`Room`结构声明 |
| 角色成长 | `gainExperience`、`restoreHealth` |
| 战斗 | `fight`、`playerAttack`、`monsterAttack` |
| 随机事件 | `treasureEvent`、`trapEvent`、`shrineEvent` |
| 探索 | `explore`和房间数组 |
| 商店 | `shop`循环和金币判断 |
| 主程序 | 名字输入、主菜单、胜负与退出总结 |

## 验证记录

```text
python -m zym check app/dungeon_game.zym
Syntax OK: app\dungeon_game.zym

direct_exit PASS
status_exit PASS
shop_exit PASS
total_lines=399
nonblank_code_lines=368
```

自动测试使用独立解释器进程，检查退出码、stderr和关键输出。随机探索与战斗适合线下演示，固定菜单路径用于持续集成，避免随机结果使测试不稳定。

最终一键测试结果：63项内部及应用测试通过，53个ZYM黑盒用例通过，共116项检查无失败，总耗时9.976448秒。

## 学生审核要点

- 运行游戏并体验至少一次探索和一次战斗；
- 检查关键字、函数和结构是否能向教师解释；
- 根据个人表达习惯调整剧情文本；
- 提交前查看Git diff和自动测试结果。
