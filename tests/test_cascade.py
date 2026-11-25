import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import torch
from lobbench.cascade import Fusion,paper_contrastive,jfds_autoencoder,reconstruct
from lobbench.cascade_run import splits
from lobbench.semisynthetic import overlay,inputs


def fixture(n=48):
    rng=np.random.default_rng(42);data={k:[] for k in ('raw','manual','aligned','rank','y','stock','date','id','kind','start_ns','end_ns')}
    for day,date in enumerate(('2017-01-10','2017-01-11','2017-01-12')):
        for stock in ('KGHM','PEKAO','PKNORLEN','PKOBP','PZU'):
            for i in range(n):
                x=np.zeros((25,2,5,2));x[:,0,:,0]=100-np.arange(5)*.1;x[:,1,:,0]=100.2+np.arange(5)*.1
                x[...,1]=rng.uniform(20,100,(25,2,5));ts=day*10**15+i*10**10+np.arange(25)*10**6
                kind=['background','layered','staggered','persistent','independent'][i%5]
                if kind!='background':x,_=overlay(x,rng,kind)
                raw,manual,dyn=inputs(x,ts)
                values=dict(raw=raw,manual=manual,aligned=dyn,rank=inputs(x,ts,False)[2],y=int(kind in ('layered','staggered')),
                            stock=stock,date=date,id=f'{date}-{stock}-{i}',kind=kind,start_ns=ts[0],end_ns=ts[-1])
                for k,v in values.items():data[k].append(v)
    return {k:np.asarray(v) for k,v in data.items()}


class CascadeTests(unittest.TestCase):
    def test_paper_loss_matches_positive_ratio_and_gradient(self):
        z=torch.tensor([[1.,0],[.5,.5],[0,1.]],requires_grad=True);y=torch.tensor([0,0,1])
        z0=torch.nn.functional.normalize(z,dim=1)
        a=torch.exp(z0@z0.T/.1)
        expected=(-torch.log(a[0,1]/(a[0,1]+a[0,2]))-torch.log(a[1,0]/(a[1,0]+a[1,2])))/2
        loss=paper_contrastive(z,y)
        torch.testing.assert_close(loss,expected)
        loss.backward();self.assertTrue(torch.isfinite(z.grad).all())
    def test_all_splits_disjoint_and_style_holdout(self):
        data=fixture(10)
        for regime in ('date','stock','combined','style'):
            for _,tr,va,te in splits(data,regime):
                self.assertFalse(set(tr)&set(va) or set(tr)&set(te) or set(va)&set(te))
                if regime in ('stock','combined'):
                    self.assertFalse(set(data['stock'][tr])&set(data['stock'][te]))
                if regime=='style':
                    self.assertNotIn('staggered',data['kind'][tr]);self.assertNotIn('layered',data['kind'][te])
    def test_price_alignment_does_not_invent_flow_on_rank_shift(self):
        x=np.zeros((25,2,5,2));x[:,0,:,0]=100-np.arange(5);x[:,1,:,0]=102+np.arange(5)
        x[...,1]=np.arange(5)+10
        x[1:,0,:,0]=99-np.arange(5);x[1:,0,:,1]=np.arange(5)+11
        a=inputs(x,np.arange(25),True)[2];r=inputs(x,np.arange(25),False)[2]
        self.assertEqual(a[1,0],0);self.assertGreater(r[1,0],0)
    def test_missing_trade_cancel_features_are_not_label_sidechannel(self):
        data=fixture(10)
        self.assertTrue((data['manual'][:,:,4:12]==0).all())
    def test_incremental_book_input_not_mutated(self):
        x=np.ones((25,2,5,2));orig=x.copy()
        overlay(x,np.random.default_rng(1),'layered')
        np.testing.assert_array_equal(x,orig)
    def test_portable_upstream_decoder_backward(self):
        torch.set_num_threads(1);m=jfds_autoencoder();x=torch.randn(2,25,20)
        loss=(reconstruct(m,x)-x).square().mean();loss.backward()
        self.assertTrue(torch.isfinite(loss))
    def test_fusion_parameter_budgets(self):
        counts=[sum(p.numel() for p in Fusion(d).parameters()) for d in (189,489,425)]
        self.assertLess(max(counts)/min(counts),1.01)

if __name__=='__main__':unittest.main()
