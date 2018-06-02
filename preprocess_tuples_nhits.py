import os, sys
import pandas as pd
import numpy as np

from root_pandas import read_root

'''
hits_branches = ['rechit_skiroc',
        'rechit_channel',
        'rechit_x',
        'rechit_y',
        'rechit_energy',
        'rechit_layer'
        ]
'''
hits_branches = ['rechit_energy','rechit_layer']

info_branches = ['run', 'event','PI_positionX', 'PI_positionY',]

tracks_branches = ['ntracks',
         'impactX_HGCal_layer_1',
         'impactY_HGCal_layer_1'
        ]

def rh_filter(rh_row, layer = 1):
    select = (rh_row.rechit_layer == layer)
    select &= rh_row.rechit_energy > 0.3
    return len(rh_row.rechit_layer[select])


def process(fnames = ["calo_setup/ntuple_1222.root"], outdir = "./test_v2/"):

    df_hits = read_root(fnames, "rechitntupler/hits", columns = hits_branches)
    #df_info = read_root(fnames, "rechitntupler/hits", columns = info_branches)
    #df_tracks = read_root(fnames, "trackimpactntupler/impactPoints", columns = tracks_branches)
    #df_all = pd.concat([df_info, df_hits, df_tracks], axis=1, join_axes=[df_hits.index])
    df_all = pd.concat([df_hits], axis=1, join_axes=[df_hits.index])

    all_columns = df_all.columns

    df_all['nhits'] = df_all.apply(rh_filter, axis=1)

    # ### Remove unneeded branches like PI position, etc.

    drop_columns = all_columns#['PI_positionY', 'PI_positionX', 'impactY_HGCal_layer_1', 'impactX_HGCal_layer_1']
    df_all = df_all.drop(columns=drop_columns, axis=0)

    outfname = outdir + fname[0] #"merge_nhits.root"#fnames
    outbasedir = os.path.dirname(outfname)

    if not os.path.exists(outbasedir): os.makedirs(outbasedir)
    df_all.to_root(outfname,key = "tree")


if __name__ == "__main__":

    if len(sys.argv) > 1:
        fnames = sys.argv[1:]
    else:
        fnames = ["calo_setup/ntuple_1222.root"]

    print fnames

    #process(fnames)
    for fname in fnames:
        print "Processing", fname
        process(fname)

