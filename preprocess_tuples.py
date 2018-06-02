import os, sys
import pandas as pd
import numpy as np

from root_pandas import read_root

DEBUG = True

hits_branches = ['rechit_skiroc',
        'rechit_channel',
        'rechit_x',
        'rechit_y',
        'rechit_energy',
        'rechit_layer'
        ]

info_branches = ['run', 'event','PI_positionX', 'PI_positionY',]

tracks_branches = ['ntracks',
         'impactX_HGCal_layer_1',
         'impactY_HGCal_layer_1'
        ]

def rh_filter(rh_row, layer = 1):
    '''
    select = (rh_row.rechit_layer == layer)
    select &= rh_row.rechit_energy > 0.5
    #return len(rh_row.rechit_x[select])
    return sum(select)
    '''
    return sum((rh_row.rechit_layer == layer) & (rh_row.rechit_energy > 0.5))


def process(fnames = ["calo_setup/ntuple_1222.root"], outdir = "./test/"):

    if DEBUG: print("Reading files")
    df_hits = read_root(fnames, "rechitntupler/hits", columns = hits_branches)
    df_info = read_root(fnames, "rechitntupler/hits", columns = info_branches)
    df_tracks = read_root(fnames, "trackimpactntupler/impactPoints", columns = tracks_branches)

    df_all = pd.concat([df_info, df_hits, df_tracks], axis=1, join_axes=[df_hits.index])

    # ### Clean ntracks == 1 events and create new branch
    selection = df_all.ntracks > 0
    df_all = df_all[selection]

    if DEBUG: print("Adding nhits")
    #df_all['nhits'] = df_all.apply(rh_filter, axis=1)
    df_all['nhits'] = df_all.apply(lambda row:
                                   sum((row.rechit_layer == 1) & (row.rechit_energy > 0.5)),
                                   axis=1)

    # ### Clean nhits > 0 events and create new branch
    selection = df_all.nhits > 0
    df_all = df_all[selection]

    # ### Define globalimpact position from the single track
    if DEBUG: print("Computing impact position")
    ## convert Series to float for impact position (take first element, which for ntracks=1 is the only one)


    '''
    impact_x = df_all.apply(lambda row:
                            row.impactX_HGCal_layer_1[0] - max(row.PI_positionX,0),
                            axis=1)
    impact_y = df_all.apply(lambda row:
                            row.impactY_HGCal_layer_1[0] - max(row.PI_positionY,0),
                            axis=1)


    impact_x = df_all.apply(lambda row: row.impactX_HGCal_layer_1[0], axis=1)
    impact_y = df_all.apply(lambda row: row.impactY_HGCal_layer_1[0], axis=1)

    df_all.loc[impact_x.index, 'impact_x'] = impact_x
    df_all.loc[impact_y.index, 'impact_y'] = impact_y

    '''

    # create columns for impacts
    df_all.loc[impact_x.index, 'impact_x'] = df_all.apply(
        lambda row:
        row.impactX_HGCal_layer_1[0] - max(row.PI_positionX,0),
        axis=1)

    df_all.loc[impact_y.index, 'impact_y'] = df_all.apply(
        lambda row:
        row.impactY_HGCal_layer_1[0] - max(row.PI_positionX,0),
        axis=1)

    # Fix PI position: put to 0 if not available
    #df_all.PI_positionX = df_all.apply(lambda row: max(row.PI_positionX,0), axis=1)
    #df_all.PI_positionY = df_all.apply(lambda row: max(row.PI_positionY,0), axis=1)

    # Construct impact from track impact and PI position
    #df_all['impact_x'] = df_all.impact_x - df_all.PI_positionX
    #df_all['impact_y'] = df_all.impact_y - df_all.PI_positionY

    # scale to cm
    df_all['impact_x'] /= 10
    df_all['impact_y'] /= 10

    # ### Remove unneeded branches like PI position, etc.

    drop_columns = ['PI_positionY', 'PI_positionX', 'impactY_HGCal_layer_1', 'impactX_HGCal_layer_1']
    df_all = df_all.drop(columns=drop_columns, axis=0)

    # ### Clean rechits: Series -> values (select only first rechit)
    if DEBUG: print("Cleaning rechits")
    for branch in hits_branches:
        df_all[branch] = df_all[branch].apply(lambda x: x[0])

    outfname = outdir + os.path.dirname(fnames[0]) + "/ntuple_preprocessed_combined.root" #fname
    outbasedir = os.path.dirname(outfname)

    if DEBUG: print("Writing to " + outfname)
    if not os.path.exists(outbasedir): os.makedirs(outbasedir)
    df_all.to_root(outfname,key = "tree")


if __name__ == "__main__":

    if len(sys.argv) > 1:
        fnames = sys.argv[1:]
    else:
        fnames = ["calo_setup/ntuple_1222.root"]

    print fnames

    process(fnames)
    #for fname in fnames:
    #    print "Processing", fname
    #    process(fname)
