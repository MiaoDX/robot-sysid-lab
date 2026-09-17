# L1: Servo driven loaded pendulum

A fixed base, rotary arm, point payload, gravity, and fixed PD servo turn a desired position `q_des` into torque. The hidden effect is command delay after the PD law. The Oracle delay is an effective, boundary dependent parameter, not a motor constant.

The fit uses a chirp; validation is a held out reversal trajectory. Compare the zero delay Initial model with the Identified Student and inspect residuals versus time and velocity. Change the initial delay or excitation, then press **Run identification** to create a new result.

The experiment is synthetic and ideal. Friction, saturation, compliance/backlash, sensor noise, voltage and thermal effects, contact, and whole robot dynamics are omitted; this does not establish hardware transfer.
