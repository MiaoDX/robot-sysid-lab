/* L0 lecture data. The complete authored lesson remains in docs/lessons/l0/index.md. */
(() => {
  const zh = document.documentElement.lang === "zh-CN";
  const copy = zh ? {
    lesson: "L0 · 估计关节的惯量与阻尼",
    coverKicker: "L0 · 第一节实验",
    coverTitle: "让模型从偏差走向验证",
    coverLede: "用一段已知力矩估计惯量和阻尼，再把模型放到没有见过的新运动上。",
    route: [["问题", "初始模型为什么会漂移"], ["实验", "怎样让参数可区分"], ["证据", "留出运动是否预测得准"], ["判断", "结果适用于什么条件"]],
    mismatchKicker: "01 · 先看偏差",
    mismatchTitle: "相同力矩，为什么会得到不同运动",
    mismatchCaption: "模型偏差看起来是什么样？",
    mismatchNote: "白色是真实系统，橙色是初始模型。相同输入没有消除参数误差。",
    mismatchObs: [["位置", "两条轨迹逐渐分开", "模型的惯量和阻尼还不准确"], ["速度", "下方刻度保持相同", "差异来自响应，不是坐标缩放"], ["下一步", "保留一段新运动", "拟合后还要检查预测"]],
    boundaryKicker: "02 · 声明边界",
    boundaryTitle: "先把模型、输入和观测说清楚",
    equationNote: "这个实验只估计两个参数。实际力矩 u 已知，记录 q 和 q̇。",
    parameter: [["惯量 J", "决定同样净力矩下有多难加速。"], ["阻尼 b", "决定同样速度下有多大的黏性阻力。"]],
    boundaryFoot: "没有重力、非黏性摩擦或传感器噪声。真实系统与待拟合模型使用相同方程，便于核对恢复结果。",
    dataKicker: "03 · 设计数据",
    dataTitle: "一组数据用于拟合，另一组数据留到最后",
    fitData: ["拟合", "扫频", "让关节经历不同快慢的运动，估计 J 和 b", "用于调参数"],
    validationData: ["验证", "多正弦", "换一种频率组合，检查模型能否解释新运动", "不参与调参"],
    dataTakeaway: "如果两组数据都被拿来调参，最后的分数就不能代表留出预测。",
    fitKicker: "04 · 看拟合",
    fitTitle: "拟合让模型贴近已知运动，但还没有完成验证",
    fitCaption: "拟合真的改善了预测吗？",
    fitRows: [["惯量 J", "0.09500000", "0.06500000"], ["阻尼 b", "0.01800000", "0.05500000"]],
    fitHead: ["量", "初始模型", "辨识后模型"],
    fitNote: "蓝色是辨识后模型，已接近真实系统。这个结果只说明拟合数据被重现得很好。",
    validationKicker: "05 · 看留出证据",
    validationTitle: "真正的问题是：固定参数后，能预测新运动吗",
    reportAlt: "L0 拟合与验证曲线",
    validationCaption: "报告：拟合、验证、输入和残差",
    metricsHead: ["留出验证", "q MAE / rad", "q̇ MAE / rad/s"],
    metrics: [["拟合 / 初始模型", "4.3107227", "1.4136074"], ["拟合 / 辨识后模型", "1.56e−14", "1.23e−14"], ["验证 / 初始模型", "2.7396426", "0.87716149"], ["验证 / 辨识后模型", "1.83e−14", "2.03e−14"]],
    validationNote: "这里约 10⁻¹⁴ 的误差来自相同方程和理想观测。它支持这次留出预测，不代表真实测量也能达到同样精度。",
    quizKicker: "06 · 暂停自检",
    quizTitle: "先判断，再看证据是否支持",
    quizQuestion: "只展示拟合曲线，下一项最需要补什么？",
    quizChoices: [["A", "再跑一次相同的拟合", false], ["B", "检查没有参与调参的新运动", true]],
    quizAnswer: "选 B。拟合曲线只能说明模型匹配了用于调参的数据；留出运动才检查预测是否迁移。",
    limitKicker: "07 · 收拢条件",
    limitTitle: "这次结果说明了什么，又没有说明什么",
    limits: [["已支持", "在已知实际力矩、理想观测和正确模型结构下，估计出的 J、b 能预测另一种输入。"], ["仍待检查", "真实关节还可能有延迟、限幅、其他摩擦、柔性和测量噪声。"], ["下一步", "L1 加入位置控制器和未知延迟，继续检查图纸看不到的时序效应。"]],
    next: "下一课 · L1 指令延迟",
    notes: ["开篇只说问题和路线，不先念完整方法。", "让视线在白色和橙色之间移动，强调输入相同而响应不同。", "先读方程，再指出本实验刻意排除的效应。", "用左右两组数据说明训练和验证的责任不同。", "先看参数变化，再提醒拟合证据的边界。", "先看验证列，再看报告中的残差和 MAE。", "给学员暂停时间；答案回到拟合与留出的区别。", "收尾保留边界，下一课承接控制器和延迟。"]
  } : {
    lesson: "L0 · Estimate joint inertia and damping",
    coverKicker: "L0 · First experiment",
    coverTitle: "Move a model from mismatch to validation",
    coverLede: "Estimate inertia and damping from a known torque, then put the model on a motion it has not seen.",
    route: [["Question", "Why does the initial model drift"], ["Experiment", "How can parameters be separated"], ["Evidence", "Does held-out motion predict well"], ["Judgment", "What conditions does this support"]],
    mismatchKicker: "01 · Start with mismatch",
    mismatchTitle: "The same torque can produce different motion",
    mismatchCaption: "What does the mismatch look like?",
    mismatchNote: "White is the observed system; orange is the initial model. The same input does not remove parameter error.",
    mismatchObs: [["Position", "The traces drift apart", "The model's inertia and damping are still wrong"], ["Velocity", "The scale stays shared", "The difference is response, not rescaling"], ["Next", "Reserve a new motion", "Fitting still needs a prediction check"]],
    boundaryKicker: "02 · State the boundary",
    boundaryTitle: "Name the model, input, and observations first",
    equationNote: "This experiment estimates two parameters. Applied torque u is known; q and q̇ are recorded.",
    parameter: [["Inertia J", "How hard the joint is to accelerate under the same net torque."], ["Damping b", "The viscous resistance at the same velocity."]],
    boundaryFoot: "There is no gravity, non-viscous friction, or sensor noise. The generating system and fitted model share the equation so recovery can be checked.",
    dataKicker: "03 · Design the data",
    dataTitle: "Fit on one dataset, reserve the other",
    fitData: ["Fit", "Chirp", "Vary motion speed to estimate J and b", "Used to tune"],
    validationData: ["Validation", "Multisine", "Change the frequency mix to test a new motion", "Held out"],
    dataTakeaway: "If both datasets tune the parameters, the final score cannot represent held-out prediction.",
    fitKicker: "04 · Inspect the fit",
    fitTitle: "Fitting matches known motion, but it has not finished validation",
    fitCaption: "Did fitting actually improve the prediction?",
    fitRows: [["Inertia J", "0.09500000", "0.06500000"], ["Damping b", "0.01800000", "0.05500000"]],
    fitHead: ["Quantity", "Initial model", "Identified model"],
    fitNote: "Blue is the identified model and is close to the true system. This only says the fitting motion was reproduced well.",
    validationKicker: "05 · Inspect held-out evidence",
    validationTitle: "The real question: can fixed parameters predict new motion",
    reportAlt: "L0 fitting and validation curves",
    validationCaption: "Report: fitting, validation, input, and residuals",
    metricsHead: ["Held-out model", "q MAE / rad", "q̇ MAE / rad/s"],
    metrics: [["Fit / initial model", "4.3107227", "1.4136074"], ["Fit / identified model", "1.56e−14", "1.23e−14"], ["Validation / initial model", "2.7396426", "0.87716149"], ["Validation / identified model", "1.83e−14", "2.03e−14"]],
    validationNote: "Errors around 10⁻¹⁴ come from a shared equation and ideal observations. This supports the held-out prediction here, not the same accuracy on hardware.",
    quizKicker: "06 · Pause and check",
    quizTitle: "Make the judgment, then ask what supports it",
    quizQuestion: "If you show only the fitting curve, what evidence is missing?",
    quizChoices: [["A", "Run the same fitting again", false], ["B", "Check motion held out from tuning", true]],
    quizAnswer: "B. A fitting curve only shows a match to tuning data; held-out motion checks whether the prediction transfers.",
    limitKicker: "07 · Gather the conditions",
    limitTitle: "What this result supports, and what it does not",
    limits: [["Supported", "With known applied torque, ideal observations, and the correct model structure, the estimated J and b predict another input."], ["Still open", "A real joint may add delay, saturation, other friction, flexibility, and measurement noise."], ["Next", "L1 adds a position controller and unknown delay to study timing effects a drawing cannot show."]],
    next: "Next · L1 command delay",
    notes: ["Open with the question and route. Do not read the full method list.", "Move attention between white and orange: same input, different response.", "Read the equation, then name the effects this experiment deliberately excludes.", "Use the two datasets to separate tuning responsibility from validation responsibility.", "Show the parameter change, then state the limit of fitting evidence.", "Start with the validation columns, then point to residuals and MAE.", "Give the learner time to pause. Bring the answer back to fit versus held out.", "Close with conditions and hand off to the controller and delay in L1."]
  };

  const esc = (value) => String(value).replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[char]));
  const arrow = () => `<svg class="signal-arrow" viewBox="0 0 80 32" aria-hidden="true"><path d="M4 16h61M52 6l13 10-13 10" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const video = (name, caption, poster) => {
    const en = `../../demos/manim/rendered/${name}.mp4`;
    const image = `../../demos/manim/rendered/${poster || name}.png`;
    const enTrack = `../site/subtitles/${name}.en.vtt`;
    const zhTrack = `../site/subtitles/${name}.zh-CN.vtt`;
    return `<figure class="clip"><video controls playsinline preload="metadata" poster="${image}"><source src="${en}" type="video/mp4"><track kind="subtitles" label="English" src="${enTrack}" srclang="en"${zh ? "" : " default"}><track kind="subtitles" label="中文" src="${zhTrack}" srclang="zh-CN"${zh ? " default" : ""}></video><figcaption><span>${esc(caption)}</span><a href="${image}">${zh ? "查看静帧" : "View still"}</a></figcaption></figure>`;
  };
  const slideHeading = (kicker, title, extra = "", cover = false) => `<div class="slide-heading"><p class="kicker">${esc(kicker)}</p><h1${cover ? ' class="cover-title"' : ""}>${title}</h1>${extra}</div>`;
  const observations = (items) => `<div class="observations">${items.map(([label, strong, body], index) => `<div class="observation" data-step="${index + 1}"><div class="label">${esc(label)}</div><strong>${esc(strong)}</strong><p>${esc(body)}</p></div>`).join("")}</div>`;
  const waveform = (kind) => {
    const points = Array.from({length: 241}, (_, i) => {
      const t = i / 240;
      const y = kind === "chirp"
        ? Math.sin(2 * Math.PI * (t + 5 * t * t))
        : .6 * Math.sin(2 * Math.PI * 2 * t) + .4 * Math.sin(2 * Math.PI * 7 * t);
      return `${i ? "L" : "M"}${(8 + 304 * t).toFixed(2)} ${(38 - 28 * y).toFixed(2)}`;
    }).join(" ");
    return `<figure class="input-schematic"><svg viewBox="0 0 320 76" aria-hidden="true"><path d="${points}" fill="none" stroke="currentColor" stroke-width="2.5"/></svg><figcaption>${zh ? "输入形式示意" : "Schematic input"}</figcaption></figure>`;
  };
  const slides = [
    { chapter: 0, className: "cover", notes: copy.notes[0], render: () => `${slideHeading(copy.coverKicker, esc(copy.coverTitle), `<svg class="cover-underline" viewBox="0 0 280 14" aria-hidden="true"><path d="M3 8c80-5 165-3 273-6" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"/></svg>`, true)}<div class="slide-body"><p class="lede">${esc(copy.coverLede)}</p><div class="route-map" data-step="2">${copy.route.map(([name, detail]) => `<div class="route-stop"><b>${esc(name)}</b><span>${esc(detail)}</span></div>`).join("")}</div></div>` },
    { chapter: 0, notes: copy.notes[1], render: () => `${slideHeading(copy.mismatchKicker, esc(copy.mismatchTitle))}<div class="slide-body evidence-layout"><div data-step="1">${video("l0-mismatch", copy.mismatchCaption)}<p class="evidence-note">${esc(copy.mismatchNote)}</p></div>${observations(copy.mismatchObs)}</div>` },
    { chapter: 1, notes: copy.notes[2], render: () => `${slideHeading(copy.boundaryKicker, esc(copy.boundaryTitle))}<div class="slide-body"><div class="signal-flow" data-step="1"><div class="signal-node"><small>${zh ? "输入" : "Input"}</small><strong>${zh ? "实际力矩 u" : "Applied torque u"}</strong><small>${zh ? "已知，单位 N m" : "Known, N m"}</small></div>${arrow("")}<div class="signal-node model"><small>${zh ? "模型" : "Model"}</small><strong class="equation" data-math="J\\ddot q + b\\dot q = u"></strong><small>${zh ? "待估计 J 与 b" : "Estimate J and b"}</small></div>${arrow("")}<div class="signal-node"><small>${zh ? "观测" : "Observations"}</small><strong>${zh ? "q、q̇" : "q, q̇"}</strong><small>${zh ? "角位置与角速度" : "Position and velocity"}</small></div></div><p class="boundary-note" data-step="2">${esc(copy.equationNote)}</p><div class="parameter-definitions" data-step="3">${copy.parameter.map(([name, text]) => `<div><b>${esc(name)}</b><p>${esc(text)}</p></div>`).join("")}</div><p class="takeaway" data-step="4">${esc(copy.boundaryFoot)}</p></div>` },
    { chapter: 1, notes: copy.notes[3], render: () => `${slideHeading(copy.dataKicker, esc(copy.dataTitle))}<div class="slide-body"><div class="data-split"><article class="dataset" data-step="1"><span class="tag">${esc(copy.fitData[0])}</span><h3>${esc(copy.fitData[1])}</h3>${waveform("chirp")}<p>${esc(copy.fitData[2])}</p><p class="purpose">${esc(copy.fitData[3])}</p></article><article class="dataset validation" data-step="2"><span class="tag">${esc(copy.validationData[0])}</span><h3>${esc(copy.validationData[1])}</h3>${waveform("multisine")}<p>${esc(copy.validationData[2])}</p><p class="purpose">${esc(copy.validationData[3])}</p></article></div><p class="takeaway risk" data-step="3">${esc(copy.dataTakeaway)}</p></div>` },
    { chapter: 2, notes: copy.notes[4], render: () => `${slideHeading(copy.fitKicker, esc(copy.fitTitle))}<div class="slide-body evidence-layout"><div><div data-step="1">${video("l0-fit-lands", copy.fitCaption)}</div><div class="table-wrap" data-step="2"><table><thead><tr>${copy.fitHead.map((head) => `<th>${esc(head)}</th>`).join("")}</tr></thead><tbody>${copy.fitRows.map((row) => `<tr><td>${esc(row[0])}</td><td class="initial-cell">${esc(row[1])}</td><td class="identified-cell">${esc(row[2])}</td></tr>`).join("")}</tbody></table></div></div><p class="takeaway" data-step="3">${esc(copy.fitNote)}</p></div>` },
    { chapter: 3, notes: copy.notes[5], render: () => `${slideHeading(copy.validationKicker, esc(copy.validationTitle))}<div class="slide-body"><div class="evidence-layout"><div data-step="1">${video("l0-heldout", zh ? "固定参数，预测预先留出的多正弦运动" : "Fixed parameters predict the reserved multisine motion")}</div><div data-step="2"><div class="table-wrap"><table class="metric-table"><thead><tr>${copy.metricsHead.map((head) => `<th>${esc(head)}</th>`).join("")}</tr></thead><tbody>${copy.metrics.slice(2).map((row, index) => `<tr class="${index ? "identified-row" : ""}"><td>${zh ? (index ? "辨识后模型" : "初始模型") : (index ? "Identified" : "Initial")}</td><td>${esc(row[1])}</td><td>${esc(row[2])}</td></tr>`).join("")}</tbody></table></div><a class="report-link" href="../../reports/l0_inertia_damping/report${zh ? ".zh-CN" : ""}.html">${zh ? "查看完整实验报告" : "Full experiment report"}</a></div></div><p class="takeaway" data-step="3">${esc(copy.validationNote)}</p></div>` },
    { chapter: 4, notes: copy.notes[6], render: () => `${slideHeading(copy.quizKicker, esc(copy.quizTitle))}<div class="slide-body"><p class="quiz-question">${esc(copy.quizQuestion)}</p><div class="choices" data-step="1">${copy.quizChoices.map(([letter, text, correct]) => `<button class="choice" type="button" data-correct="${correct}" aria-pressed="false"><span>${letter}</span><b>${esc(text)}</b></button>`).join("")}</div><div class="answer" data-step="2" aria-live="polite"><i data-lucide="circle-check"></i><div><p>${esc(copy.quizAnswer)}</p><p>${zh ? "如果根据验证结果继续调参，最终评估需要另留数据。" : "If validation informs more tuning, reserve fresh data for final evaluation."}</p></div></div></div>` },
    { chapter: 4, notes: copy.notes[7], render: () => `${slideHeading(copy.limitKicker, esc(copy.limitTitle))}<div class="slide-body"><div class="limits">${copy.limits.map(([label, text], index) => `<div class="limit-row" data-step="${index + 1}"><b>${esc(label)}</b><p>${esc(text)}</p></div>`).join("")}</div></div>` },
    { chapter: 4, className: "summary", notes: zh ? "先收拢实验闭环，再用 L1 的未知延迟提出下一课的问题。" : "Gather the experiment cycle, then introduce the unknown delay in L1.", render: () => `${slideHeading(zh ? "L0 · 本节小结" : "L0 · Takeaway", zh ? "估计参数之后，要让新运动来检验" : "After estimating parameters, let new motion test them")}<div class="slide-body"><div class="summary-flow" data-step="1"><b>${zh ? "已知力矩" : "Known torque"}</b>${arrow()}<b>${zh ? "估计 J、b" : "Estimate J, b"}</b>${arrow()}<b>${zh ? "留出预测" : "Held-out prediction"}</b></div><p class="takeaway" data-step="2">${zh ? "拟合说明匹配；留出说明预测；实验边界限定结论。" : "Fit supports a match. Held-out data tests prediction. The boundary limits the claim."}</p><a class="next-lesson" data-step="2" href="${zh ? "../lessons/l1/index.zh-CN.html" : "../lessons/l1/index.html"}"><span class="link-label">${esc(copy.next)}</span><i data-lucide="arrow-right"></i></a></div>` }
  ];
  const ids = ["opening", "mismatch", "boundary", "data", "fit", "validation", "check", "limits", "summary"];
  const steps = [2, 3, 4, 3, 3, 3, 2, 3, 2];
  slides.forEach((item, index) => { item.id = ids[index]; item.steps = steps[index]; });
  const segments = zh ? ["问题", "实验设计", "拟合", "留出验证", "自检与收尾"] : ["Question", "Experiment", "Fitting", "Validation", "Takeaway"];
  window.presentationData = { slides, segments, lang: zh ? "zh-CN" : "en" };
})();
