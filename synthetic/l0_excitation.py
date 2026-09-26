"""Frozen L0-E excitation comparison; both inputs recover the noiseless plant.

Reuse L0's analytical simulator and bounded least-squares settings, with public
fixed output scales so changing the input does not silently change the objective.
The estimator and fit diagnostics accept observations and public settings only.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import resource
import time
from typing import Mapping

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy

from synthetic.l0_inertia_damping import (
    Observations, Params, _run_least_squares, _validate_bounds,
    chirp_command, load_config, make_time, multisine_command, score, simulate,
)

CONFIG_PATH = Path(__file__).with_name('l0_excitation_config.json')
CASE_LABELS = {'slow_narrow': 'Slow / narrow', 'broad': 'Broad / reversing'}
COLORS = {'slow_narrow': '#bb5b2c', 'broad': '#1677a3'}
CASE_ORDER = ('slow_narrow', 'broad')
# The prose/plot limits below belong to this reviewed teaching experiment only.
FROZEN_CONFIG_SHA256 = '652b594f371356f96d47e150ff5aa98cede63aa944cdd294d57de07c21986a6c'


def config_digest(settings):
    return hashlib.sha256(json.dumps(settings, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load_experiment(path=CONFIG_PATH):
    raw = json.loads(Path(path).read_text(encoding='utf-8'))
    return load_config(path), raw


def make_fit_observations(config, settings) -> dict[str, Observations]:
    """Oracle generator: only this boundary receives hidden parameters."""
    t = make_time(config)
    result = {}
    for key, spec in settings['comparison_inputs'].items():
        unit = chirp_command(t, **spec, amplitude_nm=1., duration_s=config.duration_s)
        u = settings['peak_torque_nm'] * unit / np.max(np.abs(unit))
        q, qd = simulate(config.truth, t, u, q0=config.q0, qd0=config.qd0)
        result[key] = Observations(t, u, q, qd)
    return result


def fixed_residual(observations: Observations, output_scales):
    scales = np.asarray(output_scales, dtype=float)
    if scales.shape != (2,) or not np.all(np.isfinite(scales)) or np.any(scales <= 0):
        raise ValueError('two finite positive output scales are required')

    def residual(vector):
        q, qd = simulate(Params(*vector), observations.t, observations.u,
                         q0=float(observations.q[0]), qd0=float(observations.qd[0]))
        return np.concatenate(((q-observations.q)/scales[0],
                               (qd-observations.qd)/scales[1]))
    return residual


def fit_observations(observations, *, initial_guess, lower_bounds, upper_bounds,
                     output_scales):
    """No Oracle or held-out argument; same L0 optimizer, declared shared scales."""
    _validate_bounds(initial_guess, lower_bounds, upper_bounds)
    result = _run_least_squares(fixed_residual(observations, output_scales),
                                [initial_guess.inertia, initial_guess.damping],
                                lower_bounds, upper_bounds)
    return {'estimate': asdict(Params(*map(float, result.x))),
            'success': bool(result.success), 'nfev': int(result.nfev),
            'cost': float(result.cost)}


def sensitivity(observations, estimate, output_scales, parameter_scales):
    """Dimensionless derivatives of scaled outputs w.r.t. scaled parameters.

    Divide by sqrt(2N) so singular values do not grow solely with sample count.
    Column plots retain samplewise derivatives before that normalization.
    """
    vector = np.array([estimate.inertia, estimate.damping])
    residual = fixed_residual(observations, output_scales)
    columns = []
    for index, scale in enumerate(parameter_scales):
        step = vector[index] * 1e-5
        plus, minus = vector.copy(), vector.copy()
        plus[index] += step
        minus[index] -= step
        columns.append((residual(plus)-residual(minus)) * scale/(2*step))
    jac = np.column_stack(columns)
    singular = np.linalg.svd(jac / np.sqrt(jac.shape[0]), compute_uv=False)
    return {'singular_values': singular.tolist(),
            'condition_number': float(singular[0]/singular[-1]),
            'column_cosine': float(jac[:,0] @ jac[:,1] /
                                   (np.linalg.norm(jac[:,0])*np.linalg.norm(jac[:,1]))),
            'scaled_jacobian': jac.tolist()}


def fit_comparison(observations: Mapping[str, Observations], *, initial_guess,
                   lower_bounds, upper_bounds, output_scales, parameter_scales,
                   starts, grid_size=41, half_width=.35):
    """Fit, multi-start and diagnose each training record before final scoring."""
    cases = {}
    for key, obs in observations.items():
        kwargs = dict(lower_bounds=lower_bounds, upper_bounds=upper_bounds,
                      output_scales=output_scales)
        fitted = fit_observations(obs, initial_guess=initial_guess, **kwargs)
        estimate = Params(**fitted['estimate'])
        records = []
        for start in starts:
            record = fit_observations(obs, initial_guess=Params(*start), **kwargs)
            records.append({'start': asdict(Params(*start)), **record})
        residual = fixed_residual(obs, output_scales)
        center = np.array([estimate.inertia, estimate.damping])
        scaled_axis = np.linspace(-half_width, half_width, grid_size)
        axes = [center[i] + scaled_axis*parameter_scales[i] for i in range(2)]
        # The frozen window is wholly inside bounds; reject invalid custom windows.
        for axis, lower, upper in zip(axes, asdict(lower_bounds).values(), asdict(upper_bounds).values()):
            if axis.min() <= lower or axis.max() >= upper:
                raise ValueError('loss diagnostic window must stay within public bounds')
        cost = np.array([[.5*np.sum(residual([j,b])**2) for b in axes[1]] for j in axes[0]])
        cases[key] = {'fit': fitted,
                      'sensitivity': sensitivity(obs, estimate, output_scales, parameter_scales),
                      'multistart': records,
                      'loss_landscape': {'inertia_axis': axes[0].tolist(),
                                         'damping_axis': axes[1].tolist(),
                                         'scaled_offset_axis': scaled_axis.tolist(),
                                         'log10_cost': np.log10(np.maximum(cost,1e-30)).tolist(),
                                         'normalized_rmse': np.sqrt(cost/len(obs.t)).tolist()},
                      'fit_metrics': asdict(score(estimate, obs)),
                      'trajectory': {'t': obs.t.tolist(), 'u': obs.u.tolist(),
                                     'q': obs.q.tolist(), 'qd': obs.qd.tolist()}}
    return cases


def run_experiment(config_path=CONFIG_PATH, *, grid_size=None):
    config, settings = load_experiment(config_path)
    observations = make_fit_observations(config, settings)
    output_scales = [settings['output_scales'][k] for k in ('q', 'qd')]
    parameter_scales = [settings['parameter_scales'][k] for k in ('inertia', 'damping')]
    # Nothing from final evaluation or hidden truth crosses this estimator call.
    cases = fit_comparison(observations, initial_guess=config.nominal,
                           lower_bounds=config.lower_bounds, upper_bounds=config.upper_bounds,
                           output_scales=output_scales, parameter_scales=parameter_scales,
                           starts=settings['multistart'],
                           grid_size=grid_size or settings['loss_grid_size'],
                           half_width=settings['loss_half_width_scaled'])
    # Generate final observations only after every estimate/diagnostic is frozen.
    t = make_time(config)
    heldout_u = multisine_command(t, frequencies_hz=config.validation_frequencies_hz,
                                  amplitudes_nm=config.validation_amplitudes_nm,
                                  phases_rad=config.validation_phases_rad)
    heldout_q, heldout_qd = simulate(config.truth, t, heldout_u, q0=config.q0, qd0=config.qd0)
    heldout = Observations(t, heldout_u, heldout_q, heldout_qd)
    for key, result in cases.items():
        obs = observations[key]
        acceleration = (obs.u - config.truth.damping*obs.qd)/config.truth.inertia
        estimate = Params(**result['fit']['estimate'])
        q, qd = simulate(estimate, t, heldout_u, q0=config.q0, qd0=config.qd0)
        result.update(input={'kind':'sample-peak-normalized chirp',
                             **settings['comparison_inputs'][key],
                             'amplitude_nm': settings['peak_torque_nm']},
                      coverage={'q_min':float(obs.q.min()), 'q_max':float(obs.q.max()),
                                'qd_min':float(obs.qd.min()), 'qd_max':float(obs.qd.max()),
                                'qdd_rms':float(np.sqrt(np.mean(acceleration**2))),
                                'qdd_peak':float(np.abs(acceleration).max()),
                                'torque_peak':float(np.abs(obs.u).max()),
                                'torque_rms':float(np.sqrt(np.mean(obs.u**2))),
                                'frequency_band_hz':list(settings['comparison_inputs'][key].values())},
                      heldout=asdict(score(estimate, heldout)),
                      heldout_prediction={'q':q.tolist(),'qd':qd.tolist()},
                      relative_parameter_error={'inertia':abs(estimate.inertia/config.truth.inertia-1),
                                                'damping':abs(estimate.damping/config.truth.damping-1)})
        result['trajectory']['qdd'] = acceleration.tolist()
    return {'schema_version':1, 'config_version':config.version,
            'config_sha256':config_digest(settings),
            'common_contract':{'dt_s':config.dt,'duration_s':config.duration_s,
                               'samples':len(t),'initial_state':{'q':config.q0,'qd':config.qd0},
                               'truth':asdict(config.truth),'fit_start':asdict(config.nominal),
                               'bounds':{'lower':asdict(config.lower_bounds),'upper':asdict(config.upper_bounds)},
                               'scales':{'outputs':settings['output_scales'],'parameters':settings['parameter_scales']},
                               'heldout_input':{'frequencies_hz':list(config.validation_frequencies_hz),
                                                'amplitudes_nm':list(config.validation_amplitudes_nm),
                                                'phases_rad':list(config.validation_phases_rad)},
                               'noise':'none','model':'J*qdd + b*qd = u'},
            'cases':cases,
            'heldout':{'t':t.tolist(),'u':heldout_u.tolist(),'q':heldout_q.tolist(),'qd':heldout_qd.tolist(),
                       'initial_model_metrics':asdict(score(config.nominal,heldout))},
            'comparison':{'conclusion':'Both noiseless fits recover; broad input improves local parameter separation. Weak sensitivity is not failed recovery.',
                          'development':'Frequency presets and public scales frozen using fit-only sensitivity and coverage; held-out scores were not used for selection.'},
            'artifacts':{'figures':['slow_narrow_vs_broad.png','excitation_loss_contours.png',
                                    'multistart_estimates.png','heldout_predictions.png'],
                         'data_json':'metrics.json'}}


def plot_report(result, directory):
    fig, axes = plt.subplots(3,2,figsize=(12,10),constrained_layout=True)
    for column,(key,case) in enumerate((key, result['cases'][key]) for key in CASE_ORDER):
        data=case['trajectory']; color=COLORS[key]
        axes[0,column].plot(data['t'],data['u'],color=color)
        axes[0,column].set(title=CASE_LABELS[key],xlabel='time (s)',ylabel='applied torque (N m)',ylim=(-.85,.85))
        axes[1,column].plot(data['qd'],data['qdd'],color=color)
        axes[1,column].set(xlabel='velocity (rad/s)',ylabel='acceleration (rad/s²)',xlim=(-2,13),ylim=(-16,16))
        jac=np.array(case['sensitivity']['scaled_jacobian']); n=len(data['t'])
        axes[2,column].plot(data['t'],jac[:n,0],label='J: position derivative',color='#7051a6')
        axes[2,column].plot(data['t'],jac[:n,1],label='b: position derivative',color='#137c67')
        axes[2,column].plot(data['t'],jac[n:,0],'--',label='J: velocity derivative',color='#7051a6')
        axes[2,column].plot(data['t'],jac[n:,1],'--',label='b: velocity derivative',color='#137c67')
        axes[2,column].set(xlabel='time (s)',ylabel='dimensionless derivative',ylim=(-20,8),
                           title=f"σ min = {case['sensitivity']['singular_values'][-1]:.3f}; κ = {case['sensitivity']['condition_number']:.2f}")
        axes[2,column].legend(fontsize=8)
    for ax in axes.flat: ax.grid(alpha=.2)
    fig.suptitle('L0-E: same 0.8 N m peak, 8 s, 800 samples; only fitting input changes')
    fig.savefig(directory/'slow_narrow_vs_broad.png',dpi=150);plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(12,5),constrained_layout=True)
    levels=[.1,.2,.4,.8,1.6,3.2]
    for ax,(key,case) in zip(axes,((key,result['cases'][key]) for key in CASE_ORDER)):
        grid=case['loss_landscape'];axis=grid['scaled_offset_axis']
        contour=ax.contour(axis,axis,np.array(grid['normalized_rmse']).T,levels=levels,cmap='viridis')
        ax.clabel(contour,inline=True,fontsize=8)
        ax.plot(0,0,'+',color='red',label='identified parameters')
        ax.set(title=CASE_LABELS[key],xlabel='(J − J fit) / 0.095',ylabel='(b − b fit) / 0.018',aspect='equal')
        ax.grid(alpha=.2);ax.legend(fontsize=8)
    fig.suptitle('Simulation loss contours: same dimensionless axes and normalized-RMSE levels')
    fig.savefig(directory/'excitation_loss_contours.png',dpi=160);plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
    truth=result['common_contract']['truth']
    for ax,(key,case) in zip(axes,((key,result['cases'][key]) for key in CASE_ORDER)):
        for record in case['multistart']:
            start,estimate=record['start'],record['estimate']
            ax.plot([start['inertia'],estimate['inertia']],[start['damping'],estimate['damping']],color=COLORS[key],alpha=.45)
            ax.plot(start['inertia'],start['damping'],'o',mfc='white',color=COLORS[key])
        ax.plot(truth['inertia'],truth['damping'],'*',color='black',ms=13,label='Oracle (evaluation only)')
        ax.set(title=CASE_LABELS[key]+' — all 9 starts recover',xlabel='J (kg m²)',ylabel='b (N m s/rad)',xlim=(0,.15),ylim=(0,.2))
        ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.suptitle('Start-to-result segments are not optimizer iteration paths')
    fig.savefig(directory/'multistart_estimates.png',dpi=150);plt.close(fig)

    fig,axes=plt.subplots(2,1,figsize=(10,6),constrained_layout=True)
    held=result['heldout']
    axes[0].plot(held['t'],held['q'],color='black',lw=2,label='Oracle held-out position')
    for key in CASE_ORDER:
        case = result['cases'][key]
        axes[0].plot(held['t'],case['heldout_prediction']['q'],'--',color=COLORS[key],label=CASE_LABELS[key]+' fitted model')
        axes[1].plot(held['t'],np.array(case['heldout_prediction']['q'])-held['q'],color=COLORS[key],label=CASE_LABELS[key])
    axes[0].set(ylabel='position (rad)',title='Same reserved multisine: both noiseless models predict it')
    axes[1].set(xlabel='time (s)',ylabel='position residual (rad)',title='Floating-point-scale residuals do not rank the inputs')
    for ax in axes: ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.savefig(directory/'heldout_predictions.png',dpi=150);plt.close(fig)



def require_frozen_report(result):
    """Reject other experiments before publishing the fixed lesson narrative.

    Internal custom runs support boundary tests, but their results must never be
    presented with this experiment's physical values, budgets or conclusions.
    """
    message = ('This report supports only the reviewed l0-excitation-v1 experiment '
               'and verified recovery/separation results; update the lesson contract '
               'and narrative before publishing another experiment.')
    config, settings = load_experiment()
    try:
        if config_digest(settings) != FROZEN_CONFIG_SHA256:
            raise ValueError(message)
        if result['config_sha256'] != FROZEN_CONFIG_SHA256 or result['config_version'] != config.version:
            raise ValueError(message)
        expected_contract = {
            'dt_s':config.dt, 'duration_s':config.duration_s, 'samples':len(make_time(config)),
            'initial_state':{'q':config.q0,'qd':config.qd0}, 'truth':asdict(config.truth),
            'fit_start':asdict(config.nominal),
            'bounds':{'lower':asdict(config.lower_bounds),'upper':asdict(config.upper_bounds)},
            'scales':{'outputs':settings['output_scales'],'parameters':settings['parameter_scales']},
            'heldout_input':{'frequencies_hz':list(config.validation_frequencies_hz),
                             'amplitudes_nm':list(config.validation_amplitudes_nm),
                             'phases_rad':list(config.validation_phases_rad)},
            'noise':'none', 'model':'J*qdd + b*qd = u',
        }
        if result['common_contract'] != expected_contract or set(result['cases']) != set(CASE_ORDER):
            raise ValueError(message)
        for key in CASE_ORDER:
            case = result['cases'][key]
            expected_input = {'kind':'sample-peak-normalized chirp',
                              **settings['comparison_inputs'][key],
                              'amplitude_nm':settings['peak_torque_nm']}
            if case['input'] != expected_input:
                raise ValueError(message)
            if [record['start'] for record in case['multistart']] != [asdict(Params(*x)) for x in settings['multistart']]:
                raise ValueError(message)
            for fitted in [case['fit'], *case['multistart']]:
                if not fitted['success'] or any(
                    not np.isfinite(fitted['estimate'][name]) or
                    abs(fitted['estimate'][name] / value - 1) >= 1e-8
                    for name, value in asdict(config.truth).items()
                ):
                    raise ValueError(message)
            for metric in ('q_rmse', 'qd_rmse'):
                if not 0 <= case['heldout'][metric] < 1e-9:
                    raise ValueError(message)
            grid = case['loss_landscape']
            size = settings['loss_grid_size']
            if (np.asarray(grid['normalized_rmse']).shape != (size,size) or
                np.asarray(grid['log10_cost']).shape != (size,size) or
                any(len(case['trajectory'][field]) != expected_contract['samples']
                    for field in ('t','u','q','qd','qdd'))):
                raise ValueError(message)
            if not (np.all(np.isfinite(grid['normalized_rmse'])) and
                    np.all(np.isfinite(grid['log10_cost']))):
                raise ValueError(message)
        slow, broad = [result['cases'][key] for key in CASE_ORDER]
        if not (0 < slow['sensitivity']['singular_values'][-1] < broad['sensitivity']['singular_values'][-1]
                and slow['sensitivity']['condition_number'] > broad['sensitivity']['condition_number'] >= 1
                and slow['coverage']['qdd_rms'] < broad['coverage']['qdd_rms']):
            raise ValueError(message)
    except (KeyError, TypeError, IndexError) as error:
        raise ValueError(message) from error


def write_report(result, directory):
    require_frozen_report(result)
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    (directory/'metrics.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    plot_report(result,directory)
    a,b=result['cases']['slow_narrow'],result['cases']['broad']
    rows=[]
    for key in CASE_ORDER:
        case = result['cases'][key]
        s=case['sensitivity'];c=case['coverage'];p=case['fit']['estimate'];h=case['heldout']
        rows.append(f"| {CASE_LABELS[key]} | {c['qd_min']:.3f} … {c['qd_max']:.3f} | {c['qdd_rms']:.3f} | {s['singular_values'][-1]:.3f} | {s['condition_number']:.2f} | {p['inertia']:.8f}, {p['damping']:.8f} | {h['q_rmse']:.3g} |")
    table='\n'.join(rows)
    common=f"""| Input / 输入 | velocity / 速度 (rad/s) | accel RMS / 加速度 (rad/s²) | σ min | κ | J, b | held-out q RMSE / 留出 (rad) |
