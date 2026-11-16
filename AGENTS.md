# 在此仓库开发 ZYM 程序

编写或修改 `.zym` 时先读 [ZYM Skill](skills/zym-language/SKILL.md)。语言规则见 [语法规范](docs/SYNTAX.md)，入门示例见 [开发指南](docs/LANGUAGE_GUIDE.md)。

在仓库根目录用 `python -m zym check FILE` 解析脚本，再用 `python -m zym FILE` 验证实际行为。交互程序准备固定输入，核对输出和退出码。修改解释器后执行 `python tests/run_all.py`。

扩充语言黑盒测试时，在 `tests/blackbox/cases/` 添加 ZYM 程序，在 `tests/blackbox/manifest.json` 登记预期行为。课程应用的 Agent 开发过程记入 `docs/AGENT_DEVELOPMENT_LOG.md`，记录实际需求、实现决定、运行结果和发现的问题。
