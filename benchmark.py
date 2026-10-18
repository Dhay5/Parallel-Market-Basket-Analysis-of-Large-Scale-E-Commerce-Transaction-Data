"""Identical sequential protocol for every member; times are seconds."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import argparse,csv,json,platform,statistics,subprocess,time,gc
from pathlib import Path
from datetime import datetime,timezone
import psutil
from mba import *

def cpu_model():
    try:
        if platform.system()=='Linux':
            for line in Path('/proc/cpuinfo').read_text().splitlines():
                if line.startswith('model name'):return line.split(':',1)[1].strip()
        if platform.system()=='Darwin':return subprocess.check_output(['sysctl','-n','machdep.cpu.brand_string'],text=True).strip()
        if platform.system()=='Windows':return subprocess.check_output(['powershell','-NoProfile','-Command','(Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name) -join "; "'],text=True).strip()
    except (OSError,subprocess.SubprocessError):pass
    return platform.processor() or 'UNKNOWN: fill manually'

def main():
    p=argparse.ArgumentParser();p.add_argument('--member',required=True);p.add_argument('--data',default='data');p.add_argument('--out',default='results/member');p.add_argument('--repeats',type=int,default=5);a=p.parse_args()
    if a.repeats<3:p.error('at least three repeats required; standard is five')
    root=Path(a.data);out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    baskets=json.loads((root/'baskets.json').read_text());audit=json.loads((root/'audit.json').read_text())
    if sha256(root/'baskets.json')!=audit['baskets_sha256']:raise ValueError('basket hash mismatch')
    meta={'member':a.member,'utc_time':datetime.now(timezone.utc).isoformat(),'cpu_model':cpu_model(),'physical_cores_reported':psutil.cpu_count(logical=False),'logical_cores_reported':psutil.cpu_count(),'affinity_logical_cpus':len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,'platform':platform.platform(),'python':platform.python_version(),'pandas':pd.__version__,'psutil':psutil.__version__,'ram_bytes':psutil.virtual_memory().total,'repeats':a.repeats,'warmups':1,'basket_sha256':audit['baskets_sha256'],'script_sha256':sha256(__file__),'mba_sha256':sha256(Path(__file__).with_name('mba.py')),'cgroup_cpu_max':Path('/sys/fs/cgroup/cpu.max').read_text().strip() if Path('/sys/fs/cgroup/cpu.max').exists() else None}
    (out/'hardware.json').write_text(json.dumps(meta,indent=2))
    rows=[];summaries=[]
    for fraction in [0.25,0.5,0.75,1.0]:
        n=int(len(baskets)*fraction);subset=baskets[:n];expected=None
        for run in range(a.repeats+1):
            gc.collect();start=time.perf_counter();counts=count_pairs(subset);elapsed=time.perf_counter()-start
            digest=fingerprint(counts)
            if expected is not None and expected!=digest:raise AssertionError('unstable results')
            expected=digest
            if run:rows.append(dict(member=a.member,fraction=fraction,baskets=n,basket_product_rows=sum(map(len,subset)),pair_occurrences=sum(len(b)*(len(b)-1)//2 for b in subset),run=run,count_seconds=elapsed,result_sha256=digest))
        times=[r['count_seconds'] for r in rows if r['fraction']==fraction]
        summaries.append(dict(member=a.member,fraction=fraction,baskets=n,pair_occurrences=rows[-1]['pair_occurrences'],mean_seconds=statistics.mean(times),median_seconds=statistics.median(times),stdev_seconds=statistics.stdev(times),min_seconds=min(times),max_seconds=max(times),result_sha256=expected))
        if fraction==1:
            pairs=frequent_pairs(counts,n)
            pd.DataFrame(pairs,columns=['product_a','product_b','basket_count','support']).to_csv(out/'frequent_pairs.csv',index=False)
            pd.DataFrame([(x,y,v,v/n) for (x,y),v in sorted(counts.items(),key=lambda x:(-x[1],x[0]))[:20]],columns=['product_a','product_b','basket_count','support']).to_csv(out/'top20.csv',index=False)
    for name,data in [('runs.csv',rows),('summary.csv',summaries)]:
        with open(out/name,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=data[0]);w.writeheader();w.writerows(data)
    # Separate full-pipeline phase measurements; never mixed with kernel runs.
    phases=[];book=root/'online_retail_II.xlsx'
    for run in range(a.repeats+1):
        gc.collect();t=time.perf_counter();raw,_=load_raw(book);t1=time.perf_counter();df,_=clean(raw);t2=time.perf_counter();b=make_baskets(df);t3=time.perf_counter();c=count_pairs(b);t4=time.perf_counter();f=frequent_pairs(c,len(b));t5=time.perf_counter()
        if fingerprint(c)!=expected:raise AssertionError('pipeline mismatch')
        if run:phases.append(dict(run=run,load_seconds=t1-t,clean_seconds=t2-t1,baskets_seconds=t3-t2,count_seconds=t4-t3,filter_sort_seconds=t5-t4,total_seconds=t5-t))
        del raw,df,b,c,f
    pd.DataFrame(phases).to_csv(out/'pipeline_runs.csv',index=False)
    print(pd.DataFrame(summaries).to_string(index=False))
if __name__=='__main__':main()