|---|---:|---:|---:|---:|---:|---:|
{table}
"""
    texts={
        'report.md':f"""# L0-E · Excitation and parameter separation

The frozen noise-free comparison **recovers both parameters from both inputs**. The broad input improves local separation (condition {a['sensitivity']['condition_number']:.2f} → {b['sensitivity']['condition_number']:.2f}); the weak direction does not make the slow fit fail. Oracle J = 0.065 kg m², b = 0.055 N m s/rad are evaluation-only.

## Contract and reproducibility

Install dependencies with `python -m pip install -r requirements.txt`, then run `python -m synthetic.l0_excitation --output-dir reports/l0_excitation` from the repository root. This command publishes only the reviewed frozen experiment; custom configurations require a revised lesson/report. The frozen config is [l0_excitation_config.json](../../synthetic/l0_excitation_config.json); [metrics.json](metrics.json) records full trajectories, loss grids, sensitivity columns and every start/result. Both records have 800 samples at 0.01 s over an 8 s budget, q(0)=qd(0)=0, and exactly 0.8 N m sampled peak torque. The 0.005–0.015 Hz chirp is a slowly increasing partial cycle; the 0.15–3 Hz chirp includes reversals. Each sampled waveform is divided by its own peak, then multiplied by 0.8. Equal peak and duration do not mean equal RMS torque, frequency content or motion range. Large angles here are acceptable only because this ideal rotor has no joint limits or gravity.

