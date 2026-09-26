# L1-O · Separate observation quality from plant behavior

A velocity trace calculated from noisy position can look like a new physical effect. This companion experiment asks a narrower question: when an observation is derived from another noisy observation, what evidence still supports an actuator estimate?

This page defines the experiment contract. The numerical runner, fixed report, and repeated-run results are still to be implemented; no measured value is claimed here.

## A rougher signal can change the answer {#failure}

Start with the delivered L1 delay experiment. Its fitter sees position and a velocity derived from position. Now add a declared position-noise source. Differencing can amplify high-frequency noise and make neighboring velocity samples correlated.

Predict two outcomes before seeing a run: using the extra channel may make the curve look more informative, but it may also change the objective's weighting without adding independent plant information.

## Declare the observation boundary {#boundary}

The Oracle still contains the exact simulator state. The Student receives only the public observation contract:

```text
command and noisy position → declared differencing rule → derived velocity → fitter
```

| Signal | Fitter | Evaluation | Oracle diagnostics |
|---|---|---|---|
| Command and noisy position | visible on fitting split | visible on held-out split only at evaluation | generated from declared seed |
| Derived velocity | visible if included in objective | scored on held-out split | exact velocity remains hidden |
| Exact simulator velocity | hidden | optional score only | explanation only |

The sampling clock and differencing endpoints must be fixed before fitting. A smoother-looking derived channel is not automatically a more independent measurement.

## Compare objectives under repeated noise {#comparison}

Keep the plant, command, controller, delay parameterization, and data durations fixed. Compare:

1. a position-only objective;
2. a position-plus-derived-velocity objective with declared channel scales.

Use independent, predeclared noise seeds for fitting, development, and final evaluation. Choose weights from fitting data or an explicitly labeled development split. Do not inspect final evaluation to select a filter, weight, or noise level.

The repeated-run comparison should separate estimator variability from plant prediction error. It should report the same held-out command family for both objectives and keep the exact state out of the fitter.

## Read observation evidence {#evidence}

The planned evidence package contains noisy position, derived velocity, channel residual scales, the distribution of fitted delays across seeds, and held-out predictions. Read it in this order:

- how much noise did differencing add;
- whether both channels are driven by the same position error;
- whether delay estimates move more across seeds;
- whether held-out plant predictions improve, worsen, or stay similar.

A smaller residual on a derived channel can coexist with a less stable parameter estimate. Report observation error and true-state error separately.

## Think it through {#exercise}

A position-plus-velocity objective has a lower training loss, but its delay estimates vary widely across repeated noise seeds. The position-only objective has a slightly higher training loss and more stable held-out predictions. Which result should guide the next experiment?

<details markdown="1">
<summary>Read a suggested answer</summary>

Prefer the objective with the more stable held-out prediction under the declared use, then investigate whether channel scaling or the differencing rule is responsible. Do not choose only by training loss or by visual smoothness. If the question is timing, design a new observation or excitation that gives timing information rather than adding a correlated derived channel.
</details>

The common wrong turn is to treat a smoother derived velocity as a new measurement. If you cannot choose an objective, compare repeated-seed stability and held-out plant prediction separately. Continue when the observation claim and the plant claim are written apart.

## What observation quality cannot prove {#limits}

This experiment isolates one position-noise model. It does not cover quantization, filter phase, timestamp offset, jitter, missing samples, or all sensor fusion choices. A noisy observation can widen uncertainty without changing the plant; a clean-looking trace cannot prove the underlying parameter is accurate.

The next conceptual step is K7, which separates physical and effective parameter meanings. The elective [L1-S saturation experiment](../l1-s/index.md) studies a different observability boundary.
