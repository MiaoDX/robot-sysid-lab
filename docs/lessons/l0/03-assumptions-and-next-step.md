# 4. Assumptions, limits, and the next lesson

L0 is a correctness and intuition lesson, not a complete servo model. It uses
known applied torque and ideal observations, and its teacher and Student share
the same equation. That makes parameter recovery easy to interpret.

The result should not be transferred directly to a real robot. Real systems
may add:

- command-to-torque scale and controller dynamics;
- delay and timing misalignment;
- saturation and voltage/current limits;
- Coulomb or Stribeck friction;
- backlash, compliance, and resonance;
- contact and load changes;
- sensor noise, filtering, quantization, and missing samples.

These are not footnotes. Each omitted effect can leave a structured residual
or make a fitted value effective rather than physically literal. For example,
an inertia-like simulator parameter that improves trajectory prediction is not
automatically a measurement of rotor inertia.

## Next question

The next lesson should add exactly one model-mismatch effect: delay. The
question becomes: can a Student without delay still fit one motion, and what
does held-out phase error reveal? It should reuse this lesson's flow:

```text
declare boundary -> generate fit/validation data -> fit -> validate -> diagnose
```

That repeated shape is why the repository keeps a [Lesson / Experiment
Pipeline](../../lesson_pipeline.md). We will extract shared code only after
the second lesson shows which data and report structures are genuinely common.

## Final checkpoint

State the L0 conclusion in one sentence:

> Under a matched $J\ddot{q} + b\dot{q} = u$ model with known torque and ideal
> observations, a chirp fit can recover `J` and `b` and predict a held-out
> multisine; the conclusion is bounded by those assumptions.