We reuse L0's exact zero-order-hold simulator and bounded TRF least-squares settings. The shared bounds are J ∈ [0.01, 0.15], b ∈ [0.000001, 0.2], and the shared initial model is (0.095, 0.018). Unlike L0's per-record standard deviations, L0-E fixes public output scales at 1 rad and 1 rad/s for **both** fits. The cost is one half the sum of squared scaled q/qd residuals. No noise or model mismatch is added.

The frequency presets and scales were frozen using training-only coverage and sensitivity. No final score selected them. Every fit and diagnostic completes before held-out observations are generated. The reserved L0 multisine uses frequencies [0.35, 1.3, 2.7] Hz, amplitudes [0.45, 0.22, 0.1] N m and phases [0, 0.3, 1] rad. There is no adaptive development or final-result tuning in the runner. Any future tuning on this final record requires a fresh final evaluation.

## Coverage and local sensitivity

![Input, coverage and scaled sensitivity columns](slow_narrow_vs_broad.png)

Read each column top to bottom: torque, velocity/acceleration coverage, then output sensitivities. Purple means J; green means b; solid lines are position and dashed lines velocity. Acceleration is an Oracle evaluation diagnostic, never a fitting input. Both sensitivity columns are evaluated at the fitted parameters using central differences. Parameter scales are public initial-model values (0.095, 0.018); output scales are (1, 1). Singular values come from the scaled output Jacobian divided by sqrt(2N), keeping sample count out of the comparison. The plot shows the samplewise columns before that final division. This is a local conditioning diagnostic, not a statistical uncertainty estimate.

