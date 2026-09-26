# 课程交付状态

本页是 19 个 K/L 课程编号的交付台账，把阅读或概念页、可使用的数值证据和教学素材分开。页面已发布不自动代表实验可运行或已有视频讲课。共享规则见[课程交付政策](../lesson_delivery_policy.zh-CN.md)。

## 证据与素材矩阵 {#evidence-media-matrix}

“已有”表示链接素材已检查且可以回答该问题；“计划中”表示问题有价值但运行或渲染尚未完成；“无需视频”表示静态推导或紧凑图表更清楚，并在行中说明理由。

| 编号 | 页面类别 | 可使用证据 | 视频状态与对应问题 |
|---|---|---|---|
| [K0](../lessons/k0/index.zh-CN.md) | 概念 + 引用实验 | [L0 失配报告](../../reports/l0_inertia_damping/report.zh-CN.md)与失配回放 | **已有 · 1 段：** [l0-mismatch.mp4](../../demos/manim/rendered/l0-mismatch.mp4)，回答“坏模型看起来怎样？” |
| [K1](../lessons/k1/index.zh-CN.md) | 阅读 | 页面中的信号与参数解释 | **无需视频：** 边界表和练习用静态文字更短更清楚 |
| [K2](../lessons/k2/index.zh-CN.md) | 概念 | [标注摆图](../lessons/k2/assets/pendulum-boundary.svg)与[解析分解图](../lessons/k2/assets/torque-residual-illustrative.png)，明确为示意 | **无需视频：** 静态推导和图足以回答单位/力矩平衡练习；不暗示实验证据 |
| [K3](../lessons/k3/index.zh-CN.md) | 概念 + 引用 L1 | [L1 摩擦报告](../../reports/l1_friction/report.zh-CN.md)与 L1 边界证据 | **已有 · 复用 3 段：** [l1-boundary.mp4](../../demos/manim/rendered/l1-boundary.mp4)、[l1-phase.mp4](../../demos/manim/rendered/l1-phase.mp4)、[l1-friction.mp4](../../demos/manim/rendered/l1-friction.mp4)，分别讲命令延迟和阻力 |
| [K4](../lessons/k4/index.zh-CN.md) | 概念 + L0-E 证据 | [L0-E 报告](../../reports/l0_excitation/report.zh-CN.md)及敏感度/覆盖图 | **已有 · 复用 1 段：** [l0-excitation.mp4](../../demos/manim/rendered/l0-excitation.mp4)，讲激励对比 |
| [K5](../lessons/k5/index.zh-CN.md) | 概念 + L0 证据 | [L0 报告](../../reports/l0_inertia_damping/report.zh-CN.md)、拟合路径和多起点指标 | **已有 · 复用 1 段：** [l0-fit-walk.mp4](../../demos/manim/rendered/l0-fit-walk.mp4)，讲优化路径 |
| [K6](../lessons/k6/index.zh-CN.md) | 概念 + 留出证据 | [L0 报告](../../reports/l0_inertia_damping/report.zh-CN.md)与拟合/留出划分 | **已有 · 复用 1 段：** [l0-heldout.mp4](../../demos/manim/rendered/l0-heldout.mp4)，讲留出运动预测 |
| [K7](../lessons/k7/index.zh-CN.md) | 概念 + 引用摩擦证据 | [L1 摩擦报告](../../reports/l1_friction/report.zh-CN.md)及等效参数局限 | **无需视频：** 报告图与对比表已承载补偿问题，无需另做视频 |
| [K8](../lessons/k8/index.zh-CN.md) | 概念 | 页面中的控制/迁移协议和解答 | **无需视频：** 有界协议是静态设计决定；下游整机证据随 L4 计划 |
| [L0](../lessons/l0/index.zh-CN.md) | 可运行 | [L0 固定报告](../../reports/l0_inertia_damping/report.zh-CN.md)、指标和本地运行器 | **已有 · 5 段：** [失配](../../demos/manim/rendered/l0-mismatch.mp4)、[拟合收敛](../../demos/manim/rendered/l0-fit-lands.mp4)、[拟合路径](../../demos/manim/rendered/l0-fit-walk.mp4)、[多起点](../../demos/manim/rendered/l0-fit-robust.mp4)、[留出](../../demos/manim/rendered/l0-heldout.mp4) |
| [L0-E](../lessons/l0-e/index.zh-CN.md) | 可运行 | [L0-E 冻结报告](../../reports/l0_excitation/report.zh-CN.md)及敏感度/覆盖/损失/多起点/留出产物 | **已有 · 1 段：** [l0-excitation.mp4](../../demos/manim/rendered/l0-excitation.mp4)，讲弱激励与对比 |
| [L1](../lessons/l1/index.zh-CN.md) | 可运行 | [L1 报告](../../reports/l1_servo_loaded_pendulum/report.zh-CN.md)及[摩擦报告](../../reports/l1_friction/report.zh-CN.md) | **已有 · 4 段：** [边界](../../demos/manim/rendered/l1-boundary.mp4)、[相位](../../demos/manim/rendered/l1-phase.mp4)、[留出](../../demos/manim/rendered/l1-heldout.mp4)、[摩擦](../../demos/manim/rendered/l1-friction.mp4) |
| [L1-O](../lessons/l1-o/index.zh-CN.md) | 设计草稿 | 页面中的观测噪声契约；没有已检查运行 | **计划中：** 观测噪声有明确残差问题，尚无视频或报告 |
| [L1-S](../lessons/l1-s/index.zh-CN.md) | 设计草稿 | 页面中的饱和契约；没有已检查运行 | **计划中：** 本地运行完成后再制作饱和视频 |
| [L2](../lessons/l2/index.zh-CN.md) | 设计草稿 | 耦合腿部契约；仿真器/报告待补 | **计划中：** 先有真实腿部运行，才能制作耦合与补偿视频 |
| [L3](../lessons/l3/index.zh-CN.md) | 设计草稿 | 接触契约；仿真器/报告待补 | **计划中：** 需要真实接触运行 |
| [L4](../lessons/l4/index.zh-CN.md) | 设计草稿 | 整机/控制对比契约；报告待补 | **计划中：** 部件/整机路径和控制对比需要实证 |
| [L5](../lessons/l5/index.zh-CN.md) | 设计草稿 | 参数共享契约；报告待补 | **计划中：** 独立和共享参数的比较需要实际规模实验后再制作视频 |
| [L6](../lessons/l6/index.zh-CN.md) | 设计草稿 | 结构失配/跨引擎契约；报告待补 | **计划中：** 两种失配都要有真实后端运行后才能确定素材 |

当前独立视频共有 10 段，均为短小、无配音的教学辅助；字幕和文字解释承载语言叙事。复用素材只有在本课页面写明问题和边界时才计入。L1-O、L1-S、L2–L6 仍是设计草稿；L0/L1 及整门课的独立学员验收仍待完成。

## 当前可交付路径

K0、K1、L0 和 L1 已可阅读。L0、L1 有可复现的本地 CPU 运行器和已检查报告；L1 含隔离摩擦扩展。L0-E 现在有可运行的 CPU 证据包。K2 是带推导和解析教学图的概念课，明确与实验证据分开。K3–K8 引用回答各自问题的证据，或说明无需视频的理由。其余 L 页面仍是等待数值路径的契约。

网站提供成对的中英文页面。Marimo 应用仍是本地适配器；浏览器/WASM 表面是可选项，不能从页面发布状态推断。独立学员验收仍需要真实读者指出初始失配、解释留出性能、改变一个设置并说明假设。
