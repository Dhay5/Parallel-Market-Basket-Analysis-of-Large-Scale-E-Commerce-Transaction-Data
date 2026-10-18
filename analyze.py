"""Run sequential analysis once on the prepared canonical baskets."""
import argparse,json
from pathlib import Path
import pandas as pd
from mba import count_pairs,frequent_pairs,sha256,fingerprint
p=argparse.ArgumentParser();p.add_argument('--data',default='data');p.add_argument('--out',default='analysis');p.add_argument('--min-support',type=float,default=.01);a=p.parse_args()
if not 0<a.min_support<=1:p.error('support must be in (0,1]')
root=Path(a.data);audit=json.loads((root/'audit.json').read_text())
if sha256(root/'baskets.json')!=audit['baskets_sha256']:raise ValueError('input hash mismatch')
baskets=json.loads((root/'baskets.json').read_text());counts=count_pairs(baskets)
rows=frequent_pairs(counts,len(baskets),a.min_support)
out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
pd.DataFrame(rows,columns=['product_a','product_b','basket_count','support']).to_csv(out/'frequent_pairs.csv',index=False)
info=dict(baskets=len(baskets),distinct_observed_pairs=len(counts),frequent_pairs=len(rows),min_support=a.min_support,result_sha256=fingerprint(counts))
(out/'analysis.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