{common}

## The objective and multiple starts

![Actual loss contours with shared levels and axes](excitation_loss_contours.png)

The plotted value is sqrt(mean(scaled residual²)); the machine-readable grid also contains log10 of the optimizer cost. Both axes are offsets from each fitted point divided by the same public parameter scales, so aspect ratio has meaning. Compare equal contour levels. A long valley is weaker local separation; it is not an exactly flat, unidentifiable direction.

![Nine starts converge for both inputs](multistart_estimates.png)

Hollow circles are nine declared starts, black stars are Oracle parameters shown for evaluation. Straight segments connect starts to final estimates; they are **not** optimizer paths. All 18 starts converge and recover J and b within 1e-8 relative error. This supports this finite test, not universal convergence.

## Final held-out prediction

![Shared held-out predictions and residuals](heldout_predictions.png)

Both held-out position RMSEs are below 1e-9 rad. Their tiny difference is numerical, and cannot justify declaring one input a better predictor. Noisy or mismatched systems may behave differently; those are separate experiments. Inspect the sensitivity and coverage when deciding the next data collection, rather than claiming a failed slow fit that did not occur.

## Resources

CPU only; no download or GPU. [runtime.json](runtime.json) records measured wall time and peak process RSS for a full report run, plus Python/NumPy/SciPy versions and the machine architecture. Budget 60 seconds and 512 MiB for this small local experiment; the measured run is machine-specific. Independent learner acceptance and hardware transfer remain untested.
""",
        'report.zh-CN.md':f"""# L0-E · 激励与参数分离

