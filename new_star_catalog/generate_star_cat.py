import numpy as np
from dl import queryClient as qc
import healpy as hp
import pandas as pd
import io
import sys
import argparse
import time


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--block", type=int, default=0)
    args = parser.parse_args()
    n_split = 20

    n_keep = 2
    n_pix = hp.nside2npix(256)
    results = []

    filtername = 'r'
    print("npix=", n_pix)

    indx = np.array_split(np.arange(n_pix), n_split)[args.block]

    for i in indx:
        try:
            result = qc.query(sql='SELECT ra,dec,umag,gmag,rmag,imag,zmag,ymag,ring256 FROM lsst_sim.simdr2 WHERE %smag > 17 and %smag < 17.5 and ring256=%i LIMIT 10;' % (filtername, filtername, i))
        except:
            # getting weird "502 Bad Gateway" error, let's just throw in a pause 
            time.sleep(5.)
            result = qc.query(sql='SELECT ra,dec,umag,gmag,rmag,imag,zmag,ymag,ring256 FROM lsst_sim.simdr2 WHERE %smag > 17 and %smag < 17.5 and ring256=%i LIMIT 10;' % (filtername, filtername, i))
        df = pd.read_csv(io.StringIO(result))
        #if df.shape[0] < n_keep:
        #    result = qc.query(sql='SELECT ra,dec,umag,gmag,rmag,imag,zmag,ymag,ring256 FROM lsst_sim.simdr2 WHERE %smag > 17 and %smag < 18 and ring256=%i LIMIT 10;' % (filtername, filtername, i))
        #    df = pd.read_csv(io.StringIO(result))
        if df.shape[0] > 0:
            df = df.sort_values('rmag')[0:n_keep]
            results.append(df)

        progress = float(i) / n_pix * 100
        text = "\rprogress = %.2f%%, %i" % (progress, i)
        sys.stdout.write(text)
        sys.stdout.flush()

    if len(results) > 0:
        stars = pd.concat(results)
        stars.to_hdf('%s_stars_block_%i.h5' % (filtername, args.block))
    else:
        with open('%s_stars_block_%i.txt' % (filtername, args.block), 'w') as f:
            print("no results", file=f)
