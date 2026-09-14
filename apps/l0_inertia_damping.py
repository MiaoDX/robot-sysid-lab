import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full", app_title="L0 - Inertia and Damping")


@app.cell
def _():
    from dataclasses import replace
    from pathlib import Path
    import sys

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))

    from synthetic.l0_inertia_damping import (
        Params,
        load_config,
        run_l0,
        simulate,
    )

    return Params, load_config, mo, np, plt, replace, repo_root, run_l0, simulate


@app.cell
def _(mo):
    mo.Html(
        """
        <style>
          :root { --lesson-ink: #17211b; --lesson-muted: #59645d; --lesson-green: #1f6b45; }
          .lesson-hero { padding: 1.4rem 0 .7rem; border-bottom: 1px solid #d9dedb; margin-bottom: 1rem; }
          .lesson-kicker { color: var(--lesson-green); font: 700 .78rem/1.2 sans-serif; text-transform: uppercase; }
          .lesson-hero h1 { color: var(--lesson-ink); font: 650 2rem/1.15 sans-serif; margin: .35rem 0 .5rem; letter-spacing: 0; }
          .lesson-hero p { color: var(--lesson-muted); font: 1rem/1.55 sans-serif; max-width: 72ch; }
          .lesson-step { border-left: 3px solid var(--lesson-green); padding-left: .9rem; margin: 1rem 0; }
          .metric-strip { display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap: .6rem; margin: .7rem 0 1rem; }
          .metric { border: 1px solid #d9dedb; border-radius: 6px; padding: .65rem .75rem; background: #fff; }
          .metric b { display: block; color: var(--lesson-ink); font: 650 1.05rem/1.2 monospace; }
          .metric span { color: var(--lesson-muted); font: .76rem/1.3 sans-serif; }
          @media (max-width: 700px) { .metric-strip { grid-template-columns: repeat(2,minmax(0,1fr)); } }
        </style>
        <section class="lesson-hero">
          <div class="lesson-kicker">Robot SysID Lab / Lesson L0</div>
          <h1>Can motion reveal inertia and damping?</h1>
          <p>Change the Student's starting model, fit it against observed motion,
          then test it on an excitation the estimator never saw.</p>
        </section>
        """
    )
    return


@app.cell
def _(load_config, mo, repo_root):
    base_config = load_config(repo_root / "synthetic" / "l0_config.json")
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
    return base_config, damping_control, inertia_control, split_control


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
    controls
    return


@app.cell
def _(
    Params,
    base_config,
    damping_control,
    inertia_control,
    np,
    plt,
    replace,
    run_l0,
    simulate,
    split_control,
):
    preview_config = replace(
        base_config,
        nominal=Params(
            inertia=float(inertia_control.value),
            damping=float(damping_control.value),
        ),
    )
    preview_run = run_l0(preview_config)
    preview_observations = (
        preview_run.data.fit
        if split_control.value == "Fit"
        else preview_run.data.validation
    )
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
    return lesson_figure, preview_metrics, preview_run


@app.cell
def _(lesson_figure, mo, preview_metrics, preview_run, split_control):
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
            mo.md("### 3. Read the result"),
            metric_strip,
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
    result_view
    return


if __name__ == "__main__":
    app.run()