这份固定无噪声对比中，**两种输入都恢复了两个参数**。宽频输入改善局部分离程度（条件数 {a['sensitivity']['condition_number']:.2f} → {b['sensitivity']['condition_number']:.2f}），但弱方向没有让慢输入拟合失败。Oracle J = 0.065 kg m²、b = 0.055 N m s/rad 只用于评估。

## 契约与复现

首次执行 `python -m pip install -r requirements.txt` 安装依赖，然后在仓库根目录运行 `python -m synthetic.l0_excitation --output-dir reports/l0_excitation`。这个命令仅发布已审定的固定实验；自定义配置需要另行修订课程与报告。固定配置为 [l0_excitation_config.json](../../synthetic/l0_excitation_config.json)，[metrics.json](metrics.json) 保存完整轨迹、损失网格、敏感度列和每组起点/结果。两份记录都是 0.01 s 采样、8 s 预算、800 个样本，q(0)=qd(0)=0，采样力矩峰值恰好为 0.8 N m。0.005–0.015 Hz 输入是缓慢上升的部分正弦周期；0.15–3 Hz 扫频包含换向。每个采样波形除以自己的峰值，再乘以 0.8。相同峰值与时长不代表相同力矩 RMS、频率内容或运动范围。这里的大转角只适用于无关节限位、无重力的理想转子。

