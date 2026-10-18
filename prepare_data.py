"""Download the official archive and prepare deterministic complete baskets."""
import argparse,json,urllib.request,zipfile
from pathlib import Path
from mba import *

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',default='data');a=p.parse_args()
    root=Path(a.data);root.mkdir(parents=True,exist_ok=True)
    archive=root/'online_retail_ii.zip';book=root/'online_retail_II.xlsx'
    if not archive.exists(): urllib.request.urlretrieve(URL,archive)
    if not book.exists():
        with zipfile.ZipFile(archive) as z:
            with z.open('online_retail_II.xlsx') as src,open(book,'wb') as dst: dst.write(src.read())
    raw,sheets=load_raw(book);df,audit=clean(raw);baskets=make_baskets(df)
    target=root/'baskets.json';target.write_text(json.dumps(baskets,separators=(',',':')))
    audit.update(sheets=sheets,archive_sha256=sha256(archive),workbook_sha256=sha256(book),baskets_sha256=sha256(target),baskets=len(baskets),products=int(df.StockCode.nunique()),date_min=str(raw.InvoiceDate.min()),date_max=str(raw.InvoiceDate.max()),raw_missing={k:int(v) for k,v in raw.isna().sum().items()},max_basket=max(map(len,baskets)),pair_occurrences=sum(len(b)*(len(b)-1)//2 for b in baskets))
    (root/'audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
if __name__=='__main__': main()
