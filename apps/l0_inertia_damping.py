import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full", app_title="L0 - Inertia and Damping")


@app.cell
def _():
    from dataclasses import replace
    from datetime import datetime
    from pathlib import Path
    import sys
    import time

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))

    from synthetic.l0_inertia_damping import (
        Params,
        build_benchmark,
        fit_l0,
        load_config,
        simulate,
    )

    return (
        Params,
        build_benchmark,
        datetime,
        fit_l0,
        load_config,
        mo,
        np,
        plt,
        replace,
        repo_root,
        simulate,
        time,
    )


@app.cell
def _(mo):
    lesson_header = mo.Html(
        """
        <style>
          /* Hallmark · genre: editorial · macrostructure: Long Document + Workbench
           * pre-emit critique: P5 H5 E4 S5 R5 V4
           * responsive: pass · honest: pass · chrome: pass · tokens: pass
           */
          :root {
            --lesson-ink: oklch(29% 0.025 151);
            --lesson-muted: oklch(48% 0.018 151);
            --lesson-green: oklch(47% 0.105 151);
            --lesson-blue: oklch(50% 0.105 230);
            --lesson-warm: oklch(59% 0.145 57);
            --lesson-paper: oklch(99% 0.006 151);
            --lesson-paper-glass: oklch(99% 0.006 151 / .82);
            --lesson-soft: oklch(96% 0.012 151);
            --lesson-line: oklch(85% 0.014 151);
            --lesson-wash-cool: oklch(92% 0.035 225);
            --lesson-wash-warm: oklch(94% 0.045 62);
            --lesson-focus: oklch(43% 0.12 230);
            --lesson-shadow: oklch(29% 0.025 151 / .08);
            --lesson-font-display: Charter, "Bitstream Charter", Georgia, serif;
            --lesson-font-body: ui-sans-serif, system-ui, sans-serif;
            --lesson-font-mono: ui-monospace, monospace;
            --lesson-space-3xs: .25rem;
            --lesson-space-2xs: .5rem;
            --lesson-space-xs: .75rem;
            --lesson-space-sm: 1rem;
            --lesson-space-md: 1.5rem;
            --lesson-space-lg: 2rem;
            --lesson-space-xl: 3rem;
            --lesson-space-2xl: 4.5rem;
          }
          html, body { overflow-x: clip; }
          body {
            color: var(--lesson-ink);
            background-color: var(--lesson-paper);
            background-image: linear-gradient(
              145deg,
              var(--lesson-wash-cool),
              var(--lesson-paper) 42%,
              var(--lesson-paper) 68%,
              var(--lesson-wash-warm)
            );
            background-attachment: fixed;
          }
          body::before {
            position: fixed;
            inset: 0;
            z-index: -1;
            content: "";
            pointer-events: none;
            opacity: .22;
            background-image: repeating-linear-gradient(
              115deg,
              transparent 0,
              transparent 3px,
              var(--lesson-line) 4px
            );
          }
          .lesson-hero {
            padding: var(--lesson-space-xl) var(--lesson-space-lg) var(--lesson-space-lg);
            border-bottom: 1px solid var(--lesson-line);
            margin-bottom: var(--lesson-space-sm);
            background-color: var(--lesson-paper);
            background-image:
              repeating-linear-gradient(
                115deg,
                transparent 0,
                transparent 4px,
                var(--lesson-line) 5px
              ),
              linear-gradient(
                135deg,
                var(--lesson-wash-cool),
                var(--lesson-paper) 48%,
                var(--lesson-wash-warm)
              );
          }
          .lesson-kicker {
            color: var(--lesson-green);
            font: 700 .78rem/1.2 var(--lesson-font-body);
            text-transform: uppercase;
          }
          .lesson-hero h1 {
            color: var(--lesson-ink);
            font: 650 clamp(2.15rem, 5vw, 4.4rem)/1.02 var(--lesson-font-display);
            margin: var(--lesson-space-xs) 0 var(--lesson-space-sm);
            letter-spacing: 0;
            overflow-wrap: anywhere;
            min-width: 0;
            max-width: 15ch;
          }
          .lesson-hero p {
            color: var(--lesson-muted);
            font: 1.05rem/1.62 var(--lesson-font-body);
            max-width: 65ch;
            margin: 0;
          }
          .lesson-progress {
            position: sticky;
            top: var(--lesson-space-2xs);
            z-index: 20;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: var(--lesson-space-3xs) var(--lesson-space-xs);
            padding: var(--lesson-space-xs) var(--lesson-space-sm);
            margin: 0 0 var(--lesson-space-xl);
            border: 1px solid var(--lesson-line);
            border-radius: 6px;
            background-color: var(--lesson-paper-glass);
            background-image: linear-gradient(
              100deg,
              var(--lesson-wash-cool),
              var(--lesson-paper-glass) 42%,
              var(--lesson-wash-warm)
            );
            color: var(--lesson-muted);
            box-shadow: 0 8px 28px var(--lesson-shadow);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
          }
          .lesson-progress strong {
            color: var(--lesson-ink);
            font: 700 .76rem/1 var(--lesson-font-mono);
            margin-inline-end: var(--lesson-space-2xs);
          }
          .lesson-progress a {
            color: var(--lesson-muted);
            font: 650 .78rem/1 var(--lesson-font-body);
            text-decoration: none;
            white-space: nowrap;
            min-height: 44px;
            display: inline-flex;
            align-items: center;
            border-bottom: 2px solid transparent;
            outline: 2px solid transparent;
            outline-offset: 2px;
          }
          @media (hover: hover) and (pointer: fine) {
            .lesson-progress a:hover {
              color: var(--lesson-green);
              border-bottom-color: var(--lesson-green);
            }
          }
          .lesson-progress a:focus-visible {
            color: var(--lesson-ink);
            outline-color: var(--lesson-focus);
          }
          .lesson-progress a:active { color: var(--lesson-blue); }
          .lesson-chapter {
            scroll-margin-top: 6rem;
            padding: var(--lesson-space-xl) 0 var(--lesson-space-lg);
            border-top: 1px solid var(--lesson-line);
            color: var(--lesson-ink);
            font-family: var(--lesson-font-body);
          }
          .lesson-chapter:first-of-type { border-top: 0; }
          .chapter-label {
            display: block;
            color: var(--lesson-green);
            font: 700 .75rem/1.2 var(--lesson-font-mono);
            margin-bottom: var(--lesson-space-xs);
          }
          .lesson-chapter h2 {
            color: var(--lesson-ink);
            font: 650 clamp(1.65rem, 3vw, 2.45rem)/1.12 var(--lesson-font-display);
            letter-spacing: 0;
            margin: 0 0 var(--lesson-space-sm);
            overflow-wrap: anywhere;
            min-width: 0;
          }
          .chapter-lede {
            color: var(--lesson-muted);
            font: 1rem/1.6 var(--lesson-font-body);
            max-width: 68ch;
            margin: 0;
          }
          .intro-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.2fr) minmax(0, .8fr);
            gap: var(--lesson-space-xl);
            align-items: start;
            padding: var(--lesson-space-md) 0 var(--lesson-space-xl);
          }
          .intro-grid h3,
          .outcome h3,
          .role h3 {
            color: var(--lesson-ink);
            font: 650 1.08rem/1.3 var(--lesson-font-display);
            letter-spacing: 0;
            margin: 0 0 var(--lesson-space-2xs);
          }
          .intro-grid p,
          .outcome p,
          .role p {
            color: var(--lesson-muted);
            font: .96rem/1.58 var(--lesson-font-body);
            margin: 0;
          }
          .mismatch {
            border-top: 3px solid var(--lesson-warm);
            background-color: var(--lesson-soft);
            color: var(--lesson-ink);
            padding: var(--lesson-space-sm);
          }
          .mismatch-flow {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
            align-items: center;
            gap: var(--lesson-space-xs);
            margin-bottom: var(--lesson-space-xs);
          }
          .flow-node {
            border: 1px solid var(--lesson-line);
            background-color: var(--lesson-paper);
            color: var(--lesson-ink);
            padding: var(--lesson-space-xs);
            font: 650 .86rem/1.35 var(--lesson-font-body);
            text-align: center;
          }
          .flow-arrow {
            color: var(--lesson-warm);
            font: 800 1.25rem/1 var(--lesson-font-body);
          }
          .mismatch-note {
            color: var(--lesson-ink);
            font: .84rem/1.45 var(--lesson-font-body);
          }
          .outcomes {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            border-top: 1px solid var(--lesson-line);
            border-bottom: 1px solid var(--lesson-line);
          }
          .outcome { padding: var(--lesson-space-sm) var(--lesson-space-sm) var(--lesson-space-md) 0; }
          .outcome + .outcome {
            border-left: 1px solid var(--lesson-line);
            padding-left: var(--lesson-space-sm);
          }
          .outcome-index {
            color: var(--lesson-green);
            font: 700 .75rem/1 var(--lesson-font-mono);
            margin-bottom: var(--lesson-space-xs);
          }
          .workflow { padding: var(--lesson-space-xl) 0; }
          .workflow-line {
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: var(--lesson-space-xs);
            margin-top: var(--lesson-space-sm);
          }
          .workflow-step {
            border-top: 2px solid var(--lesson-green);
            padding-top: var(--lesson-space-xs);
            min-width: 0;
          }
          .workflow-step b {
            display: block;
            color: var(--lesson-ink);
            font: 650 .85rem/1.3 var(--lesson-font-body);
            margin-bottom: var(--lesson-space-3xs);
          }
          .workflow-step span {
            color: var(--lesson-muted);
            font: .75rem/1.4 var(--lesson-font-body);
          }
          .roles {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: var(--lesson-space-md);
            padding-top: var(--lesson-space-lg);
          }
          .role { border-top: 2px solid var(--lesson-line); padding-top: var(--lesson-space-sm); }
          .role:nth-child(1) { border-top-color: var(--lesson-ink); }
          .role:nth-child(2) { border-top-color: var(--lesson-warm); }
          .role:nth-child(3) { border-top-color: var(--lesson-blue); }
          .metric-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: var(--lesson-space-xs);
            margin: var(--lesson-space-sm) 0;
          }
          .metric {
            border: 1px solid var(--lesson-line);
            border-radius: 6px;
            padding: var(--lesson-space-xs);
            background-color: var(--lesson-paper);
            color: var(--lesson-ink);
          }
          .metric b {
            display: block;
            color: var(--lesson-ink);
            font: 650 1.05rem/1.2 var(--lesson-font-mono);
          }
          .metric span {
            color: var(--lesson-muted);
            font: .76rem/1.35 var(--lesson-font-body);
          }
          @media (max-width: 40rem) {
            .lesson-hero {
              padding: var(--lesson-space-lg) var(--lesson-space-sm);
            }
            .lesson-progress { position: static; padding: var(--lesson-space-2xs) var(--lesson-space-xs); }
            .lesson-progress strong { flex-basis: 100%; margin-bottom: var(--lesson-space-3xs); }
            .lesson-chapter { padding: var(--lesson-space-lg) 0; }
            .intro-grid { grid-template-columns: minmax(0, 1fr); gap: var(--lesson-space-sm); }
            .outcomes,
            .roles { grid-template-columns: minmax(0, 1fr); }
            .metric-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .outcome + .outcome { border-left: 0; border-top: 1px solid var(--lesson-line); padding-left: 0; }
            .workflow-line { grid-template-columns: repeat(2, minmax(0, 1fr)); }
          }
        </style>
        <section class="lesson-hero">
          <div class="lesson-kicker">Robot SysID Lab / L0</div>
          <h1>Make a model answer to evidence</h1>
          <p>Begin with the reason robot models drift, reduce the problem to one
          joint, then identify inertia and damping and test the result on motion
          the estimator never saw.</p>
        </section>
        <nav class="lesson-progress" aria-label="Lesson chapters">
          <strong>L0 PATH</strong>
          <a href="#why">Why</a>
          <a href="#boundary">Boundary</a>
          <a href="#experiment">Experiment</a>
          <a href="#evidence">Evidence</a>
          <a href="#limits">Limits</a>
        </nav>
        """
    )
    return lesson_header


