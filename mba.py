"""Sequential pair-support baseline. No parallel execution."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib, json, math
import pandas as pd

URL = 'https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip'

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def load_raw(path):
    sheets = pd.read_excel(path, sheet_name=None, engine='openpyxl')
    parts=[]; info={}
    for name, frame in sheets.items():
        info[name] = {'rows':len(frame), 'columns':list(frame.columns)}
        frame=frame.copy(); frame['Sheet']=name; parts.append(frame)
    return pd.concat(parts, ignore_index=True), info

def clean(raw):
    """Disjoint rejection counts, evaluated in the order below."""
    df=raw.copy(); audit={'raw_rows':len(df)}
    def reject(label, mask):
        nonlocal df
        audit[label]=int(mask.sum()); df=df.loc[~mask].copy()
    reject('missing_invoice_or_stock',df['Invoice'].isna() | df['StockCode'].isna())
    for col in ['Invoice','StockCode']: df[col]=df[col].astype(str).str.strip().str.upper()
    reject('blank_invoice_or_stock',df['Invoice'].eq('') | df['StockCode'].eq(''))
    reject('cancellation_rows',df['Invoice'].str.startswith('C'))
    q=pd.to_numeric(df['Quantity'],errors='coerce'); p=pd.to_numeric(df['Price'],errors='coerce')
    reject('nonpositive_or_invalid_quantity_price',~(q.gt(0)&p.gt(0)&q.lt(float('inf'))&p.lt(float('inf'))))
    # Reproducible conservative merchandise rule: five digits plus optional letter.
    reject('non_merchandise_codes',~df['StockCode'].str.fullmatch(r'\d{5}[A-Z]?'))
    audit['eligible_rows']=len(df)
    audit['missing_customer_retained']=int(df['Customer ID'].isna().sum())
    audit['missing_description_retained']=int(df['Description'].isna().sum())
    # Sheet is part of the invoice key; never accidentally join years.
    df=df.drop_duplicates(['Sheet','Invoice','StockCode'])
    audit['repeated_basket_product_rows_removed']=audit['eligible_rows']-len(df)
    audit['basket_product_rows']=len(df)
    return df,audit

def make_baskets(df):
    grouped=df.groupby(['Sheet','Invoice'],sort=True)['StockCode']
    return [tuple(sorted(set(v))) for _,v in grouped]

def count_pairs(baskets):
    counts=Counter()
    for basket in baskets:
        for pair in combinations(basket,2): counts[pair]+=1
    return counts

def fingerprint(counts):
    h=hashlib.sha256()
    for (a,b),n in sorted(counts.items()): h.update(f'{a}\t{b}\t{n}\n'.encode())
    return h.hexdigest()

def frequent_pairs(counts,n,min_support=0.01):
    if not 0<min_support<=1: raise ValueError('support must be in (0,1]')
    cutoff=math.ceil(min_support*n)
    return [(a,b,c,c/n) for (a,b),c in sorted(counts.items(),key=lambda x:(-x[1],x[0])) if c>=cutoff] if n else []
