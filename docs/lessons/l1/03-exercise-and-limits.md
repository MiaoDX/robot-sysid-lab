# L1 · Exercises and the scope of the result

Open the local app and change **Initial delay**. Predict how the curves will change, then press **Run identification** to check the result.

Moving the initial delay toward the true value usually brings the orange response closer to the observations. Moving away usually increases error. Because this is a feedback system, larger delays can also change damping and stability; the response is more than a simple time shift of the entire curve.

After a settings change, the app shows a pending state. Existing orange and blue curves still come from the previous run. Submit before comparing new results. The replay timeline and signal selector let you inspect the completed run.

## Which conditions still need checking

This experiment fixes the mechanics and controller and estimates only command delay. Observations are ideal and the model matches the data-generating system. Other friction, saturation, compliance, measurement noise, contact, and payload changes are not included.

The result supports improved new-motion prediction using the estimated delay in this known system. Before applying it to a real actuator, check whether omitted effects change the result. The delay describes timing along the chosen command path; it is not the motor's electromagnetic time constant.

Later experiments will study friction, output limits, and observation errors before moving to coupled joints. Each starts by asking how the added effect changes observations and how to estimate it.

## Explain the result in one sentence

Describe what was estimated, which data was used, and how the result was checked. For example:

> For this loaded arm with known mechanical parameters, we estimated torque-command delay from position and derived velocity, improving predictions on a separate set of reversal motions.

Then name an assumption you would check before moving to hardware and explain which measurement would help.
