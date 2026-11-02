# ZYM Git 历史记录

## 说明

Git 的完整历史保存在仓库的 `.git` 目录和 GitHub 远程仓库中。本文件是截至 2026-11-02 的可读快照，用于课程材料整理；后续开发产生新提交后，需要在最终提交前更新本文件。

- 本地仓库：`D:\学习\网存作业`
- 远程仓库：https://github.com/danshafaker663-dotcom/ZYM_language
- 主分支：`main`
- Git 作者：`13135856270 <2024211206@bupt.cn>`

## 提交历史

### 867fbd1：撤销临时回滚标记

- 完整哈希：`867fbd10063eec0aca1eb1f9fcb3c9c4d3a5a0f7`
- 时间：2026-11-02 08:17:55 +08:00
- 说明：`Revert "test: add temporary rollback marker"`
- 目的：撤销已经推送的临时 README 内容，同时保留完整历史。

### 13e53e9：创建回滚实验提交

- 完整哈希：`13e53e946d2fb906a68be4f80b00088a85b4df1f`
- 时间：2026-11-02 08:14:23 +08:00
- 说明：`test: add temporary rollback marker`
- 目的：模拟错误提交已经推送到 GitHub 的情况，用于验证 `git revert`。

### 1c5bae7：完善 README 和语言设计

- 完整哈希：`1c5bae799b19ef3995f1951f9b133e173515d055`
- 时间：2026-11-01 22:56:29 +08:00
- 说明：`docs: expand README and update ZYM language design`
- 目的：补充项目信息、系统架构、交付计划，并确定新的核心关键词。

### 48a9d7c：初始化项目

- 完整哈希：`48a9d7c2195840fc2812ce165fa1eca9969bdc1e`
- 时间：2026-11-01 22:29:39 +08:00
- 说明：`chore: initialize ZYM language project and specification`
- 目的：创建目录结构、README、语法规范、开发路线和初始语法示例。

## 回滚实验结论

本项目通过一次真实实验验证了 GitHub 上已推送提交的回滚过程：

```text
48a9d7c  初始化项目
    ↓
1c5bae7  完善 README
    ↓
13e53e9  添加临时错误内容
    ↓
867fbd1  使用 git revert 撤销临时内容
```

`git revert` 不删除原提交，而是增加一个反向修改提交。这种方式不会重写公共分支历史，适合已经推送到 GitHub 的提交。

## 查看最新历史

简洁模式：

```powershell
git log --oneline --graph --decorate --all
```

详细模式：

```powershell
git log --pretty=format:"提交：%H%n作者：%an <%ae>%n时间：%ad%n说明：%s%n" --date=iso
```

最终提交作业前，应以命令输出和 GitHub 提交页面为准，并更新本文件中的历史快照。