@app.cell
def _(mo):
    introduction = mo.Html(
        """
        <section class="lesson-chapter" id="why">
          <span class="chapter-label">01 / WHY SYSID</span>
          <h2>Your controller acts on a model. The robot acts on physics.</h2>
          <p class="chapter-lede">System identification turns the gap between
          expected and observed motion into an experiment we can measure,
          explain, and use to improve prediction.</p>
          <div class="intro-grid">
            <div>
              <h3>Models begin as assumptions</h3>
              <p>A simulator, controller, or policy begins with assumed masses,
              actuator response, friction, delay, and contact. Manufacturing
              variation, payload, temperature, wear, wiring, and unmodeled
              dynamics make the observed robot move differently. SysID turns
              that mismatch into an experiment we can measure and explain.</p>
            </div>
            <div class="mismatch">
              <div class="mismatch-flow">
                <div class="flow-node">Expected motion<br>from a model</div>
                <div class="flow-arrow">&ne;</div>
                <div class="flow-node">Observed motion<br>from the plant</div>
              </div>
              <div class="mismatch-note"><strong>Model mismatch</strong> appears
              as prediction error, tracking error, unstable tuning, or a policy
              that works in simulation and fails on hardware.</div>
            </div>
          </div>

          <span class="chapter-label">WHAT SYSID GIVES US</span>
          <div class="outcomes">
            <div class="outcome">
              <div class="outcome-index">01</div>
              <h3>A useful plant model</h3>
              <p>Estimate physical or effective parameters inside a declared
              boundary, such as inertia, damping, delay, or torque response.</p>
            </div>
            <div class="outcome">
              <div class="outcome-index">02</div>
              <h3>Predictive evidence</h3>
              <p>Test the fitted Student on motions and conditions that were not
              used during fitting. A low fit loss alone is not enough.</p>
            </div>
            <div class="outcome">
              <div class="outcome-index">03</div>
              <h3>A map of what is missing</h3>
              <p>Use residual patterns and sensitivity to decide whether the
              experiment, observations, optimizer, or model structure must change.</p>
            </div>
          </div>

          <div class="workflow">
            <span class="chapter-label">THE REPEATED LOOP</span>
            <h2>Six steps, repeated at increasing scale</h2>
            <div class="workflow-line">
              <div class="workflow-step"><b>1. Boundary</b><span>Name the plant, input, output, and unknowns.</span></div>
              <div class="workflow-step"><b>2. Excite</b><span>Apply motion that reveals the target dynamics.</span></div>
              <div class="workflow-step"><b>3. Observe</b><span>Record only signals available to the estimator.</span></div>
              <div class="workflow-step"><b>4. Fit</b><span>Estimate parameters inside the Student model.</span></div>
              <div class="workflow-step"><b>5. Validate</b><span>Predict a held-out motion or condition.</span></div>
              <div class="workflow-step"><b>6. Diagnose</b><span>Read residuals and add complexity only as needed.</span></div>
            </div>
          </div>

        </section>

        """
    )
    return introduction