复用 L0 的精确零阶保持仿真器和有界 TRF 最小二乘设置。公共边界为 J ∈ [0.01, 0.15]、b ∈ [0.000001, 0.2]，公共初始模型为 (0.095, 0.018)。L0 按每份数据的标准差归一化；L0-E 为保证公平比较，把**两次**输出尺度都固定为公开的 1 rad 和 1 rad/s。代价为尺度化位置/速度残差平方和的一半。没有加入噪声或模型失配。

频率预设和尺度仅根据拟合数据的覆盖与敏感度冻结，未用最终分数选择。全部拟合和诊断完成后才生成留出观测。沿用 L0 已声明多正弦：频率 [0.35, 1.3, 2.7] Hz、幅值 [0.45, 0.22, 0.1] N m、相位 [0, 0.3, 1] rad。运行器不进行自适应开发或最终结果调参。如果未来用本结果选择设置，必须另留新的最终评估。

## 覆盖与局部敏感度

![输入、状态覆盖与尺度化敏感度列](slow_narrow_vs_broad.png)

每列从上到下读：力矩、速度/加速度覆盖、输出敏感度。紫色是 J，绿色是 b；实线对应位置，虚线对应速度。加速度是 Oracle 评估诊断，不进入拟合。两列敏感度都在拟合参数处用中心差分计算。参数尺度取公开初始模型 (0.095, 0.018)，输出尺度为 (1, 1)。对尺度化输出 Jacobian 除以 sqrt(2N) 后求奇异值，避免仅由样本数放大诊断值；图中显示除以 sqrt(2N) 前的逐样本列。这是局部条件性诊断，不是统计不确定度。

