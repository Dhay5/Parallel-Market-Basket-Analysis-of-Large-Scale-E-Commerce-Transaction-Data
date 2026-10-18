import unittest,random
from collections import Counter
import pandas as pd
from mba import *
class Tests(unittest.TestCase):
    def test_known(self):
        b=[('A','B','C'),('A','B'),('B',),()]
        self.assertEqual(count_pairs(b),{('A','B'):2,('A','C'):1,('B','C'):1})
        self.assertEqual(frequent_pairs(count_pairs(b),4,0.5),[('A','B',2,0.5)])
    def test_clean(self):
        rows=[('1','10000',1,2),('1','10000',3,2),('1','10001',1,2),('C2','10000',1,2),('3','10000',0,2),('4','POST',1,2),('5',None,1,2),('6','10000',1,-1)]
        raw=pd.DataFrame(rows,columns=['Invoice','StockCode','Quantity','Price']);raw['Sheet']='s';raw['Customer ID']=None;raw['Description']=None
        second=raw.iloc[[0]].copy();second['Sheet']='t';raw=pd.concat([raw,second],ignore_index=True)
        df,a=clean(raw);b=make_baskets(df)
        self.assertEqual(b,[('10000','10001'),('10000',)])
        self.assertEqual(count_pairs(b),{('10000','10001'):1})
        self.assertEqual(a['repeated_basket_product_rows_removed'],1)
    def test_oracle(self):
        rng=random.Random(503)
        for _ in range(100):
            baskets=[tuple(sorted(rng.sample(list('ABCDE'),rng.randrange(6)))) for _ in range(20)]
            oracle=Counter()
            for a in 'ABCDE':
                for b in 'ABCDE':
                    if a<b:
                        n=sum(a in x and b in x for x in baskets)
                        if n:oracle[a,b]=n
            self.assertEqual(count_pairs(baskets),oracle)
    def test_empty(self):
        self.assertEqual(count_pairs([]),{})
        self.assertEqual(frequent_pairs(Counter(),0),[])
if __name__=='__main__':unittest.main()