@app.cell
def _(mo):
    boundary_header = mo.Html(
        """
        <section class="lesson-chapter" id="boundary">
          <span class="chapter-label">02 / DECLARE THE BOUNDARY</span>
          <h2>Begin with one joint and two unknowns</h2>
          <p class="chapter-lede">L0 removes hardware and model-structure
          ambiguity so the full identification loop stays visible.</p>
        </section>
        """
    )
    boundary_equation = mo.vstack(
        [
            mo.md(
                r"""
                \[
                \Large J\ddot{q} + b\dot{q} = u
                \]
                """
            ).style(
                {
                    "color": "var(--lesson-blue)",
                }
            ),
            mo.md(
                "**Known:** time, applied torque, position, and velocity. "
                "**Unknown:** inertia $J$ and viscous damping $b$. Larger $J$ "
                "resists acceleration; larger $b$ removes more energy while "
                "the joint moves."
            ),
        ],
        gap=0.5,
    ).style(
        {
            "border-top": "1px solid var(--lesson-line)",
            "border-bottom": "1px solid var(--lesson-line)",
            "padding": "var(--lesson-space-md) 0",
        }
    )
    boundary_roles = mo.Html(
        """
        <div class="roles">
          <div class="role"><h3>Oracle</h3><p>The hidden plant that generates
          observations. Its true parameters are reserved for evaluation.</p></div>
          <div class="role"><h3>Nominal Student</h3><p>The plausible but wrong
          model available before identification. It is the orange baseline.</p></div>
          <div class="role"><h3>Identified Student</h3><p>The same model after
          fitting J and b from the declared fit observations.</p></div>
        </div>
        """
    )
    boundary = mo.vstack(
        [boundary_header, boundary_equation, boundary_roles], gap=0.0
    )
    return boundary


