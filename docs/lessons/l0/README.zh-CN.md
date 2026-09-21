# L0 · 补充笔记与代码

完整讲解、视频、验证结果和练习都在 [L0 课程](index.zh-CN.md)中。本页提供按主题查阅的笔记，以及自行运行和检查实验的入口。

## 按问题查阅

- [系统、观测与未知量](00-orientation.zh-CN.md)
- [惯量、阻尼与输入选择](01-physics-to-data.zh-CN.md)
- [拟合、验证与残差](02-fit-to-validation.zh-CN.md)
- [实验假设与下一步](03-assumptions-and-next-step.zh-CN.md)

## 查看实验结果

[完整报告](../../../reports/l0_inertia_damping/report.zh-CN.md)包含参数、曲线、误差与实验条件。阅读时可以对照[报告大图](../../../reports/l0_inertia_damping/report.png)，也可以下载 [Notebook](../../../notebooks/l0_inertia_damping.ipynb)逐步检查计算。

## 自己运行一次

运行代码需要基础 Python 环境。实验使用 CPU，不需要机器人中间件或 GPU。在仓库根目录执行：

```bash
python -m pip install -r requirements-interactive.txt
python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping
python -m marimo run apps/l0_inertia_damping.py --host 0.0.0.0 --port 2718
```

应用中的操作练习见[课程末尾](index.zh-CN.md#local-experiment)。修改参数前先预测曲线怎样变化，运行后再比较拟合与验证结果。

## 复现记录

[工程验证记录](../../../reports/l0_inertia_damping/verification.md)保留实验检查、复现命令和学员反馈项目，供检查实现时参考。
