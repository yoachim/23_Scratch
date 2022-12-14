import numpy as np
import pandas as pd
import sqlite3
from rubin_sim.scheduler.model_observatory import ModelObservatory
from rubin_sim.scheduler.utils import empty_observation, run_info_table, SchemaConverter
import sys
from astropy.time import Time



def update_minion(outfile='minion_1016_update.db', 
                  in_db='minion_1016_sqlite.db',
                  apply_weather=True, use_dithered=False,
                  table='Summary',
                  mjd_name='expMJD', exptime_name='visitExpTime',
                  radians=True):
    """Let's update the minion_1016 runs to have the current sky, weather downtime, and throughputs.
    """

    conn = sqlite3.connect(in_db)
    query = 'select * from %s group by %s order by %s' % (table, mjd_name, mjd_name)
    df = pd.read_sql(query, conn)

    num_obs = df['fieldRA'].size

    mo = ModelObservatory(mjd_start=df[mjd_name].min())
    blank = empty_observation()

    observations = np.zeros(num_obs, dtype=blank.dtype)
    if use_dithered:
        observations['RA'] = df['ditheredRA']
        observations['dec'] = df['ditheredDec']
    else:
        observations['RA'] = df['fieldRA']
        observations['dec'] = df['fieldDec']
    observations['mjd'] = df[mjd_name]
    observations['filter'] = df['filter']
    observations['exptime'] = df[exptime_name]
    observations['nexp'] = 2
    observations['slewtime'] = df['slewTime']
    observations['alt'] = df['altitude']
    observations['az'] = df['azimuth']
    observations['rotSkyPos'] = df['rotSkyPos']
    observations['rotTelPos'] = df['rotTelPos']
    try:
        observations['visittime'] = df['visitTime']
    except:
        observations['visittime'] = df[exptime_name] + 4

    obs_good = np.ones(num_obs, dtype=bool)

    if not radians:
        for key in ['RA', 'dec', 'rotSkyPos',
                    'rotTelPos', 'alt', 'az']:
            observations[key] = np.radians(observations[key])

    if apply_weather:
        for i, obs in enumerate(observations):

            obs_good[i] = True 
            
            clouds = mo.cloud_data(Time(obs['mjd'], format='mjd'))
            if clouds > mo.cloud_limit:
                obs_good[i] = False

            if obs_good[i]:
                mo.mjd = obs['mjd']

                observations[i] = mo.observation_add_data(obs)

                progress = i/num_obs*100
                text = "\rprogress=%.3f%%, %i of %i" % (progress, i, num_obs)
                sys.stdout.write(text)
                sys.stdout.flush()
    else:
        observations['airmass'] = df['airmass']
        observations['FWHMeff'] = df['FWHMeff']
        observations['FWHM_geometric'] = df['FWHMgeom']
        observations['skybrightness'] = df['filtSkyBrightness']
        observations['night'] = df['night']
        observations['slewdist'] = df['slewDist']
        observations['fivesigmadepth'] = df['fiveSigmaDepth']
        observations['pa'] = df['phaseAngle']
        observations['clouds'] = df['transparency']
        observations['sunAlt'] = df['sunAlt']

    observations = observations[np.where(obs_good == True)[0]]
    if outfile is not None:
        info = run_info_table(mo)
        converter = SchemaConverter()
        converter.obs2opsim(observations, filename=outfile, info=info, delete_past=True)


if __name__ == '__main__':
    #update_minion()
    #update_minion(outfile='minion_1016_newschema.db', apply_weather=True, use_dithered=False)
    
    update_minion(in_db='baseline2018a.db',
                  outfile='baseline2018a_newschema.db', 
                  apply_weather=True, use_dithered=False,
                  table='SummaryAllProps', mjd_name='observationStartMJD',
                  exptime_name='visitExposureTime',
                  radians=False)
    #update_minion(outfile='opsim3_61_newschema.db', in_db='opsim3_61_sqlite.db',exptime_name='expTime')

