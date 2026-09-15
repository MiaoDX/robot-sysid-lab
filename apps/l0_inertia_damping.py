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
          /* Hallmark · pre-emit critique: P4 H5 E4 S5 R4 V4 */
          :root {
            --lesson-ink: #17211b;
            --lesson-muted: #59645d;
            --lesson-green: #1f6b45;
            --lesson-blue: #1677a3;
            --lesson-warm: #d97706;
            --lesson-paper: #ffffff;
            --lesson-soft: #f3f6f4;
            --lesson-line: #d9dedb;
            --lesson-font-display: ui-sans-serif, system-ui, sans-serif;
            --lesson-font-body: ui-sans-serif, system-ui, sans-serif;
            --lesson-font-mono: ui-monospace, monospace;
          }
          html, body { overflow-x: clip; }
          .lesson-hero { padding: 1.4rem 0 .7rem; border-bottom: 1px solid var(--lesson-line); margin-bottom: 1rem; }
          .lesson-kicker { color: var(--lesson-green); font: 700 .78rem/1.2 var(--lesson-font-body); text-transform: uppercase; }
          .lesson-hero h1 { color: var(--lesson-ink); font: 650 2rem/1.15 var(--lesson-font-display); margin: .35rem 0 .5rem; letter-spacing: 0; overflow-wrap: anywhere; }
          .lesson-hero p { color: var(--lesson-muted); font: 1rem/1.55 var(--lesson-font-body); max-width: 72ch; }
        </style>
        <section class="lesson-hero">
          <div class="lesson-kicker">Robot SysID Lab / Course entry</div>
          <h1>From model mismatch to evidence</h1>
          <p>Learn why robot models drift from physical systems, what system
          identification can recover, and how held-out experiments tell us
          whether a fitted model is useful.</p>
        </section>
        """
    )
    return lesson_header


@app.cell
def _(mo):
    introduction = mo.Html(
        """
        <style>
          :root {
            --lesson-ink: #17211b;
            --lesson-muted: #59645d;
            --lesson-green: #1f6b45;
            --lesson-blue: #1677a3;
            --lesson-warm: #d97706;
            --lesson-paper: #ffffff;
            --lesson-soft: #f3f6f4;
            --lesson-line: #d9dedb;
            --lesson-font-display: ui-sans-serif, system-ui, sans-serif;
            --lesson-font-body: ui-sans-serif, system-ui, sans-serif;
            --lesson-font-mono: ui-monospace, monospace;
          }
          :host { overflow-x: clip; }
          .intro-wrap { color: var(--lesson-ink); font-family: var(--lesson-font-body); padding: .8rem 0 1.5rem; }
          .intro-grid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, .85fr); gap: 2.5rem; align-items: start; padding: 1.4rem 0 2rem; }
          .intro-label { color: var(--lesson-green); font-size: .75rem; font-weight: 750; text-transform: uppercase; margin-bottom: .55rem; }
          .intro-wrap h2 { font: 650 1.7rem/1.22 var(--lesson-font-display); letter-spacing: 0; margin: 0 0 .8rem; overflow-wrap: anywhere; }
          .intro-wrap h3 { font: 650 1.08rem/1.3 var(--lesson-font-display); letter-spacing: 0; margin: 0 0 .4rem; }
          .intro-wrap p { color: var(--lesson-muted); font-size: .98rem; line-height: 1.58; margin: 0; }
          .mismatch { border-top: 3px solid var(--lesson-warm); background: var(--lesson-soft); padding: 1rem; }
          .mismatch-flow { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: .65rem; margin-bottom: .85rem; }
          .flow-node { border: 1px solid var(--lesson-line); background: var(--lesson-paper); padding: .75rem; font-size: .88rem; font-weight: 650; text-align: center; }
          .flow-arrow { color: var(--lesson-warm); font-size: 1.25rem; font-weight: 800; }
          .mismatch-note { color: var(--lesson-ink); font-size: .84rem; line-height: 1.45; }
          .outcomes { border-top: 1px solid var(--lesson-line); border-bottom: 1px solid var(--lesson-line); display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); }
          .outcome { padding: 1.15rem 1.1rem 1.2rem 0; }
          .outcome + .outcome { border-left: 1px solid var(--lesson-line); padding-left: 1.1rem; }
          .outcome-index { color: var(--lesson-green); font: 700 .75rem/1 var(--lesson-font-mono); margin-bottom: .55rem; }
          .workflow { padding: 2rem 0; }
          .workflow-line { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 0; margin-top: 1rem; }
          .workflow-step { border-top: 2px solid var(--lesson-green); padding: .7rem .7rem .2rem 0; min-width: 0; }
          .workflow-step + .workflow-step { margin-left: .55rem; }
          .workflow-step b { display: block; color: var(--lesson-ink); font-size: .86rem; margin-bottom: .25rem; }
          .workflow-step span { color: var(--lesson-muted); font-size: .75rem; line-height: 1.35; }
          .scope-row { display: grid; grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr); gap: 2rem; padding: 1.2rem 0; border-top: 1px solid var(--lesson-line); }
          .scope-tag { color: var(--lesson-blue); font: 700 .76rem/1.3 var(--lesson-font-mono); }
          .scope-copy { color: var(--lesson-muted); font-size: .9rem; line-height: 1.55; }
          @media (max-width: 700px) {
            .intro-grid, .scope-row { grid-template-columns: minmax(0, 1fr); gap: 1rem; }
            .outcomes { grid-template-columns: minmax(0, 1fr); }
            .outcome + .outcome { border-left: 0; border-top: 1px solid var(--lesson-line); padding-left: 0; }
            .workflow-line { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .8rem; }
            .workflow-step + .workflow-step { margin-left: 0; }
          }
        </style>
        <section class="intro-wrap">
          <div class="intro-grid">
            <div>
              <div class="intro-label">Why system identification?</div>
              <h2>Your controller acts on a model. The robot acts on physics.</h2>
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

          <div class="intro-label">What SysID gives us</div>
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
            <div class="intro-label">What we actually do</div>
            <h2>One loop, repeated at increasing scale</h2>
            <div class="workflow-line">
              <div class="workflow-step"><b>1. Boundary</b><span>Name the plant, input, output, and unknowns.</span></div>
              <div class="workflow-step"><b>2. Excite</b><span>Apply motion that reveals the target dynamics.</span></div>
              <div class="workflow-step"><b>3. Observe</b><span>Record only signals available to the estimator.</span></div>
              <div class="workflow-step"><b>4. Fit</b><span>Estimate parameters inside the Student model.</span></div>
              <div class="workflow-step"><b>5. Validate</b><span>Predict a held-out motion or condition.</span></div>
              <div class="workflow-step"><b>6. Diagnose</b><span>Read residuals and add complexity only as needed.</span></div>
            </div>
          </div>

          <div class="scope-row">
            <div>
              <div class="intro-label">Why begin with L0?</div>
              <div class="scope-tag">J * qdd + b * qd = u</div>
            </div>
            <div class="scope-copy">L0 uses one rotational joint, known torque,
            ideal observations, and only two unknown parameters. This removes
            hardware and model-structure ambiguity so you can first learn the
            meaning of Oracle, Nominal, Student, fitting, held-out validation,
            and residuals. Later lessons add delay, friction, actuators, legs,
            contact, and whole robots one uncertainty class at a time.</div>
          </div>
        </section>
        """
    )
    return introduction


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
def _(damping_control, inertia_control, mo, split_control):
    controls = mo.vstack(
        [
            mo.md("### 1. Start with a model you know is imperfect"),
            mo.md(
                "The orange **Nominal** model is the Student before SysID. "
                "Move either control and predict how its motion will change."
            ),
            inertia_control,
            damping_control,
            mo.md("### 2. Choose the evidence"),
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
        <style>
          :root {{
            --lesson-ink: #17211b;
            --lesson-muted: #59645d;
            --lesson-paper: #ffffff;
            --lesson-line: #d9dedb;
            --lesson-font-body: ui-sans-serif, system-ui, sans-serif;
            --lesson-font-mono: ui-monospace, monospace;
          }}
          .metric-strip {{ display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap: .6rem; margin: .7rem 0 1rem; }}
          .metric {{ border: 1px solid var(--lesson-line); border-radius: 6px; padding: .65rem .75rem; background: var(--lesson-paper); }}
          .metric b {{ display: block; color: var(--lesson-ink); font: 650 1.05rem/1.2 var(--lesson-font-mono); }}
          .metric span {{ color: var(--lesson-muted); font: .76rem/1.3 var(--lesson-font-body); }}
          @media (max-width: 700px) {{ .metric-strip {{ grid-template-columns: repeat(2,minmax(0,1fr)); }} }}
        </style>
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
            mo.md("### 3. Read the result"),
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
            mo.md(
                """
### 4. Explain before moving on

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
def _(controls, introduction, lesson_header, mo, result_view):
    course = mo.vstack(
        [
            lesson_header,
            mo.ui.tabs(
                {
                    "01 Why SysID": introduction,
                    "02 Run L0": mo.vstack([controls, result_view], gap=1.2),
                },
                value="01 Why SysID",
                lazy=True,
                label="Lesson stage",
            ),
        ],
        gap=0.5,
    )
    course
    return


if __name__ == "__main__":
    app.run()