@app.cell
def _(build_benchmark, load_config, mo, repo_root):
    base_config = load_config(repo_root / "synthetic" / "l0_config.json")
    prepared_data = build_benchmark(base_config)
    inertia_control = mo.ui.slider(
        start=0.02,
        stop=0.14,
        step=0.005,
        value=base_config.nominal.inertia,
        label="Nominal inertia J (kg m^2)",
        show_value=True,
        full_width=True,
    )
    damping_control = mo.ui.slider(
        start=0.005,
        stop=0.12,
        step=0.005,
        value=base_config.nominal.damping,
        label="Nominal damping b (N m s/rad)",
        show_value=True,
        full_width=True,
    )
    split_control = mo.ui.radio(
        options=["Fit", "Validation"],
        value="Validation",
        label="Trajectory",
        inline=True,
    )
    return base_config, damping_control, inertia_control, prepared_data, split_control


@app.cell
def _(mo):
    experiment_intro = mo.Html(
        """
        <section class="lesson-chapter" id="experiment">
          <span class="chapter-label">03 / RUN THE EXPERIMENT</span>
          <h2>Move the wrong model, then let the data answer</h2>
          <p class="chapter-lede">First predict what higher inertia or damping
          will do to the orange trajectory. Each slider change fits the Student
          again against the same Oracle dataset; switching Fit and Validation
          only changes which completed result you inspect.</p>
        </section>
        """
    )
    return experiment_intro


