# K5 · Understand what fitting actually solved

An optimizer can stop successfully and still leave us with a model that is poorly supported. This lesson explains what a parameter fit minimizes, what initial values and bounds can change, and how to decide whether a failure belongs to the optimizer, the data, or the model structure.

The goal is not to memorize optimizer names. It is to read a fitting record as evidence.

## “Converged” is not the same as “explained” {#failure}

Suppose two runs use the same L0 model and fitting data. One starts close to the hidden parameters and one starts far away. Both report success, but one reaches a lower loss and the other stops at a parameter bound. What should we conclude?

First inspect the objective, scaling, termination reason, and held-out prediction. A successful status only says that the algorithm met its stopping rule. It does not establish that the model structure is adequate, that the experiment was informative, or that the result is unique.

## Define the residual and objective {#objective}

For a predicted signal $y_\text{model}$ and an observed signal $y_\text{obs}$, use the declared residual convention

$$
r(\theta) = y_\text{model}(\theta) - y_\text{obs}.
$$

A weighted least-squares objective can be written as

$$
L(\theta) = \sum_i \left(\frac{r_i(\theta)}{s_i}\right)^2,
$$

where $s_i$ is a declared scale for a channel or noise level. Scaling changes how position, velocity, or torque errors contribute to the numerical objective. It does not add information to the experiment.

The fitting contract must declare the parameters $\theta$, bounds, initial value, data split, residual channels, scales, and stopping budget before final evaluation. If a validation curve is used to choose any of these, that curve is development data.

## How one local update uses sensitivities {#derivation}

Near a current parameter value $\theta$, approximate the residual with a first-order model:

$$
r(\theta + \Delta\theta) \approx r(\theta) + S\Delta\theta,
$$

where $S$ contains sensitivities of the residual to the parameters. The fitting step chooses an update that reduces the scaled residual according to the declared bounds and objective. In a well-conditioned problem, the columns of $S$ point in directions that the data can distinguish. In a long valley, many updates trade one parameter against another with little loss change.

This is why K4 and K5 are connected: the optimizer can only use information that the input made visible. A more elaborate optimizer cannot manufacture a missing sensitivity direction.

## Read the fitting record {#diagnostics}

Use the following order when a fit looks wrong:

1. **Objective:** Are residual signs, units, channel scales, and masks correct?
2. **Data:** Does the fitting input cover the effects needed to separate the parameters?
3. **Structure:** Is a delay, friction term, saturation, or coupling absent from the Student model?
4. **Optimization:** Given the first three checks, did the run stop early, hit a bound, or depend strongly on its initial value?

Compare multiple starts under the same budget, then change one upstream condition at a time. A lower fitting loss after changing the model does not tell us whether the new structure will predict new data. A lower loss after changing only the start tells us about optimization, not model adequacy.

## Think it through {#exercise}

Three records show these outcomes:

| Record | Fitting loss | Held-out loss | Other evidence |
|---|---:|---:|---|
| A | high | high | several starts agree; residual follows velocity |
| B | low | high | parameters move to a bound; held-out residual follows frequency |
| C | moderate | moderate | starts disagree; sensitivity columns are nearly parallel |

For each record, choose the first action: improve the model structure, redesign the experiment, or investigate optimization and scaling.

<details markdown="1">
<summary>Read a suggested answer</summary>

A calls for a model-structure hypothesis, because agreement across starts does not remove a systematic residual. B calls for checking the model and the fitting boundary before increasing the optimizer budget; the bound and frequency pattern are evidence, not a generic optimization failure. C calls for a more informative experiment or an additional constraint, because nearly parallel sensitivities indicate weak separation. In all cases, inspect units and objective construction before interpreting the parameter values.
</details>

## What fitting cannot prove {#limits}

Convergence is not uniqueness, and a small objective is not validation. Bounds can make an answer look stable while hiding an unmodeled effect. Multiple starts are a useful robustness check for a declared problem, not a proof for all inputs.

K6 will make the held-out evidence explicit: how to choose a new experiment, avoid leakage, and state the prediction envelope. Continue to [K6 · Challenge predictions with new experiments](../k6/index.md).
