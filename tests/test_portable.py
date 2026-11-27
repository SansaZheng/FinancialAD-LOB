import json,tempfile,unittest
from pathlib import Path
import numpy as np
import torch
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.svm import OneClassSVM
from lobbench.portable import interactions,block_indices,export_hgb,tree_score,export_dense,dense,export_ae,ae_encode,ocsvm_score,rbf
from lobbench.direct import DirectMLP
from lobbench.cascade import jfds_autoencoder,encode

class PortableTests(unittest.TestCase):
 def test_full_factorial_layout_zero_and_exact_diagonal(self):
  rng=np.random.default_rng(5);x=rng.random((7,25,2,5,4)).astype('float32');x[...,2:]=1
  a=interactions(x);b=interactions(np.asfortranarray(x));np.testing.assert_array_equal(a,b);np.testing.assert_array_equal(a,np.concatenate([interactions(x[:3]),interactions(x[3:])]))
  np.testing.assert_array_equal(interactions(np.zeros_like(x)),0)
  for offset in [0,50]:
   g=a[:,offset:offset+50].reshape(7,2,5,5);np.testing.assert_array_equal(np.diagonal(g,axis1=2,axis2=3),1.)
  self.assertEqual(len(block_indices('all')),488);self.assertEqual(len(block_indices('gram_lag')),400)
  self.assertFalse(set(block_indices('moments'))&set(block_indices('gram_lag')))
  with self.assertRaises(ValueError):block_indices('gram_gram')
 def test_tree_export_missing_values_and_nonlinear_boundary(self):
  rng=np.random.default_rng(8);x=rng.normal(size=(240,6));x[::19,2]=np.nan;y=(x[:,0]*x[:,1]>.15).astype(int)
  m=HistGradientBoostingClassifier(max_iter=15,max_leaf_nodes=7,early_stopping=False).fit(x,y)
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'tree.json';doc=export_hgb(m,p);np.testing.assert_allclose(tree_score(doc,x),m.predict_proba(x)[:,1],atol=6e-13,rtol=0);np.testing.assert_array_equal(tree_score(json.loads(p.read_text()),x),tree_score(doc,x))
 def test_dense_numpy_matches_double_torch(self):
  torch.manual_seed(2);m=DirectMLP(13);x=np.random.default_rng(4).normal(size=(23,13)).astype('float32')
  with tempfile.TemporaryDirectory() as td:
   values=export_dense(m,Path(td)/'m.npz');expected=m.double()(torch.tensor(x,dtype=torch.float64)).detach().numpy();np.testing.assert_allclose(dense(values,x),expected,atol=5.1e-9,rtol=0)
 def test_numpy_frozen_transformer_matches_double_torch(self):
  torch.set_num_threads(1);torch.manual_seed(3);m=jfds_autoencoder().eval();x=np.random.default_rng(5).normal(size=(4,25,20)).astype('float32')
  with tempfile.TemporaryDirectory() as td:
   state=export_ae(m,Path(td)/'ae.npz');actual=ae_encode(state,x,batch=2)
   with torch.no_grad():expected=encode(m.double(),torch.tensor(x,dtype=torch.float64)).numpy()
   np.testing.assert_allclose(actual,expected,rtol=0,atol=6e-7);np.testing.assert_array_equal(actual,ae_encode(state,x,batch=4))
 def test_ocsvm_data_export_score_sign_and_offset(self):
  rng=np.random.default_rng(7);x=rng.normal(size=(45,6));query=rng.normal(size=(12,6));gamma=.1/6;m=OneClassSVM(kernel='precomputed',nu=.05).fit(rbf(x,x,gamma));values=dict(mean=np.zeros(6),scale=np.ones(6),support=x[m.support_],dual=m.dual_coef_.ravel(),gamma=gamma)
  np.testing.assert_allclose(ocsvm_score(values,query),-m.score_samples(rbf(query,x,gamma)),rtol=0,atol=5.1e-9)
