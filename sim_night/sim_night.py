import numpy as np
import copy


# How do we go about simulating a night?

# Scenario 1:  Sim night, send the list of observations out, and they all just get executed

# Scenario 2:  Sim night, we get a ways into list, then deviate (clouds roll in, telescope down for an hour, whatever)
# restore scheduler to point right before divergence. Add in observations that haven't been recorded. 
# Sim rest of night again.

# I think we can't assume we have good Q/A on visits during night. So when inturrupted, let's assume things before that
# went accourding to plan. If they didn't, we'll get a proper update the next night with a scheduler constructed with
# only observations we know are good.

class NightSimulator(object):
    """Simulate a night

    Parameters
    ----------
    scheduler : rubin_sim.scheduler.Scheduler object
        A scheduler object. Up to date with all completed observations
        played into it.

    model_observatory : 
    """
    def __init__(self, scheduler, model_observatory):
        
        self.scheduler = scheduler
        self.model_observatory = model_observatory

        self.empty_queue_schedulers = []
        self.empty_queue_times = []

        scheduler_end, observatory_end, observations_full_night = sim_runner()
        # Need to generate 

    def update_observatory(self, scheduler_update_object):

        self.model_observatory.update(scheduler_update_object)

    def sim_rest_of_night(self, ):
        """Simulate the rest of the night"""
        # Take scheduler with empty queue closest in time to before requested date


