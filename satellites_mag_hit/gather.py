import numpy as np


if __name__ == "__main__":


    lengths = []
    ns = []

    for i in np.arange(200):
        filename = "streaks_all_%i.npz" % i
        data = np.load(filename)
        lengths.append(data["streak_lengths"].copy())
        ns.append(data["n_streaks"].copy())
        data.close()


    streak_lengths = np.concatenate(lengths)
    n_streaks = np.concatenate(ns)

    np.savez("streaks_all.npz", streak_lengths=streak_lengths, n_streaks=n_streaks)
    