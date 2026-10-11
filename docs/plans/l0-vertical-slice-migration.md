# L0 垂直切片迁移计划

## Plan Ledger

- Plan status: DONE
- Session scope: l0-vertical-slice-migration
- Parent plan: `handbook/plan.md`
- Child plans: none
- Last updated: 2026-09-28
- Current slice: 第 02 课 L0 垂直切片已实现并完成自动化与浏览器验收。
- Next action: none; 后续课程迁移另立计划。
- Blocked on: none
- Do not touch from this session: 第 01、03–13 课；L0-E/L1 实验；MuJoCo、Manim、WASM、全站 vendor；旧 Pages 发布根的切换和旧目录删除。

## Goal

用一个完整的 L0 垂直切片验证课程重构的核心链路：

```text
冻结旧实现 → sysid_lab 包 → 可审计 artifact → sysid-lab run 02
→ course/ 第 02 课 → Marimo 调用同一实现 → shadow build 与回滚验证
```

切片完成后，新的第 02 课可以在独立环境中运行、生成可追溯产物并构建页面；旧的 L0 命令、报告和课程页面仍然可用。这个结果作为后续第 01、04、05、08 课迁移的模板。

## Source Evidence

- [`handbook/plan.md`](../../handbook/plan.md) - 已确定的新目录、连续课号、artifact 单一来源和批次方向。
- [`handbook/template.md`](../../handbook/template.md) - manifest、课程页面结构、证据标签、网页不运行模型等形式约束。
- [`STATUS.md`](../../STATUS.md) - 当前 L0 已有可复现模型、报告、Marimo、notebook 和测试，但独立学习者验收仍未完成。
- [`synthetic/l0_inertia_damping.py`](../../synthetic/l0_inertia_damping.py) - 当前唯一的 L0 数值实现和旧 CLI。
- [`tests/test_l0_inertia_damping.py`](../../tests/test_l0_inertia_damping.py) - 当前数值、泄漏边界、报告和 Marimo 合同。
- [`tools/build_course.py`](../../tools/build_course.py) 与 [Pages workflow](../../.github/workflows/pages.yml) - 当前构建器和发布根仍以 `docs/` 为中心。
- `docs/lessons/l0/`、`apps/l0_inertia_damping.py`、`reports/l0_inertia_damping/` - 当前 L0 的完整四页学习路径、交互入口和已生成证据。

## Decisions Already Made

- 先做第 02 课的完整垂直切片，再扩展整个批次 0；不把全站迁移作为第一步。
- 新包的 canonical lesson slug 为 `02-inertia-damping`；CLI 同时接受 `02` 和该 slug。
- `sysid_lab` 成为 L0 的 canonical Python 实现；迁移期间保留 `synthetic.l0_inertia_damping` 兼容 shim，旧入口不立即删除。
- 新 artifact 与旧 `reports/l0_inertia_damping` 并行生成。新旧结果用显式容差比较，不比较包含时间、commit 或运行环境的原始文件字节。
- 稳定教学 artifact 入库；运行缓存和临时自定义配置输出不入库。当前 `.gitignore` 对 `artifacts/` 的整目录忽略需要在实现切片中改成精确规则，并为 `02-inertia-damping` 写出 tracked allowlist。
- canonical artifact 只由冻结默认配置生成；`--config` 的自定义运行必须输出到用户指定目录，不能覆盖发布 artifact。
- 课程切片迁移 L0 的完整四页叙事（入口、README、00–03 支撑页），不为了验证架构强行重写成单页。
- 第 02 课保留多页形态：`index` 是课程壳，`README/00–03` 是支撑页；统一课号、slug、资源路径，并让整套页面共同通过 shadow build。
- 新站先做 shadow build 到独立输出目录；GitHub Pages 仍上传现有 `docs/`，直到新构建根和旧链接策略另有计划并通过验证。
- 本计划是 intuitive-flow 的规划 checkpoint，不生成 `.planning/*` 或 GSD phase 文件。

## Open Decisions

本切片没有需要用户现在裁决的产品决定。以下事项保留到后续全站迁移计划：旧 URL 是否提供重定向、何时把 Pages 根切到 `course/` 构建输出、是否删除旧 `docs/lessons/l0` 和 `reports/`。

## Non-Goals

- 不迁移第 01、03–13 课、概念卡、术语表、参考书目或全站首页。
- 不改 L0 的模型、默认配置、拟合目标、数据划分、结论或数值基准。
- 不把 L0-E 改成加噪声实验；不实现 L1、L1 摩擦、MuJoCo、mjlab、GPU 或硬件路径。
- 不在本切片实现 Pyodide/Marimo WASM、浏览器内拟合、uPlot/Plotly 自托管、Manim 浅色重渲染或全站数字占位符系统。
- 不删除旧目录、旧命令、旧报告、旧测试或切换 Pages 发布根。
- 不把独立学习者验收冒充为本切片的工程完成条件；保留现有维护者验证边界。

