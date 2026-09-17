"""L1 guided lesson: explicit submission, then replay of a completed CPU run."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full", app_title="L1 · Servo and loaded pendulum")


@app.cell
def _():
    from dataclasses import replace
    from datetime import datetime
    from pathlib import Path
    import base64
    import io
    import sys
    import time

    import marimo as mo
    import matplotlib.pyplot as plt

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from synthetic.l1_servo_loaded_pendulum import (
        Params,
        load_config,
        machine_svg,
        run_l1,
    )

    return (
        Params,
        base64,
        datetime,
        io,
        load_config,
        machine_svg,
        mo,
        plt,
        replace,
        run_l1,
        time,
    )


@app.cell
def _(mo):
    mo.Html("""
    <style>
    /* Hallmark · inherited L0 editorial system · long lesson + workbench
       pre-emit critique: P4 H4 E4 S5 R5 V4 */
    :root {
      --l1-ink: #263b30; --l1-muted: #53635a; --l1-line: #ced8cf;
      --l1-paper: #fcfdfb; --l1-wash: #edf3ee; --l1-accent: #32664a;
      --l1-display: Charter, "Bitstream Charter", Georgia, serif;
      --l1-body: ui-sans-serif, system-ui, sans-serif;
      --l1-space: 1rem;
    }
    html, body { overflow-x: clip; }
    body { background: var(--l1-paper); color: var(--l1-ink); font-family: var(--l1-body); }
    .l1 { max-width: 1100px; margin: auto; padding: var(--l1-space); }
    .l1 h1, .l1 h2 { font-family: var(--l1-display); font-style: normal;
      overflow-wrap: anywhere; min-width: 0; line-height: 1.15; }
    .l1 h1 { font-size: clamp(2rem, 5vw, 3.7rem); max-width: 20ch; }
    .l1 h2 { font-size: 1.65rem; margin: 1.5rem 0 .8rem; }
    .l1 p { margin: .8rem 0; max-width: 76ch; line-height: 1.65; }
    .l1 .eyebrow { color: var(--l1-accent); letter-spacing: .12em; font-size: .8rem; }
    .l1 .pair { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--l1-space); }
    .l1 img, .l1 svg { display: block; width: 100%; max-width: 100%; height: auto; }
    .l1 .machine { max-width: 700px; margin: auto; }
    .l1 .boundary { border-left: 3px solid var(--l1-accent); padding: var(--l1-space); background: var(--l1-wash); }
    .l1 .muted { color: var(--l1-muted); }
    .l1 table { border-collapse: collapse; width: 100%; font-size: .9rem; }
    .l1 td, .l1 th { text-align: left; padding: .55rem .25rem; border-bottom: 1px solid var(--l1-line); overflow-wrap: anywhere; }
    .l1 button { white-space: nowrap; }
    @media (max-width: 600px) { .l1 .pair { grid-template-columns: minmax(0, 1fr); } .l1 { padding: .5rem; } }
    </style>
    <article class="l1">
    <p class="eyebrow">SYNTHETIC LAB 1 · COMMAND → ACTUATOR → BODY</p>
    <h1>A correct shape can still move at the wrong time.</h1>
    <p>A CAD model tells us where the mass is. It does not tell us when a servo's
    torque reaches that mass. Here we hold the mechanics and controller fixed
    and identify one omitted effect: a delay after the controller.</p>
    <h2>01 · Meet the machine</h2>
    <p>A fixed base holds a rotary servo, a uniform rigid arm, and a point payload.
    Gravity pulls downward. Angle zero points down; positive angle moves the
    payload to the right. This is a synthetic machine with ideal observations.</p>
    <div class="machine">
    <svg viewBox="0 0 620 260" role="img" aria-label="Fixed base and servo axis, arm pointing down-right to a payload, downward gravity, positive angle from downward vertical">
      <defs><marker id="intro-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0 0 L7 3 L0 6" fill="var(--l1-accent)"/></marker></defs>
      <path d="M160 30 H270 V72 H160 Z" fill="var(--l1-line)"/>
      <rect x="195" y="50" width="60" height="42" rx="4" fill="var(--l1-wash)" stroke="var(--l1-ink)"/>
      <circle cx="225" cy="80" r="9" fill="var(--l1-ink)"/>
      <path d="M225 80 L295 220" stroke="var(--l1-accent)" stroke-width="12"/>
      <circle cx="295" cy="220" r="17" fill="var(--l1-ink)"/>
      <path d="M225 80 V222 M225 130 Q239 130 247 124" fill="none" stroke="var(--l1-muted)" stroke-dasharray="4 3"/>
      <path d="M440 92 V165" stroke="var(--l1-accent)" stroke-width="3" marker-end="url(#intro-arrow)"/>
      <g fill="var(--l1-ink)" font-size="16" font-family="var(--l1-body)">
        <text x="62" y="38">Fixed base</text><text x="276" y="64">Servo body / axis</text>
        <text x="302" y="162">Rigid arm</text><text x="321" y="228">Point payload</text>
        <text x="453" y="128">Gravity</text><text x="236" y="153">q</text>
      </g>
    </svg></div>
    <h2>02 · Put the delay at the right boundary</h2>
    <p class="boundary">q_des + measured position → fixed PD controller → delayed torque command → pendulum → encoder q and derived qd</p>
    <p>The full controller command is <code>kp × (q_des − q) − kd × velocity</code>.
    Delay shifts this torque history, including feedback, before the plant sees it.
    Gains, geometry, gravity, sampling and reset state stay known. Fitting receives
    only <code>t, q_des, q, qd</code>; true torque and internal controller state are
    evaluation-only diagnostics. Encoder velocity uses centered differences, with
    one-sided differences at the endpoints.</p>
    <h2>03 · Predict, then identify</h2>
    <p>The default Initial model assumes zero delay. Move its delay setting and
    predict whether the mismatch should shrink. This changes the pending setup;
    only <strong>Run identification</strong> submits it. The optimizer has its own
    fixed starting guess, independent of the displayed baseline.</p>
    <p>Fit uses a chirp that sweeps frequency. A separate reversal command with a
    different phase/frequency composition is held out. Both start from the same
    known reset. The fitter never sees validation observations or scores.</p>
    </article>
    """)
    return


@app.cell
def _(load_config, mo):
    base_config = load_config()
    initial_delay = mo.ui.slider(
        start=base_config.lower.delay_s,
        stop=base_config.upper.delay_s,
        value=base_config.initial.delay_s,
        step=base_config.model.dt,
        label="Initial delay (s)",
        show_value=True,
        full_width=True,
    )
    run_identification = mo.ui.button(
        value=(0, base_config.initial.delay_s),
        on_click=lambda previous: (previous[0] + 1, float(initial_delay.value)),
        label="Run identification",
        kind="success",
    )
    timeline = mo.ui.slider(
        start=0,
        stop=100,
        step=1,
        value=50,
        label="Timeline (%)",
        show_value=True,
        full_width=True,
    )
    machine_split = mo.ui.dropdown(
        options=["fit", "validation"], value="validation", label="Machine split"
    )
    signal_view = mo.ui.dropdown(
        options=[
            "Angle",
            "Angular velocity",
            "Torque diagnostics",
            "Residual vs time",
            "Residual vs velocity",
        ],
        value="Angle",
        label="Signal view",
    )
    return (
        base_config,
        initial_delay,
        machine_split,
        run_identification,
        signal_view,
        timeline,
    )


@app.cell
def _(initial_delay, mo, run_identification):
    mo.vstack([initial_delay, run_identification])
    return


@app.cell
def _(Params, base_config, datetime, replace, run_identification, run_l1, time):
    # Only submitted values enter this cell. No timeline/view/slider dependencies.
    submission_id, submitted_delay = run_identification.value
    completed_run = None
    fit_error = None
    elapsed_s = 0.0
    completed_at = None
    if submission_id:
        _started = time.perf_counter()
        try:
            completed_run = run_l1(
                replace(base_config, initial=Params(submitted_delay))
            )
            completed_at = (
                datetime.now().astimezone().isoformat(timespec="milliseconds")
            )
        except (ValueError, RuntimeError, FloatingPointError) as _error:
            fit_error = str(_error)
        elapsed_s = time.perf_counter() - _started
    return (
        completed_at,
        completed_run,
        elapsed_s,
        fit_error,
        submission_id,
        submitted_delay,
    )


@app.cell
def _(
    completed_at,
    completed_run,
    elapsed_s,
    fit_error,
    initial_delay,
    mo,
    submission_id,
    submitted_delay,
):
    _current = float(initial_delay.value) == submitted_delay
    if fit_error:
        _state = f"Failed: {fit_error}. Adjust the pending setup and retry."
    elif completed_run is None:
        _state = "Not run. Choose an Initial delay, then press Run identification."
    elif not completed_run.fit.success:
        _state = "Fit failed to converge. The displayed run is diagnostic only."
    elif not _current:
        _state = "Stale: pending Initial delay differs from the completed run. Press Run identification to replace it."
    else:
        _state = "Succeeded · current completed run."
    mo.Html(
        f'<div class="l1"><p id="fit-status" role="status">{_state}</p>'
        f'<p id="run-receipt">Completed run #{submission_id if completed_run else 0} · '
        f"{completed_at or 'no completion yet'} · {elapsed_s:.3f} s</p>"
        '<p class="muted">Changing the pending setup preserves the displayed completed run. '
        "Playback and signal selection do not fit or simulate.</p></div>"
    )
    return


@app.cell
def _(machine_split, mo, signal_view, timeline):
    mo.vstack([timeline, mo.hstack([machine_split, signal_view], wrap=True)])
    return


@app.cell
def _(
    base64,
    completed_run,
    io,
    machine_split,
    machine_svg,
    mo,
    plt,
    signal_view,
    timeline,
):
    if completed_run is None:
        _display = mo.md(
            "Run identification to unlock recorded machine playback and fit / validation evidence."
        )
    else:
        _run = completed_run
        _index = round(timeline.value / 100 * (len(_run.data.fit.t) - 1))
        _machine = machine_svg(_run, machine_split.value, _index)
        _frame_rows = "".join(
            f"<tr><td>{_role.title()}</td><td>{_tr.q[_index]:.4f}</td><td>{_tr.qd[_index]:.4f}</td></tr>"
            for _role, _tr in _run.trajectories[machine_split.value].items()
        )
        _frame_readout = (
            f"<p>Recorded {machine_split.value} time: {_run.data.fit.t[_index]:.3f} s</p>"
            '<table aria-label="Recorded frame values"><thead><tr><th>Role</th><th>q (rad)</th><th>qd (rad/s)</th></tr></thead>'
            f"<tbody>{_frame_rows}</tbody></table>"
        )
        _images = []
        for _split in ("fit", "validation"):
            _obs = getattr(_run.data, _split)
            _fig, _ax = plt.subplots(figsize=(6, 3.6), layout="constrained")
            if signal_view.value == "Angle":
                _ax.plot(
                    _obs.t,
                    _obs.q_des,
                    color="#788879",
                    linestyle=":",
                    label="Target q_des",
                )
            for _role, _label, _color, _style, _marker in (
                ("oracle", "Oracle · solid", "#17211b", "-", None),
                ("initial", "Initial model", "#bb6b0d", "-", None),
                ("identified", "Identified · dashed + markers", "#1677a3", "--", "o"),
            ):
                _tr = _run.trajectories[_split][_role]
                _x = _obs.t
                _y = _tr.q
                _ylabel = "angle (rad)"
                if signal_view.value == "Angular velocity":
                    _y, _ylabel = _tr.qd, "qd (rad/s)"
                elif signal_view.value == "Torque diagnostics":
                    _y, _ylabel = _tr.torque, "torque (N m), evaluation only"
                    if _role == "oracle":
                        _ax.plot(
                            _x,
                            _tr.command_torque,
                            ":",
                            color=_color,
                            label="Oracle pre-delay command",
                        )
                elif signal_view.value in ("Residual vs time", "Residual vs velocity"):
                    if _role == "oracle":
                        continue
                    _y, _ylabel = _tr.q - _obs.q, "q prediction − Oracle (rad)"
                    if signal_view.value == "Residual vs velocity":
                        _x = _obs.qd
                _ax.plot(
                    _x,
                    _y,
                    color=_color,
                    linestyle=_style,
                    marker=_marker,
                    markevery=max(1, len(_x) // 15),
                    markersize=3,
                    markerfacecolor="white",
                    linewidth=1.5,
                    label=_label,
                )
                _ax.scatter([_x[_index]], [_y[_index]], color=_color, s=24, zorder=5)
            if signal_view.value != "Residual vs velocity":
                _ax.axvline(_obs.t[_index], color="#929d95", linewidth=0.8)
            _ax.set(
                xlabel="Oracle qd (rad/s)"
                if signal_view.value == "Residual vs velocity"
                else "time (s)",
                ylabel=_ylabel,
                title="Fit · chirp"
                if _split == "fit"
                else "Validation · held-out reversals",
            )
            _ax.grid(alpha=0.18)
            _ax.legend(fontsize=7, loc="best")
            _buffer = io.BytesIO()
            _fig.savefig(_buffer, format="png", dpi=130)
            plt.close(_fig)
            _encoded = base64.b64encode(_buffer.getvalue()).decode("ascii")
            _images.append(
                f'<img src="data:image/png;base64,{_encoded}" alt="{_split} {signal_view.value} from completed run"/>'
            )
        _display = mo.Html(
            '<section class="l1"><h2>04 · Replay the recorded machine</h2>'
            "<p>Synthetic, ideal observation. Oracle: solid black; Initial: orange; Identified: blue dashed with hollow markers. "
            "Coincident curves remain distinguishable. Angle and velocity labels come from the selected sample.</p>"
            f'<div class="machine" id="machine-playback">{_machine}{_frame_readout}</div>'
            "<h2>05 · Compare fit and held-out evidence</h2>"
            "<p>Oracle torque and pre-delay commands are privileged diagnostics, never fitting inputs. "
            "Repeating signed residual lobes around reversals suggest timing mismatch. "
            "A velocity-correlated residual alone does not prove friction.</p>"
            f'<div class="pair">{"".join(_images)}</div></section>'
        )
    _display
    return


@app.cell
def _(base_config, completed_run, mo):
    _model = base_config.model
    _rows = [
        ("Uniform arm mass", f"{_model.arm_mass:g} kg", "Shared / fixed"),
        ("Point payload", f"{_model.payload_mass:g} kg", "Shared / fixed"),
        ("Arm length", f"{_model.arm_length:g} m", "Shared / fixed"),
        ("Gravity", f"{_model.gravity:g} m/s²", "Shared / fixed"),
        ("PD gains kp / kd", f"{_model.kp:g} / {_model.kd:g}", "Shared / fixed"),
        ("Sampling", f"{_model.dt:g} s", "Shared / fixed"),
        (
            "Oracle delay",
            f"{base_config.truth.delay_s:g} s",
            "Hidden from fitting; evaluation only",
        ),
        (
            "Delay search bounds",
            f"{base_config.lower.delay_s:g}–{base_config.upper.delay_s:g} s",
            "Public",
        ),
        (
            "Optimizer start",
            f"{base_config.optimizer_start.delay_s:g} s",
            "Public; independent of Initial model",
        ),
    ]
    _metrics = ""
    if completed_run is not None:
        _rows.extend(
            [
                (
                    "Initial delay in completed run",
                    f"{completed_run.config.initial.delay_s:.5f} s",
                    "Learner baseline",
                ),
                (
                    "Identified effective delay",
                    f"{completed_run.fit.params.delay_s:.5f} s",
                    "Fitted on chirp only",
                ),
            ]
        )
        for _name, _before, _after in (
            ("Fit", completed_run.initial_fit, completed_run.identified_fit),
            (
                "Validation",
                completed_run.initial_validation,
                completed_run.identified_validation,
            ),
        ):
            _metrics += f"<p>{_name}: q RMSE {_before.q_rmse:.5g} → {_after.q_rmse:.5g} rad; qd RMSE {_before.qd_rmse:.5g} → {_after.qd_rmse:.5g} rad/s.</p>"
    _table = "".join(
        f"<tr><td>{_name}</td><td>{_value}</td><td>{_role}</td></tr>"
        for _name, _value, _role in _rows
    )
    mo.Html(
        f'<section class="l1"><h2>06 · Keep the parameter roles separate</h2>{_metrics}'
        "<table><thead><tr><th>Quantity</th><th>Value</th><th>Role</th></tr></thead>"
        f"<tbody>{_table}</tbody></table><p>Default matched benchmark gates: delay error ≤ 1 ms; "
        "held-out q and qd RMSE improve by at least 90%. Near-zero error demonstrates a matched "
        "synthetic model, not hardware transfer.</p></section>"
    )
    return


@app.cell
def _(mo):
    mo.Html("""<section class="l1"><h2>07 · Try to explain the evidence</h2>
    <p>Before changing Initial delay from zero toward 0.08 s, predict the direction
    of the residual change. Submit, compare the two trajectory columns, then use
    Residual vs velocity to explain one pattern. Why does the fitted delay stay
    the same when only the displayed baseline changes? The optimizer's starting
    guess and fit observations did not change.</p>
    <p>The local loss slice in the fixed report checks whether nearby delay
    candidates fit worse. Very slow commands can make that minimum shallow:
    choosing informative excitation matters as much as choosing an optimizer.</p>
    <h2>08 · Know where the model ends</h2>
    <p>The fitted delay is effective and depends on this command boundary and
    sampling. This is not a motor-electromagnetic or whole-robot simulation.
    It omits friction, saturation, compliance, backlash, sensor noise, voltage,
    temperature and contact; it does not establish hardware transfer.</p>
    <p>Next, introduce friction or saturation only when residual evidence calls
    for it. Then carry the same command / observation / validation discipline to
    a fixed-base leg, where gravity and coupled joints complicate interpretation.</p>
    </section>""")
    return


if __name__ == "__main__":
    app.run()
