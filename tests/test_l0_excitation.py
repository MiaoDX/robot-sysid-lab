"""Scientific invariants of the fixed excitation comparison."""
import json
from pathlib import Path

import numpy as np
import pytest

from synthetic.l0_excitation import (
    CONFIG_PATH, fixed_residual, load_experiment,
    make_fit_observations, run_experiment, sensitivity,
)
from synthetic.l0_inertia_damping import Params, simulate


@pytest.fixture(scope='module')
def result():
    return run_experiment(grid_size=7)


def test_only_excitation_changes_between_records(result):
    a, b = [result['cases'][key] for key in ('slow_narrow', 'broad')]
    np.testing.assert_array_equal(a['trajectory']['t'], b['trajectory']['t'])
    assert len(a['trajectory']['t']) == 800
    assert a['coverage']['torque_peak'] == b['coverage']['torque_peak'] == .8
    assert all(c['trajectory']['q'][0] == c['trajectory']['qd'][0] == 0 for c in (a,b))
    assert not np.array_equal(a['trajectory']['u'], b['trajectory']['u'])
    assert result['common_contract']['scales']['outputs'] == {'q':1., 'qd':1.}


def test_noiseless_recovery_and_weaker_separation_are_distinct_claims(result):
    a,b=[result['cases'][key] for key in ('slow_narrow','broad')]
    assert 0 < a['sensitivity']['singular_values'][-1] < b['sensitivity']['singular_values'][-1]
    assert a['sensitivity']['condition_number'] > 5*b['sensitivity']['condition_number']
    assert a['coverage']['qdd_rms'] < b['coverage']['qdd_rms']
    for case in (a,b):
        assert case['fit']['success']
        for fit in case['multistart']:
            assert fit['success']
            assert fit['estimate']['inertia'] == pytest.approx(.065,rel=1e-8)
            assert fit['estimate']['damping'] == pytest.approx(.055,rel=1e-8)
        assert case['heldout']['q_rmse'] < 1e-9
        assert case['heldout']['qd_rmse'] < 1e-9


def test_hidden_truth_and_final_motion_cannot_change_fits_on_fixed_observations(tmp_path, monkeypatch):
    """Poison evaluation-only fields while keeping the actual training data fixed.

    This checks execution, not just the argument names: any new truth-based
    initialization, scaling or final-trajectory model selection changes a result.
    """
    config,settings=load_experiment()
    fixed=make_fit_observations(config,settings)
    monkeypatch.setattr('synthetic.l0_excitation.make_fit_observations',lambda *_:fixed)
    original=run_experiment(grid_size=5)
    poisoned=json.loads(CONFIG_PATH.read_text())
    poisoned['truth']={'inertia':.11,'damping':.09}
    poisoned['validation_excitation']={'frequencies_hz':[.73], 'amplitudes_nm':[.19], 'phases_rad':[.8]}
    path=tmp_path/'poisoned.json';path.write_text(json.dumps(poisoned))
    changed=run_experiment(path,grid_size=5)
    for key in original['cases']:
        for field in ['fit','fit_metrics','multistart','sensitivity','loss_landscape']:
            assert original['cases'][key][field] == changed['cases'][key][field]
        assert original['cases'][key]['heldout'] != changed['cases'][key]['heldout']


def test_repeated_execution_reproduces_numerical_artifact(result):
    assert result == run_experiment(grid_size=7)


def test_sensitivity_predicts_an_independent_small_parameter_perturbation():
    config,settings=load_experiment()
    obs=make_fit_observations(config,settings)['slow_narrow']
    point=config.nominal
    parameter_scales=[.095,.018]
    diagnostic=sensitivity(obs,point,[1.,1.],parameter_scales)
    direction=np.array([2e-4,-1e-4])
    base=np.array([point.inertia,point.damping])
    residual=fixed_residual(obs,[1.,1.])
    actual=residual(base+direction*parameter_scales)-residual(base)
    predicted=np.array(diagnostic['scaled_jacobian']) @ direction
    np.testing.assert_allclose(actual,predicted,rtol=.004,atol=2e-6)


def test_contours_measure_the_same_objective_as_fitting(result):
    config,settings=load_experiment()
    records=make_fit_observations(config,settings)
    for key,case in result['cases'].items():
        grid=case['loss_landscape'];i,j=1,3
        candidate=Params(grid['inertia_axis'][i],grid['damping_axis'][j])
        obs=records[key]
        q,qd=simulate(candidate,obs.t,obs.u,q0=obs.q[0],qd0=obs.qd[0])
        residual=np.r_[q-obs.q,qd-obs.qd]
        expected=.5*np.dot(residual,residual)
        assert grid['log10_cost'][i][j] == pytest.approx(np.log10(expected))
        assert grid['normalized_rmse'][i][j] == pytest.approx(np.sqrt(np.mean(residual**2)))


def test_frozen_artifact_matches_fresh_metrics(result):
    frozen=json.loads(Path('reports/l0_excitation/metrics.json').read_text())
    assert frozen['common_contract'] == result['common_contract']
    for key in result['cases']:
        for field in ['fit','coverage','heldout','sensitivity','multistart','trajectory']:
            assert frozen['cases'][key][field] == result['cases'][key][field]


@pytest.mark.parametrize('change', ['reverse_bands', 'truth', 'start_count'])
def test_custom_experiment_cannot_publish_the_frozen_lesson(tmp_path, change):
    from synthetic.l0_excitation import write_report

    raw = json.loads(CONFIG_PATH.read_text())
    if change == 'reverse_bands':
        inputs = raw['comparison_inputs']
        inputs['slow_narrow'], inputs['broad'] = inputs['broad'], inputs['slow_narrow']
    elif change == 'truth':
        raw['truth']['inertia'] = .07
    else:
        raw['multistart'] = raw['multistart'][:1]
    custom_path = tmp_path / 'custom.json'
    custom_path.write_text(json.dumps(raw))
    changed = run_experiment(custom_path, grid_size=5)
    if change == 'reverse_bands':
        assert changed['cases']['slow_narrow']['sensitivity']['condition_number'] < changed['cases']['broad']['sensitivity']['condition_number']
    output = tmp_path / 'published'
    with pytest.raises(ValueError, match='reviewed l0-excitation-v1'):
        write_report(changed, output)
    assert not output.exists()


@pytest.mark.parametrize('change', ['missing_field', 'failed_recovery', 'changed_condition'])
def test_report_rejects_results_that_cannot_support_its_claims(tmp_path, change):
    from synthetic.l0_excitation import write_report

    frozen = json.loads(Path('reports/l0_excitation/metrics.json').read_text())
    if change == 'missing_field':
        del frozen['common_contract']
    elif change == 'failed_recovery':
        frozen['cases']['slow_narrow']['fit']['estimate']['inertia'] = .12
    else:
        frozen['cases']['slow_narrow']['sensitivity']['condition_number'] = 1.1
    output = tmp_path / 'published'
    with pytest.raises(ValueError, match='reviewed l0-excitation-v1'):
        write_report(frozen, output)
    assert not output.exists()


def test_cli_does_not_advertise_or_accept_custom_report_configuration(tmp_path):
    from synthetic.l0_excitation import main

    with pytest.raises(SystemExit) as error:
        main(['--config', str(CONFIG_PATH), '--output-dir', str(tmp_path/'published')])
    assert error.value.code == 2
    assert not (tmp_path/'published').exists()
