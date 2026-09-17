# 3. Fit, validation, and residual phase

The fit asks the Student to choose one delay value that reproduces the public
fit observations. The Initial model remains the transparent zero-delay
baseline. The Identified Student starts from the optimizer's configured start
and is constrained by the documented lower and upper bounds. Those optimizer
details are separate from the learner-visible Initial model.

| Split | Excitation | Used by fitting? | Question |
| --- | --- | --- | --- |
| Fit | chirp | yes | Can public observations identify the timing effect? |
| Validation | held-out reversal waveform | no | Does the fitted delay predict another motion? |

Compare position and velocity for Oracle, Initial, and Identified curves. A
small fit error is expected after fitting, but the stronger evidence is lower
held-out validation error for the Identified Student. The default report's
metrics record both models so the comparison is inspectable rather than a
single success score.

## How to read the residuals

The report defines residuals as `model - observed` for the selected quantity.
Repeating positive and negative lobes around reversals can be a timing clue:
the Initial response is ahead of or behind the delayed Oracle. For a small
time shift, position residual is approximately proportional to velocity, so
the residual-versus-velocity view can also reveal phase mismatch. It does not
identify friction by itself: delay and velocity-dependent effects can produce
correlated patterns, and controlled experiments are needed to distinguish
them. In this matched ideal benchmark, a near-zero Identified
residual supports recovery of the configured effective delay; it does not prove
that delay is the only effect on a real servo.

The machine playback is a replay of recorded states. Scrubbing it must not
re-simulate or re-fit. Oracle and Identified lines keep distinct labels and
styles even when their arrays coincide.

## Checkpoint questions

1. Why would fit error alone be weak evidence?
2. What does lower Identified validation error show about the held-out command?
3. If validation error stayed high, what repeat-from-another-start test would
   separate optimizer trouble from a missing model effect?

Suggested answers: fit-only scoring cannot reveal poor generalization; lower
held-out error shows prediction improved on a motion withheld from fitting; and
repeating from an independent optimizer start checks convergence before adding
another physical effect.
