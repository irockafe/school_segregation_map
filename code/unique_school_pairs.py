import argparse
import numpy as np
import pandas as pd
import pickle
import time


def pairwise_from_multiIndex(data):
   df_idx = data.reset_index().drop(data.columns, axis=1)
   vals = df_idx.values
   # Sort each pair
   vals.sort(axis=1)
   # Get unique pairs
   return np.unique(vals, axis=0)

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
