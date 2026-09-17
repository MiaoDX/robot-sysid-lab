"""Small guided L1 surface; fitting is explicit via Run identification."""
from synthetic.l1_servo_loaded_pendulum import run_l1

def main():
 r=run_l1(); print('L1 Servo Driven Loaded Pendulum'); print('Run identification:', r.fit.params.delay_s)
if __name__=='__main__': main()
