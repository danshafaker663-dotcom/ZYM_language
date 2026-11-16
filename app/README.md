# 星火地下城

这是使用ZYM 0.1编写的终端角色扮演游戏，也是课程要求的200行以上综合应用。主程序共有399行，其中去除空行和注释后有368行ZYM代码。

## 运行

在项目根目录执行：

```powershell
python -m zym check app/dungeon_game.zym
python -m zym app/dungeon_game.zym
```

输入英雄名字后，通过数字菜单探索地下城。主菜单可以探索房间、查看状态、进入商店、查看帮助或退出。战斗菜单可以攻击、使用药水或尝试逃跑。达到5级即可通关，生命降到0则冒险结束。

## 使用的语言功能

- `Player`、`Monster`、`Room`三种结构类型；
- 玩家、怪物和房间数组；
- 17个函数及返回值；
- `input`与`output`交互；
- `when / otherwise`多分支；
- `while`主循环、战斗循环和商店循环；
- `loop`、数组索引和结构字段修改；
- `randInt`、`length`与`toText`内置函数；
- 经验升级、药水、金币、商店和随机事件。

## 自动冒烟测试

`tests/test_application.py`通过独立子进程验证直接退出、查看状态后退出、进入商店后退出三条固定路径。完整测试命令为：

```powershell
python tests/run_all.py
```