## Smallest Demo

在干净环境中运行：

```bash
uv sync --frozen
uv run sysid-lab run 02
```

命令生成 `artifacts/02-inertia-damping/`，包含冻结配置副本、指标、拟合路径、报告所需图像、课程引用的数据和 `manifest.json`。页面构建后，打开第 02 课中文页可以读到同一批产物；Marimo 文件可以从 `sysid_lab` 调用同一 runner，并保留现有显式 `Run identification` 交互。

## Fuller Demo

同时保留旧路径并运行旧命令：

```bash
python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping
uv run sysid-lab run 02 --output-dir artifacts/02-inertia-damping
uv run python tools/build_course.py --source-root course --output-dir site-preview
```

新旧运行的 identified `J`、`b`、fit/validation 指标、关键轨迹和成功状态在声明容差内一致；新页面在桌面和窄屏下可读，所有本地链接和双语锚点有效；旧页面、旧 Marimo、Manim 读取的旧路径仍能运行。

## Artifact Contract

本切片只定义能支撑第 02 课的最小协议，后续课程不得在未更新协议前自行扩展。

- `artifacts/02-inertia-damping/manifest.json` 必须包含：`schema_version`、lesson slug/课号、生成命令、git commit、配置路径和 SHA-256、Python/依赖版本、随机种子（无随机性时明确写 `null`）、生成时间、以及除 manifest 自身外每个文件的相对路径、角色和 SHA-256。
- `generated_at`、git commit、运行时和环境字段属于 provenance；数值 parity 使用去除这些字段后的 canonical payload 比较，避免每次运行因为元数据变化而误报。
- 每个文件标记 `public` 或 `evaluation`。`fit_student`、`fit_l0` 等拟合 API 只能接收公开 observations、公开初值和边界；Oracle truth、验证集和内部信号不得作为拟合参数传入。报告可按当前 L0 教学目的展示真值，但 manifest 必须标明其角色。
- 课程页面只读取已生成的 artifact，不在 JavaScript 中实现模型、仿真或拟合。若页面需要完整曲线，产物必须提供确定性的 `trajectory.json` 或等价轨迹文件；不能假设 `metrics.json` 已经包含页面所需数据。
- 第 02 课的 tracked allowlist 至少覆盖 `manifest.json`、冻结配置副本、公开指标、公开轨迹、课程需要的图像和双语 Markdown 报告；运行日志、临时自定义结果和重复生成缓存继续 ignored。实现后用 `git check-ignore` 和 `git ls-files` 验证 clean clone 能拿到 allowlist 内所有文件。
- artifact Markdown 报告不得保留指向旧 `reports/` 或旧课程目录的悬空相对链接。报告只链接 artifact 内文件或由课程页提供的站点相对链接；链接检查器必须从生成的 HTML 扫描所有 `href`、`src`、`poster` 和字幕路径，并验证课程引用的资源闭包全部落在 `site-preview` 或明确声明的静态根中。
- canonical 默认运行和自定义运行分开。自定义 `--config` 必须显式指定输出目录，不能覆盖 `artifacts/02-inertia-damping`。

## Vertical Slices

