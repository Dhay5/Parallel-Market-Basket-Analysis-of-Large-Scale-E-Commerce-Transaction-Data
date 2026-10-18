from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).parent/'results/reference_environment'
s=pd.read_csv(root/'summary.csv');p=pd.read_csv(root/'pipeline_runs.csv')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(7,3.6));ax.errorbar(s.baskets,s.mean_seconds,yerr=s.stdev_seconds,marker='o',capsize=4,color='#215c92');ax.set(xlabel='Complete baskets in deterministic prefix',ylabel='Pair counting time in seconds',title='Sequential counting in the reference environment');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(root/'scaling.png',dpi=180);plt.close(fig)
cols=['load_seconds','clean_seconds','baskets_seconds','count_seconds','filter_sort_seconds'];means=p[cols].mean()
fig,ax=plt.subplots(figsize=(7,3.6));ax.barh(['Load workbook','Clean rows','Build baskets','Count pairs','Filter and sort'],means,color='#215c92');ax.set(xlabel='Mean seconds over five measured runs',title='Full input phase costs in the reference environment');ax.invert_yaxis();ax.grid(axis='x',alpha=.2);fig.tight_layout();fig.savefig(root/'phases.png',dpi=180)
