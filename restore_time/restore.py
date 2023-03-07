from rubin_sim.scheduler import sim_runner
from rubin_sim.scheduler.model_observatory import ModelObservatory
from rubin_sim.scheduler.example import example_scheduler
from rubin_sim.scheduler.utils import restore_scheduler
import time


if __name__ == '__main__':
    mjd_start = 60676.0
    scheduler = example_scheduler(mjd_start=mjd_start)

    filename = 'time_test.db'

    mo = ModelObservatory(mjd_start=mjd_start)
    mo, scheduler, observations = sim_runner(mo, scheduler, survey_length=100.0,
                                             verbose=True, filename=filename)
    sched2 = example_scheduler(mjd_start=mjd_start)
    mo = ModelObservatory(mjd_start=mjd_start)
    t1 = time.time()

    sched2 = restore_scheduler(3000000, sched2, mo, filename)
    t2 = time.time()

    dt = (t2-t1)/60.
    print('Time to restore=%f min' % dt)