1. **基线快照**：在改动前运行当前测试、构建检查和 L0 默认命令到临时目录（如 `.tmp/l0-old`），记录 Python/依赖版本、报告与 JSON/PNG/fitting journey 的 checksum、关键指标和当前工作树状态。旧的 tracked `reports/l0_inertia_damping/` 只做非破坏性存在性 smoke check；基线后 `git diff --exit-code` 必须通过。旧树是回滚依据，不覆盖或重写它。
2. **canonical Python 包**：建立 `sysid_lab` 包，把 L0 实现迁入或薄适配为 canonical API；保留 `synthetic.l0_inertia_damping` re-export shim。`Params`、`load_config`、`simulate`、`fit_student`、`run_l0` 和报告生成能力在迁移期间保持兼容。
3. **artifact writer 与 manifest**：实现第 02 课 artifact 导出，明确 public/evaluation 文件角色、manifest 自身不参与 checksum、确定性 payload 比较和 `.gitignore` 的 tracked/ignored 边界。生成的数据、图和报告链接基准必须能在新课程输出目录中解析。
4. **CLI**：在 `pyproject.toml` 和 `uv.lock` 中建立最小可安装入口 `sysid-lab`；preflight 冻结当前已验证的 Python minor 版本，并明确 core、interactive、docs 的依赖组。支持 `run 02`、slug、显式输出目录和默认冻结配置。默认运行不能写入旧报告目录或覆盖 canonical artifact。
5. **新课程切片**：创建 `course/lessons/02-inertia-damping/`，迁移 L0 四页双语内容和资源路径；页面使用第 02 课编号、证据标签和 artifact 链接，保持已有事实和练习语义。增加 `apps/02_inertia_damping.py` 或等价新命名入口调用 `sysid_lab`，不复制模型代码；旧 `apps/l0_inertia_damping.py` 和 `notebooks/l0_inertia_damping.ipynb` 保留并继续通过 shim 工作。
6. **shadow builder**：以扩展现有 `tools/build_course.py` 的 additive 参数实现 `--source-root course --output-dir site-preview`；不改变无参数旧行为。新参数先生成 preview，再由同一参数加 `--check` 比较已生成输出。只对新切片检查双语配对、锚点、本地链接、artifact/manifest 引用、禁用词和页面体积；旧 `docs/` builder 和 Pages workflow 继续工作。
7. **闭环验证与 checkpoint**：在干净 `uv` 环境运行新 CLI、manifest 校验、新旧 parity、focused tests、shadow build 和窄屏/桌面浏览器检查；同时运行旧命令和现有全套测试。只有这些证据齐全，才把新切片标为可复制模板；旧目录清理和全站迁移另立计划。

## Acceptance Criteria

- [x] preflight 已冻结 Python minor 版本、core/interactive/docs 依赖组和 `uv.lock`；`uv sync --frozen --extra docs --extra interactive --extra dev` 能安装依赖，`uv run sysid-lab run 02` 成功写出 canonical artifact。
- [x] 新 artifact 的 manifest 满足字段、checksum、角色和 provenance 规则；manifest 自身不被纳入 checksum；重复默认运行的 canonical payload 稳定。
- [x] 新 runner 与旧 runner 的 parity schema 和容差已写入验证记录：参数 `J/b` 使用 `rtol=1e-8, atol=1e-10`；标量 fit/validation 指标使用 `rtol=1e-7, atol=1e-9`；`t/u/q/qd` 轨迹使用 `rtol=1e-7, atol=1e-9`。比较字段、样本数量和 success 状态固定。
- [x] `fit_student` 等公共拟合入口通过 focused test 证明不接收 Oracle truth、验证数据或隐藏信号；默认 L0 数据划分和配置版本不变。
- [x] 第 02 课的入口、README、00–03 支撑页和双语页面在 `course/lessons/02-inertia-damping/` 可达；链接、图片、证据标签、heading anchors 和报告引用在 shadow build 中解析。
- [x] Marimo 入口调用 `sysid_lab` 的 canonical runner，保留显式运行和 stale 状态行为；不包含第二份模型实现。旧 Marimo、notebook 和旧 CLI 仍通过 shim 工作。
- [x] 旧 L0 CLI、旧 L0 页面、旧 Marimo、旧 notebook、旧报告、Manim 相关旧路径和现有测试仍可运行；没有切换 Pages 根或删除旧目录。
- [x] 桌面和窄屏浏览器检查通过：页面无水平溢出，中文/英文切换有效，artifact 图和公式加载，控制台无新增错误。
- [x] `git check-ignore`/`git ls-files` 证明 tracked allowlist 在 clean clone 中存在，运行缓存不会污染版本库；shadow link checker 扫描生成 HTML 后所有本地 `href/src/poster/track` 都能解析。
- [x] `handbook/status.md` 未在本切片创建；完成证据记录在 [verification record](l0-vertical-slice-migration-verification.md)。

## Verification

基线与完成检查至少包含：

```bash
python -m pytest -q
python tools/build_course.py --check
python -m synthetic.l0_inertia_damping --output-dir .tmp/l0-old
uv sync --frozen
uv run sysid-lab run 02 --output-dir artifacts/02-inertia-damping
uv run pytest -q tests/test_l0_vertical_slice.py
uv run python tools/build_course.py --source-root course --output-dir site-preview
uv run python tools/build_course.py --source-root course --output-dir site-preview --check
uv run python -m json.tool notebooks/l0_inertia_damping.ipynb >/dev/null
```

并人工检查：

- 新旧 metrics、轨迹和 manifest payload 的 parity 对比报告；
- 基线与新运行后的 `git diff --exit-code`，以及 `git check-ignore`/`git ls-files` 的 tracked allowlist 结果；
- 新页面在 1280 px 和 375 px 宽度下的首屏、图像、公式、链接和语言切换；
- 自定义 `--config` 不覆盖 canonical artifact；旧命令和旧页面的回滚路径；
- `course/` 构建输出不包含 `handbook/`、旧计划或开发资料；生成 HTML 的所有本地 `href/src/poster/track` 都能解析。

