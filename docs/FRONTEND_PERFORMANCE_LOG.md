# ZYM 解释器前端性能记录

## 测试目的

在完整 Interpreter 和 ZYM/Python 对比性能测试完成前，先为 Lexer + Parser 建立可重复的前端性能基线，并用测量结果验证一项小型优化。

本记录不是最终课程性能报告。最终报告仍需使用 ZYM 和 Python 实现同一算法，比较完整程序运行性能。

## 测试环境

- 日期：2026-11-02
- Python：3.12.14
- 平台：Windows 11 10.0.26200
- 输入：`examples/syntax_tour.zym`
- 源码字符数：724
- 每次输出 Token 数：162
- 每次输出顶层 AST 节点数：8
- 预热：100 次
- 正式轮数：7
- 每轮解析：1000 次
- 计时函数：`time.perf_counter()`
- Git HEAD：`e236bfd77259b9245fa39dec1a2ecb4e10d065a7`
- Git 状态：dirty，因为 Parser 和性能工具处于提交前审核阶段

## 优化内容

初始 Lexer 在每次调用 `_scan_token()` 时重新创建单字符 Token 映射字典，在每次处理字符串转义时重新创建转义映射字典。

优化后将两个只读映射移到模块级常量：

```text
_SINGLE_CHARACTER_TOKENS
_STRING_ESCAPES
```

这样扫描每个 Token 时不再重复分配相同字典。

## 测试结果

| 指标 | 优化前 | 优化后 | 变化 |
| --- | ---: | ---: | ---: |
| 最小单次解析耗时 | 1.194151 ms | 1.016307 ms | 降低 |
| 中位单次解析耗时 | 1.213873 ms | 1.020273 ms | 降低 15.95% |
| 最大单次解析耗时 | 1.536599 ms | 1.036971 ms | 降低 |
| 中位吞吐量 | 823.81 次/秒 | 980.13 次/秒 | 提高 18.98% |

原始数据：

- `benchmark/results/frontend_before_optimization.log`
- `benchmark/results/frontend_after_optimization.log`

## 结论与限制

在相同输入和相同测试参数下，移除重复字典分配后，中位解析耗时从 1.213873 ms 降至 1.020273 ms。结果说明该修改在本次环境下具有正向效果。

本测试只使用一个较小源文件，且优化前后顺序执行，仍可能受到 CPU 调频、后台进程和缓存状态影响。因此该结果作为开发期基线使用，不替代最终多规模、重复运行的 ZYM/Python 性能对比。

## 运行命令

```powershell
python benchmark/frontend_benchmark.py --iterations 1000 --rounds 7
```