@app.cell
def _(damping_control, inertia_control, mo, split_control):
    controls = mo.vstack(
        [
            mo.md("### Set the pre-identification Student"),
            mo.md(
                "The orange **Nominal** model is the Student before SysID. "
                "Move one control at a time and predict how its motion will change."
            ),
            inertia_control,
            damping_control,
            mo.md("### Select the evidence view"),
            split_control,
            mo.callout(
                mo.md(
                    "**Fit** data is visible to the estimator. **Validation** "
                    "uses a different input and is scored only after fitting."
                ),
                kind="info",
            ),
        ],
        gap=1.0,
    )
    return controls


@app.cell
def _(
    Params,
    base_config,
    datetime,
    damping_control,
    fit_l0,
    inertia_control,
    prepared_data,
    replace,
    time,
):
    preview_config = replace(
        base_config,
        nominal=Params(
            inertia=float(inertia_control.value),
            damping=float(damping_control.value),
        ),
    )
    started_at = time.perf_counter()
    preview_run = fit_l0(preview_config, prepared_data)
    fit_elapsed_s = time.perf_counter() - started_at
    fit_completed_at = datetime.now().astimezone().strftime("%H:%M:%S")
    fit_state = "succeeded" if preview_run.fit.success else "failed"
    return fit_completed_at, fit_elapsed_s, fit_state, preview_config, preview_run


