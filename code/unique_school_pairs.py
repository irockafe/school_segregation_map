import argparse
import numpy as np
import pandas as pd
import pickle
import time


def pairwise_from_multiIndex(data):
    df_idx = data.reset_index().drop(data.columns, axis=1)
    schools = df_idx['central_school'].unique()
    out = {}
    for i, school in enumerate(schools):
        # get neighboring schools
        subset = df_idx[df_idx['central_school'] == school]
        out[school] = subset['neighbors'].values
        # Change any remaining entries for that school to zero
        # so we don't double count
        to_drop = np.where(df_idx['neighbors'] == school)
        df_idx.iloc[to_drop] = 0
    return out

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str,
        help='Path to pickled file containing multi-Index df')
args = parser.parse_args()
data = pickle.load(open(args.path, 'rb'))
t1 = time.time()
pairwise = pairwise_from_multiIndex(data)
out_path = args.path.replace('.pkl', '') + '_pairwise.pkl'
pickle.dump(pairwise, open(out_path, 'wb'))
print(time.time() - t1)
