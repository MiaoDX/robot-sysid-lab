# L1 · 补充笔记与代码

完整讲解、视频、验证结果和练习都在 [L1 课程](index.zh-CN.md)中。本页提供按主题查阅的笔记，以及自行运行和检查实验的入口。

## 按问题查阅

- [装置与动力学](00-orientation.zh-CN.md)
- [从位置指令到力矩](01-command-to-torque.zh-CN.md)
- [拟合、验证与相位误差](02-fit-validation-residuals.zh-CN.md)
- [练习与结果的适用范围](03-exercise-and-limits.zh-CN.md)

## 查看实验结果

[完整报告](../../../reports/l1_servo_loaded_pendulum/report.zh-CN.md)包含参数、曲线、误差与实验条件。阅读时可以对照[报告大图](../../../reports/l1_servo_loaded_pendulum/report.png)，也可以下载 [Notebook](../../../notebooks/l1_servo_loaded_pendulum.ipynb)逐步检查计算。

## 自己运行一次

运行代码需要基础 Python 环境。实验使用 CPU，不需要机器人中间件或 GPU。在仓库根目录执行：

```bash
python -m pip install -r requirements-interactive.txt
python -m synthetic.l1_servo_loaded_pendulum --output-dir reports/l1_servo_loaded_pendulum
python -m marimo run apps/l1_servo_loaded_pendulum.py --host 0.0.0.0 --port 2719
```

应用中的操作练习见[课程末尾](index.zh-CN.md#local-experiment)。修改参数前先预测曲线怎样变化，运行后再比较拟合与验证结果。

## 复现记录

[工程验证记录](../../../reports/l1_servo_loaded_pendulum/verification.md)保留实验检查、复现命令和学员反馈项目，供检查实现时参考。