@app.cell
def _(preview_run, split_control):
    preview_observations = (
        preview_run.data.fit
        if split_control.value == "Fit"
        else preview_run.data.validation
    )
    preview_metrics = (
        (
            preview_run.nominal_fit_metrics,
            preview_run.identified_fit_metrics,
        )
        if split_control.value == "Fit"
        else (
            preview_run.nominal_validation_metrics,
            preview_run.identified_validation_metrics,
        )
    )
    return preview_metrics, preview_observations


@app.cell
def _(
    np,
    plt,
    preview_config,
    preview_observations,
    preview_run,
    simulate,
    split_control,
):
    nominal_q, nominal_qd = simulate(
        preview_config.nominal,
        preview_observations.t,
        preview_observations.u,
        q0=preview_config.q0,
        qd0=preview_config.qd0,
    )
    identified_q, identified_qd = simulate(
        preview_run.fit.params,
        preview_observations.t,
        preview_observations.u,
        q0=preview_config.q0,
        qd0=preview_config.qd0,
    )
    lesson_figure, lesson_axes = plt.subplots(
        2, 2, figsize=(12, 7), constrained_layout=True
    )
    lesson_colors = {
        "oracle": "#17211b",
        "nominal": "#d97706",
        "identified": "#1677a3",
    }
    for lesson_axis, observed, nominal, identified, ylabel in (
        (
            lesson_axes[0, 0],
            preview_observations.q,
            nominal_q,
            identified_q,
            "position q (rad)",
        ),
        (
            lesson_axes[0, 1],
            preview_observations.qd,
            nominal_qd,
            identified_qd,
            "velocity qd (rad/s)",
        ),
    ):
        lesson_axis.plot(
            preview_observations.t,
            observed,
            color=lesson_colors["oracle"],
            label="Oracle",
            linewidth=1.8,
        )
        lesson_axis.plot(
            preview_observations.t,
            nominal,
            color=lesson_colors["nominal"],
            label="Nominal",
            linewidth=1.3,
        )
        lesson_axis.plot(
            preview_observations.t,
            identified,
            color=lesson_colors["identified"],
            label="Identified",
            linewidth=1.3,
        )
        lesson_axis.set(xlabel="time (s)", ylabel=ylabel)
        lesson_axis.grid(alpha=0.2)
        lesson_axis.legend(frameon=False)

    lesson_axes[1, 0].plot(
        preview_observations.t,
        preview_observations.u,
        color="#2f7d4d",
        linewidth=1.5,
    )
    lesson_axes[1, 0].set(
        xlabel="time (s)", ylabel="torque u (N m)", title="Applied excitation"
    )
    lesson_axes[1, 0].grid(alpha=0.2)

    parameter_names = ["inertia J", "damping b"]
    parameter_x = np.arange(2)
    parameter_width = 0.24
    lesson_axes[1, 1].bar(
        parameter_x - parameter_width,
        [preview_config.truth.inertia, preview_config.truth.damping],
        parameter_width,
        label="Oracle",
        color=lesson_colors["oracle"],
    )
    lesson_axes[1, 1].bar(
        parameter_x,
        [preview_config.nominal.inertia, preview_config.nominal.damping],
        parameter_width,
        label="Nominal",
        color=lesson_colors["nominal"],
    )
    lesson_axes[1, 1].bar(
        parameter_x + parameter_width,
        [preview_run.fit.params.inertia, preview_run.fit.params.damping],
        parameter_width,
        label="Identified",
        color=lesson_colors["identified"],
    )
    lesson_axes[1, 1].set(
        xticks=parameter_x,
        xticklabels=parameter_names,
        ylabel="parameter value",
        title="Parameter recovery",
    )
    lesson_axes[1, 1].grid(axis="y", alpha=0.2)
    lesson_axes[1, 1].legend(frameon=False)
    lesson_figure.suptitle(
        f"{split_control.value}: Oracle vs Student models", fontsize=15
    )
    plt.close(lesson_figure)
    return lesson_figure


