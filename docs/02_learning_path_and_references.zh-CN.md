# 学习路径与参考资料

项目旨在建立简短的共同语言并开展实践实验，不要求每位机器人工程师成为系统辨识专家。

## 建议的团队学习顺序

### A — 动力学与反馈直觉

掌握足以理解二阶系统、阻尼、共振、带宽、延迟和频率响应的基础。

推荐：Åström 与 Murray 的 [Feedback Systems](https://fbsbook.org/)，以及 MIT OpenCourseWare 的 [Engineering Dynamics](https://ocw.mit.edu/)。重点看质量—弹簧—阻尼系统、传递函数、Bode/频率响应、极点与阻尼、反馈稳定性与带宽。

### B — 系统辨识概念

推荐 MIT 2.160 *Identification, Estimation and Learning*（通过 MIT OpenCourseWare 查找）；Ljung 的 *System Identification: Theory for the User* 可作为深入参考。

重点看实验设计、持续激励、模型结构、最小二乘与预测误差、可辨识性、验证和残差。

### C — 机器人实践材料

主要参考：

- [BAM：Better Actuator Models](https://github.com/rhoban/bam)
- [PACE sim-to-real](https://github.com/leggedrobotics/pace-sim2real)
- Microduck RL：查找 Pollen Robotics / Hugging Face 的 Microduck 仓库
- [mjlab](https://github.com/mujocolab/mjlab)
- [MuJoCo](https://github.com/google-deepmind/mujoco)

深入参考包括 SPI-Active（主动激励与信息驱动辨识）、Pinocchio（刚体动力学回归器），以及 FIGAROH（动力学辨识与校准流程）。

## 完成入门后应该能回答

1. 系统边界是什么？
2. 模型类别是什么？
3. 哪些量是参数，哪些是隐藏状态？
4. 为什么这个激励有信息量？
5. 两组参数能否解释同一份数据？
6. 拟合参数具有物理意义，还是仅为仿真等效值？
7. 模型能否预测留出轨迹？
8. 残差中还剩什么结构？
9. 下一步需要更多优化，还是更丰富模型？
10. 辨识参考模型如何连接域随机化与 RL？

## 课程路线

[课程地图](course/index.zh-CN.html)是主要总览。三个前缀表示不同类型的进展：

| 路线 | 编号 | 目的 |
|---|---|---|
| 知识 | `K0-K8` | 从动机到仿真迁移的概念 |
| 合成实验 | `L0-L6` | 从单关节到跨仿真失配的受控实验 |
| 硬件迁移 | `H0-H2` | 执行器台架、小机器人、完整人形 |

`L0` 表示实验课 0，不是混合路线中的第一个等级。每阶段有意只增加一两类不确定性。知识和实验共同推进；硬件阶段在对应实验与安全规程就绪后开始。