## Risks And Assumptions

- 当前 `artifacts/` 被 `.gitignore` 整目录忽略，而现有 CLI 默认也写入该目录；实现必须先分清 tracked 教学产物和 ignored 运行缓存，不能把“生成成功”误当成“可发布”。
- 当前旧报告含相对链接和评估真值；复制到新 artifact 时可能产生死链或角色混淆，必须在 manifest/页面检查中显式处理。
- 图像和 HTML 可能受 NumPy/Matplotlib/Python 版本影响，因此 parity 以数值和结构化 payload 为主，图像只检查存在、尺寸和可读性，不要求跨环境字节相同。
- 当前 `tools/build_course.py`、测试和 Pages workflow 都硬编码旧目录；shadow builder 必须隔离旧路径，避免为了一个切片破坏既有全站合同。
- `uv.lock`、Python minor 版本和依赖 extras 目前不存在；它们是 preflight 的输入，不应在执行中临时决定。
- 第 01 课若以后直接引用第 02 课结果，会与线性学习顺序冲突；本计划不解决它，后续内容计划必须提供独立预计算 fixture 或调整依赖。

## Planning Loop Result

- Loop status: complete
- Round 1: migration scout and acceptance/skeptic scout independently检查了当前 L0 实现、构建器、Pages、测试、artifact 忽略规则和课程四页结构。
- Round 2: skeptic 复查本计划；已接受 tracked allowlist、临时基线目录、逐字段 parity 容差、旧 notebook/app 兼容、builder additive 参数、依赖冻结和资源闭包检查。
- Accepted: 以第 02 课为垂直切片；先基线、再 canonical 包、artifact/manifest、CLI、四页课程、shadow build、回滚验证；保留旧入口。
- Parked: 全站迁移、编号重排、L0-E 加噪声、L1/多体、WASM、vendor、Manim、Pages 根切换、旧 URL 删除、独立学员验收。
- Rejected: 先重写全站 builder、先删除旧目录、把所有批次 0 工具建设塞进一个 slice、用原始报告字节比较代替结构化 parity。
- User decisions: 先做 L0 完整垂直切片；使用 intuitive-flow 风格计划与 agent planning loop；第 02 课保留多页形态；本轮只产出计划，不执行实现。
- Grill batch: 用户确认保留多页形态；没有剩余会改变范围、公共边界、验收或 rollout 的问题。

## Preflight Contract

- Preflight status: READY FOR EXECUTION
- Task source: user prompt + this plan
- Canonical source: `docs/plans/l0-vertical-slice-migration.md`
- Route: main direct via `intuitive-flow`, with no worker delegation
- Goal: 在保留旧入口的前提下，交付可运行、可追溯、可构建的第 02 课 L0 垂直切片。
- Scope: `sysid_lab` canonical 包、artifact/manifest、`sysid-lab run 02`、第 02 课多页课程和 Marimo 入口、additive shadow builder、全套 parity 与页面验证。
- Non-goals: 全站迁移、其他课程、L0-E/L1 改造、WASM、vendor、Manim、Pages 根切换、旧目录删除。
- Acceptance: 以本计划的 Artifact Contract、Acceptance Criteria 和 Verification 为准；旧 CLI、旧页面、旧 Marimo、旧 notebook 和现有测试必须继续通过。
- Required product proof: 新 CLI 生成 canonical artifact；shadow site 在 1280 px 与 375 px 下可读，双语切换、图像、公式、链接和控制台检查通过。
- Stop conditions: manifest/public-evaluation 边界未定、parity 超差未解释、clean `uv` 安装失败、artifact 资源闭包不完整、旧入口回归失败，或必需浏览器检查无法完成。
- Execution: main session owns implementation, checkpoints, verification and commit boundaries. Main session handles this bounded slice directly.
- Approval: 用户已授权本次 preflight 和计划提交；实现阶段仍以本契约和本计划为唯一范围。

## Closeout

- Status: DONE
- Verification record: `docs/plans/l0-vertical-slice-migration-verification.md`
- Browser evidence: `.tmp/browser-proof/final-responsive-{mobile,tablet,desktop}.png` and `final-chinese.png` from the local preview.
- Parked: full-site migration, old URL cleanup, Pages root switch, and other lesson migrations remain outside this slice.

## GSD Handoff Trigger

本计划未触发 GSD；已由 `intuitive-flow` 完成执行和验证。只有用户明确要求 GSD handoff，才将本文件作为输入转换为 GSD 计划。
