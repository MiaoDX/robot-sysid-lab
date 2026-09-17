import json
from synthetic.l1_servo_loaded_pendulum import *
def test_delay_recovery_and_validation():
 r=run_l1(); assert r.fit.success; assert abs(r.fit.params.delay_s-r.config.truth.delay_s)<1e-3; assert r.identified_validation.q_rmse < .5*r.initial_validation.q_rmse
def test_public_namespace_excludes_oracle():
 d=build_benchmark(load_config()); assert d.metadata['public_observations']==['t','q_des','q','qd']; assert 'true_torque' in d.metadata['oracle_only']
def test_report(tmp_path):
 p=write_report(run_l1(),tmp_path); assert p.exists(); assert json.loads((tmp_path/'metrics.json').read_text())['identified']['delay_s']>0
