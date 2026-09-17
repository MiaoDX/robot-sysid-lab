import marimo
__generated_with = "0.24.2"
app = marimo.App(width="full", app_title="L1 - Servo Loaded Pendulum")
@app.cell
def _():
    from dataclasses import replace
    from pathlib import Path
    import sys
    import marimo as mo
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from synthetic.l1_servo_loaded_pendulum import load_config, build_benchmark, fit_student, score, simulate
    return mo, plt, load_config, build_benchmark, fit_student, score, simulate, replace
@app.cell
def _(mo, load_config):
    config = load_config()
    initial_delay = mo.ui.slider(0, 0.2, value=config.initial.delay_s, step=0.005, label="Initial delay (s)")
    run_identification = mo.ui.run_button(label="Run identification")
    timeline = mo.ui.slider(0, 1, value=0.5, step=0.01, label="Playback position")
    return config, initial_delay, run_identification, timeline
@app.cell
def _(config, build_benchmark, fit_student, initial_delay, mo, run_identification, score, simulate, timeline, plt):
    data = build_benchmark(config)
    initial_q, initial_qd = simulate(config, data.validation.q_des, delay_s=initial_delay.value, q0=data.validation.q[0], qd0=data.validation.qd[0])
    if run_identification.value:
        fit = fit_student(data.fit, config)
        identified_delay = fit.params.delay_s
        state = "succeeded"
    else:
        identified_delay = None
        state = "stale — press Run identification"
    figure, axes = plt.subplots(1, 2, figsize=(10, 3.5), constrained_layout=True)
    axes[0].plot(data.validation.t, data.validation.q, label="Oracle")
    axes[0].plot(data.validation.t, initial_q, label="Initial model")
    if identified_delay is not None:
        iq, _ = simulate(config, data.validation.q_des, delay_s=identified_delay, q0=data.validation.q[0], qd0=data.validation.qd[0])
        axes[0].plot(data.validation.t, iq, "--", label="Identified")
    axes[0].axvline(data.validation.t[int(timeline.value*(len(data.validation.t)-1))], color="k", alpha=.25)
    axes[0].set(title="Validation angle", xlabel="time (s)", ylabel="q (rad)"); axes[0].legend()
    axes[1].plot(data.validation.qd, initial_qd-data.validation.qd, ".", ms=2)
    axes[1].set(title="Residual vs velocity", xlabel="qd (rad/s)", ylabel="residual")
    mo.vstack([mo.md(f"## Servo driven loaded pendulum\n**Fit state:** {state}\n\nThe delay is an effective command-boundary parameter. Presentation controls replay the completed run."), initial_delay, run_identification, timeline, figure])
    return
if __name__ == "__main__": app.run()
