"""Deterministic L1 servo-driven loaded pendulum SysID lesson."""
from __future__ import annotations
import argparse,json
from dataclasses import asdict,dataclass
from pathlib import Path
from typing import Any
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares
DEFAULT_CONFIG_PATH=Path(__file__).with_name('l1_config.json')
@dataclass(frozen=True)
class Params: delay_s: float
@dataclass(frozen=True)
class Config:
 version:str; dt:float; duration_s:float; q0:float; qd0:float; mass:float; arm_length:float; gravity:float; kp:float; kd:float; truth:Params; initial:Params; optimizer_start:Params; lower:Params; upper:Params; fit_amp:float; fit_f0:float; fit_f1:float; validation_amp:float
@dataclass(frozen=True)
class Observations: t:np.ndarray; q_des:np.ndarray; q:np.ndarray; qd:np.ndarray
@dataclass(frozen=True)
class BenchmarkData: fit:Observations; validation:Observations; oracle_torque_fit:np.ndarray; oracle_torque_validation:np.ndarray; metadata:dict[str,Any]
@dataclass(frozen=True)
class Metrics: q_mae:float; qd_mae:float; q_rmse:float; qd_rmse:float
@dataclass(frozen=True)
class FitResult: params:Params; success:bool; message:str; cost:float
@dataclass(frozen=True)
class Run: config:Config; data:BenchmarkData; fit:FitResult; initial_fit:Metrics; identified_fit:Metrics; initial_validation:Metrics; identified_validation:Metrics
def load_config(path=None):
 r=json.loads((Path(path) if path else DEFAULT_CONFIG_PATH).read_text()); p=lambda x:Params(float(x['delay_s']))
 return Config(r['version'],r['dt'],r['duration_s'],r['initial_state']['q'],r['initial_state']['qd'],r['plant']['mass'],r['plant']['arm_length'],r['plant']['gravity'],r['controller']['kp'],r['controller']['kd'],p(r['truth']),p(r['initial_model']),p(r['optimizer_start']),p(r['bounds']['lower']),p(r['bounds']['upper']),r['fit_excitation']['amplitude_rad'],r['fit_excitation']['f0_hz'],r['fit_excitation']['f1_hz'],r['validation_excitation']['amplitude_rad'])
def make_time(c): return np.arange(int(round(c.duration_s/c.dt)),dtype=float)*c.dt
def excitation(t,amp,f0,f1,duration):
 e=t-t[0]; return amp*np.sin(2*np.pi*(f0*e+.5*(f1-f0)/duration*e*e))
def simulate(c,q_des,*,delay_s,q0=None,qd0=None,return_torque=False):
 q_des=np.asarray(q_des,float); n=q_des.size; q=np.empty(n); qd=np.empty(n); torque=np.empty(n); q[0]=c.q0 if q0 is None else q0; qd[0]=c.qd0 if qd0 is None else qd0; lag=max(0.0,delay_s/c.dt)
 for i in range(n-1):
  x=max(0.0,i-lag); j=int(x); w=x-j; delayed=(1-w)*q_des[j] + w*q_des[min(j+1,n-1)]; torque[i]=c.kp*(delayed-q[i])-c.kd*qd[i]; acc=(torque[i]-c.mass*c.gravity*c.arm_length*np.sin(q[i]))/(c.mass*c.arm_length*c.arm_length); qd[i+1]=qd[i]+acc*c.dt; q[i+1]=q[i]+qd[i]*c.dt+.5*acc*c.dt*c.dt
 torque[-1]=torque[-2] if n>1 else 0.; return (q,qd,torque) if return_torque else (q,qd)
def build_benchmark(c):
 t=make_time(c); fd=excitation(t,c.fit_amp,c.fit_f0,c.fit_f1,c.duration_s); vd=c.validation_amp*np.sign(np.sin(2*np.pi*.65*t+.4))*np.minimum(1,np.abs(np.sin(2*np.pi*.65*t+.4))*3); fq,fqd,ft=simulate(c,fd,delay_s=c.truth.delay_s,return_torque=True); vq,vqd,vt=simulate(c,vd,delay_s=c.truth.delay_s,return_torque=True); m={'config_version':c.version,'observations':['t','q_des','q','qd'],'public_observations':['t','q_des','q','qd'],'oracle_only':['true_torque','delayed_command_state'],'delay_semantics':'effective command delay after fixed PD law'}; return BenchmarkData(Observations(t,fd,fq,fqd),Observations(t,vd,vq,vqd),ft,vt,m)
def fit_student(o,c,initial_guess=None):
 def res(x):
  q,qd=simulate(c,o.q_des,delay_s=float(x[0]),q0=o.q[0],qd0=o.qd[0]); return np.r_[q-o.q,qd-o.qd]
 r=least_squares(res,[ (initial_guess or c.optimizer_start).delay_s],bounds=([c.lower.delay_s],[c.upper.delay_s]),max_nfev=100,ftol=1e-12,xtol=1e-12,gtol=1e-12); return FitResult(Params(float(r.x[0])),bool(r.success),str(r.message),float(r.cost))
