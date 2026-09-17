# L1 Servo Driven Loaded Pendulum

Synthetic ideal observation: fixed base, rotary arm, point payload, gravity, and fixed PD servo. Boundary: `q_des -> PD -> effective command delay -> torque -> pendulum`. Oracle delay is hidden; fitted delay is effective and boundary dependent.

Initial delay: **0.000 s**; identified: **0.080 s**; Oracle: **0.080 s**. Validation q RMSE changes from 0.11588 to 2.0502e-16.

Estimator inputs are only `t`, `q_des`, `q`, and `qd`; torque and delayed state are Oracle diagnostics. Omitted effects include friction, saturation, compliance/backlash, sensor noise, voltage/thermal behavior, contacts, and whole-robot dynamics. This is not a motor electromagnetic model and does not establish hardware transfer.