{common}

## 目标函数与多初始点

![共同尺度与等高线级别的实际损失图](excitation_loss_contours.png)

图中数值为 sqrt(mean(尺度化残差²))；机器可读网格还包含优化器代价的 log10。两轴是相对各自拟合点的偏移，除以相同公开参数尺度，因此长宽比可以比较。比较相同等高线级别。细长谷说明局部分离较弱，不等于存在完全平坦、不可辨识的方向。

![两种输入的九个起点都收敛](multistart_estimates.png)

空心圆是预先声明的九个起点，黑星是仅用于评估的 Oracle 参数。直线连接起点和最终估计，**不是**优化迭代路径。18 次拟合全部成功，J 与 b 的相对误差均低于 1e-8。这只支持已测起点，不保证普遍收敛。

## 最终留出预测

![共同留出预测与残差](heldout_predictions.png)

两种输入的留出位置 RMSE 都小于 1e-9 rad。微小差别属于数值精度，不能据此宣布某种输入预测更好。噪声或模型失配可能改变结果，但属于其他实验。决定下一次采集时应看敏感度与覆盖，不能把未发生的慢输入失败写成结论。

## 资源

仅 CPU，无需下载数据或 GPU。[runtime.json](runtime.json) 记录完整报告运行的实测耗时、进程峰值 RSS、Python/NumPy/SciPy 版本和机器架构。为这个本地小实验预留 60 秒、512 MiB；实测值随机器变化。独立学习者验收与硬件迁移仍未验证。
"""}
    for name,text in texts.items(): (directory/name).write_text(text,encoding='utf-8')
    return directory/'report.md'


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=Path('reports/l0_excitation'))
    args=parser.parse_args(argv);started=time.perf_counter()
    result=run_experiment();report=write_report(result,args.output_dir)
    runtime={'wall_seconds':time.perf_counter()-started,
             'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
             'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
             'architecture':platform.machine(),'gpu_required':False,
             'scope':'full fit, diagnostics, figures and bilingual report; Linux process peak RSS',
             'budget_seconds':60,'budget_mib':512}
    (args.output_dir/'runtime.json').write_text(json.dumps(runtime,indent=2,sort_keys=True)+'\n')
    print(report);print(json.dumps(runtime))
    return 0 if all(c['fit']['success'] and all(m['success'] for m in c['multistart']) for c in result['cases'].values()) else 1


if __name__=='__main__':
    raise SystemExit(main())
