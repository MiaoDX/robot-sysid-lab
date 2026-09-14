# 3. From fit to held-out validation

Fitting minimizes an error on the observations given to the estimator. That
error alone is not enough: a flexible or badly structured model can match one
trajectory and fail elsewhere.

L0 therefore has two explicit splits:

| Split | Input | Purpose |
|---|---|---|
| Fit | chirp | estimate `J` and `b` |
| Validation | held-out multisine | test prediction on a different motion |

The report gives mean absolute error (MAE) for both position `q` and velocity
`qd`. Compare the two nominal rows with the two identified rows. The important
pattern is not that every number is zero; it is that the identified model
improves on the untouched validation motion as well as on the fit motion.

The residual panels show `identified - observed`. A residual close to zero and
without an obvious time pattern is consistent with this matched, idealized
example. It does not establish that the parameters are identifiable under all
inputs or that the same model will work on hardware.

## Questions to answer

1. Why would reporting only fit MAE make the experiment weaker?
2. What evidence in the validation columns supports the identified model?
3. If fit error is low but validation error is high, would you first blame the
   optimizer or the model structure? What extra experiment would distinguish
   those explanations?

**Suggested answers:** fit-only scoring cannot expose overfitting or a model
that only matches one excitation. Here the identified validation errors are
much smaller than the nominal errors. A high validation error needs diagnosis:
repeat fitting from another start to test optimization, then inspect residuals
and add a missing effect only when the evidence supports it.
