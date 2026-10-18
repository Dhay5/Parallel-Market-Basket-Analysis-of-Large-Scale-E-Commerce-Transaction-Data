"""Validate and combine members' actual outputs; never creates missing measurements."""
from pathlib import Path
import argparse,json
import pandas as pd
p=argparse.ArgumentParser();p.add_argument('folders',nargs='+');p.add_argument('--out',default='member_comparison.csv');a=p.parse_args()
frames=[];reference=None;members=set()
for folder in a.folders:
    root=Path(folder);h=json.loads((root/'hardware.json').read_text());s=pd.read_csv(root/'summary.csv');runs=pd.read_csv(root/'runs.csv')
    if h['member'] in members:raise ValueError('duplicate member ID')
    members.add(h['member'])
    if h['repeats']!=5:raise ValueError('standard protocol requires five repeats')
    signatures=(h['basket_sha256'],h['script_sha256'],h['mba_sha256'],tuple(s.result_sha256))
    if reference is None:reference=signatures
    if signatures!=reference:raise ValueError('input/code/result hashes differ')
    for row in s.itertuples():
        times=runs.loc[runs.fraction==row.fraction,'count_seconds']
        if len(times)!=5 or abs(times.mean()-row.mean_seconds)>1e-8:raise ValueError('summary differs from raw runs')
    for field in ['cpu_model','physical_cores_reported','logical_cores_reported','platform','python']:s[field]=h[field]
    frames.append(s)
pd.concat(frames,ignore_index=True).to_csv(a.out,index=False)
print(f'Combined {len(members)} real result folders into {a.out}; no missing members were filled.')