@app.cell
def _(
    fit_completed_at,
    fit_elapsed_s,
    fit_state,
    lesson_figure,
    mo,
    preview_metrics,
    preview_run,
    split_control,
):
    nominal_metrics, identified_metrics = preview_metrics
    metric_strip = mo.Html(
        f"""
        <div class="metric-strip">
          <div class="metric"><b>{nominal_metrics.q_mae:.3g}</b><span>{split_control.value} nominal q MAE</span></div>
          <div class="metric"><b>{identified_metrics.q_mae:.3g}</b><span>{split_control.value} identified q MAE</span></div>
          <div class="metric"><b>{preview_run.fit.params.inertia:.5f}</b><span>identified inertia J</span></div>
          <div class="metric"><b>{preview_run.fit.params.damping:.5f}</b><span>identified damping b</span></div>
        </div>
        """
    )
    result_view = mo.vstack(
        [
            mo.Html(
                """
                <section class="lesson-chapter" id="evidence">
                  <span class="chapter-label">04 / READ THE EVIDENCE</span>
                  <h2>Fit explains the estimate. Validation tests its use.</h2>
                  <p class="chapter-lede">The blue Identified curve should
                  follow the hidden Oracle on the chirp used for fitting and
                  on the held-out multisine used only for evaluation.</p>
                </section>
                """
            ),
            metric_strip,
            mo.md(
                f"`Oracle dataset reused` · fit completed at "
                f"`{fit_completed_at}` · `{fit_state}` in "
                f"`{fit_elapsed_s * 1000:.0f} ms` · optimizer evaluations: "
                f"`{preview_run.fit.nfev}`"
            ),
            lesson_figure,
            mo.callout(
                mo.md(
                    "The blue Identified curve should overlap the black Oracle "
                    "on both splits. Changing the orange baseline does not change "
                    "the hidden plant. In this matched, noise-free lesson, a "
                    "successful fit returns to the same physical parameters."
                ),
                kind="success",
            ),
            mo.Html(
                """
                <section class="lesson-chapter" id="limits">
                  <span class="chapter-label">05 / NAME THE LIMITS</span>
                  <h2>A successful fit is a bounded claim</h2>
                  <p class="chapter-lede">L0 proves the loop under a matched,
                  noise-free model. It does not prove that two parameters can
                  explain an actuator, a leg, or a complete robot.</p>
                </section>
                """
            ),
            mo.md(
                """
### Explain before moving on

1. Where does the orange curve first reveal the wrong model?
2. Why is improvement on **Validation** stronger evidence than fit error alone?
3. Name two effects that could break this result on a real servo.

This L0 plant omits controller and torque calibration effects, delay,
saturation, nonlinear friction, compliance, contact, and sensor noise. The next
lesson adds one mismatch at a time so its residual signature remains visible.
                """
            ),
        ],
        gap=1.0,
    )
    return result_view


@app.cell
def _(
    boundary,
    controls,
    experiment_intro,
    introduction,
    lesson_header,
    mo,
    result_view,
):
    course = mo.vstack(
        [
            lesson_header,
            introduction,
            boundary,
            experiment_intro,
            controls,
            result_view,
        ],
        gap=0.8,
    )
    course
    return


if __name__ == "__main__":
    app.run()
