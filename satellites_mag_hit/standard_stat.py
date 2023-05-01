import numpy as np
import matplotlib.pylab as plt
from rubin_sim.satellite_constellations import (Constellation, starlink_tles_v2,
                                                oneweb_tles,
                                                ModelObservatory,
                                                SatelliteAvoidBasisFunction)
import healpy as hp
from rubin_sim.data import get_baseline
import pandas as pd
import sqlite3
import os
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--i", type=int, default=0)
    parser.add_argument("--n_blocks", type=int, default=200)
    args = parser.parse_args()

    save_file = 'streaks_all_%i.npz' % args.i

    # a starlink gen 2 + oneweb
    tles = starlink_tles_v2() # + oneweb_tles()
    const = Constellation(tles)
    print('number of satellites= ', len(tles))

    baseline = get_baseline()
    con = sqlite3.connect(baseline)
    # year 1
    visits = pd.read_sql('select fieldRA, fieldDec, fivesigmadepth, observationstartmjd,rotSkyPos,visitExposureTime,numExposures from observations where night < 365', con)
    con.close()

    keys = ['fieldRA', 'fieldDec', 'fiveSigmaDepth',
            'observationStartMJD', 'rotSkyPos', 'visitExposureTime', 'numExposures']
    types = [float] * len(keys)

    numpy_visits = np.zeros(np.size(visits["fieldRA"].values), dtype=list(zip(keys, types)))

    for key in keys:
        numpy_visits[key] = visits[key].values

    numpy_visits = np.array_split(numpy_visits, args.n_blocks)[args.i]

    streak_lengths, n_streaks = const.check_pointings(numpy_visits["fieldRA"],
                                                      numpy_visits["fieldDec"],
                                                      numpy_visits["observationStartMJD"],
                                                      visit_time=numpy_visits["visitExposureTime"]+2.*(numpy_visits["numExposures"]-1))
    np.savez(save_file, streak_lengths=streak_lengths, n_streaks=n_streaks)


    """
    exptimes = numpy_visits['visitExposureTime']+0
    exptime_before = np.sum(exptimes)
    exptimes[np.where(n_streaks > 0)] = exptimes[np.where(n_streaks > 0)]/2.
    exptime_after = np.sum(exptimes)

    print('Fractional loss of total exposure=', (exptime_before-exptime_after)/exptime_before)

    # what fraction of pixels are lost to streaks with a 1 arcmin mask
    # 
    pixscale = 0.2 # arcsec/pix
    tot_pix = 3.2e9 # total pixels in focal plane
    mask_width = 60 # arcsec

    print('fraction of pix lost', np.sum(streak_lengths/pixscale*3600 * mask_width /pixscale)/(tot_pix*np.size(streak_lengths)))
    # fraction of images with a streak
    print('fraction of streaked images= ', np.where(n_streaks > 0)[0].size/np.size(n_streaks))

    print('mean streak length', np.mean(streak_lengths)*60, ' (arcmin)') # to arcmin
    """