def score(o,c,d):
 q,qd=simulate(c,o.q_des,delay_s=d,q0=o.q[0],qd0=o.qd[0]); a=q-o.q; b=qd-o.qd; return Metrics(float(np.mean(abs(a))),float(np.mean(abs(b))),float(np.sqrt(np.mean(a*a))),float(np.sqrt(np.mean(b*b))))
def run_l1(c=None):
 c=c or load_config(); d=build_benchmark(c); f=fit_student(d.fit,c); return Run(c,d,f,score(d.fit,c,c.initial.delay_s),score(d.fit,c,f.params.delay_s),score(d.validation,c,c.initial.delay_s),score(d.validation,c,f.params.delay_s))
def run_summary(r): return {'config_version':r.config.version,'metadata':r.data.metadata,'truth':asdict(r.config.truth),'initial':asdict(r.config.initial),'identified':asdict(r.fit.params),'fit':{'initial':asdict(r.initial_fit),'identified':asdict(r.identified_fit)},'validation':{'initial':asdict(r.initial_validation),'identified':asdict(r.identified_validation)},'effective_delay_note':'identified delay is boundary and sampling dependent'}
def plot_run(r,path):
 p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); d=r.data; iq,iqd=simulate(r.config,d.fit.q_des,delay_s=r.config.initial.delay_s); fq,fqd=simulate(r.config,d.fit.q_des,delay_s=r.fit.params.delay_s); iv,ivd=simulate(r.config,d.validation.q_des,delay_s=r.config.initial.delay_s); fv,fvd=simulate(r.config,d.validation.q_des,delay_s=r.fit.params.delay_s); fig,ax=plt.subplots(3,2,figsize=(12,10),constrained_layout=True)
 ax[2,1].plot([0,0],[0,0],marker='s',markersize=14,color='black',label='fixed base')
 angle=float(d.validation.q[len(d.validation.q)//2]); ax[2,1].plot([0,r.config.arm_length*np.sin(angle)],[0,-r.config.arm_length*np.cos(angle)],linewidth=6,color='tab:blue',label='loaded arm')
 ax[2,1].scatter([r.config.arm_length*np.sin(angle)],[-r.config.arm_length*np.cos(angle)],s=100,color='tab:orange',label='point payload')
 ax[2,1].arrow(0,0,0,-.3,length_includes_head=True,color='tab:red',label='gravity'); ax[2,1].set_aspect('equal'); ax[2,1].set_title('Machine schematic (synthetic)'); ax[2,1].legend(fontsize=7)
 for a,t,o,i,f,title in [(ax[0,0],d.fit.t,d.fit.q,iq,fq,'Fit position'),(ax[0,1],d.validation.t,d.validation.q,iv,fv,'Validation position'),(ax[1,0],d.fit.t,d.fit.qd,iqd,fqd,'Fit velocity'),(ax[1,1],d.validation.t,d.validation.qd,ivd,fvd,'Validation velocity')]: a.plot(t,o,label='Oracle'); a.plot(t,i,label='Initial model'); a.plot(t,f,'--',label='Identified'); a.set_title(title); a.legend(); a.grid(alpha=.2)
 ax[2,0].plot(d.fit.t,fq-d.fit.q); ax[2,0].set_title('Fit residual: position'); ax[2,1].scatter(d.fit.qd,fqd-d.fit.qd,s=3); ax[2,1].set_title('Residual vs velocity'); fig.savefig(p,dpi=140); plt.close(fig); return p
def write_report(r,out):
 out=Path(out); out.mkdir(parents=True,exist_ok=True); plot_run(r,out/'report.png'); (out/'metrics.json').write_text(json.dumps(run_summary(r),indent=2)); (out/'report.md').write_text(f'# L1 Servo Driven Loaded Pendulum\n\nSynthetic ideal observation: fixed base, rotary arm, point payload, gravity, and fixed PD servo. Boundary: `q_des -> PD -> effective command delay -> torque -> pendulum`. Oracle delay is hidden; fitted delay is effective and boundary dependent.\n\nInitial delay: **{r.config.initial.delay_s:.3f} s**; identified: **{r.fit.params.delay_s:.3f} s**; Oracle: **{r.config.truth.delay_s:.3f} s**. Validation q RMSE changes from {r.initial_validation.q_rmse:.5g} to {r.identified_validation.q_rmse:.5g}.\n\nEstimator inputs are only `t`, `q_des`, `q`, and `qd`; torque and delayed state are Oracle diagnostics. Omitted effects include friction, saturation, compliance/backlash, sensor noise, voltage/thermal behavior, contacts, and whole-robot dynamics. This is not a motor electromagnetic model and does not establish hardware transfer.\n'); return out/'report.md'
def main(argv=None):
 a=argparse.ArgumentParser(); a.add_argument('--output-dir',default='reports/l1_servo_loaded_pendulum'); write_report(run_l1(),a.parse_args(argv).output_dir); return 0
if __name__=='__main__': raise SystemExit(main())
