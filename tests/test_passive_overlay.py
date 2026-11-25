import unittest
import numpy as np
from lobbench.passive_overlay import merge_visible,intervention,level_flows


def book():
    x=np.zeros((25,2,5,2));x[:,0,:,0]=100-np.arange(5);x[:,1,:,0]=102+np.arange(5);x[...,1]=10+np.arange(5)
    return x

class PassiveOverlayTests(unittest.TestCase):
    def test_inserted_order_remains_when_base_level_disappears(self):
        x=book()[0];x[0,:,0]-=1
        y=merge_visible(x,0,[100],[30],[True])
        np.testing.assert_array_equal(y[0,0],[100,30])
        np.testing.assert_array_equal(y[0,1],x[0,0])
    def test_hidden_order_reappears_without_losing_quantity(self):
        x=book()[0]
        y=merge_visible(x,0,[95],[30],[True]);np.testing.assert_array_equal(y,x)
        x[0,:,0]-=1;y=merge_visible(x,0,[95],[30],[True])
        self.assertEqual(y[0,-1,1],44)
    def test_marketability_is_censored_not_silently_filled(self):
        with self.assertRaisesRegex(ValueError,'marketable'):
            merge_visible(book()[0],0,[102],[30],[True])
    def test_inactive_orders_leave_exact_base_book(self):
        x=book()[0];np.testing.assert_array_equal(merge_visible(x,0,[100],[30],[False]),x)
    def test_overlay_conservation_in_fixed_visible_book(self):
        x=book()
        for kind in ('layered','staggered','benign_burst','benign_wave'):
            y,record=intervention(x,np.random.default_rng(42),kind)
            for t in range(25):
                mass=sum(v for v,a,b in zip(record['added_volume'],record['placement_steps'],record['withdrawal_steps']) if a<=t<b)
                self.assertEqual((y[t,...,1]-x[t,...,1]).sum(),mass)
    def test_known_absence_and_censored_boundary_are_distinct(self):
        x=book();x[1:,0,:,0]-=1;x[1:,0,:,1]+=1
        f=level_flows(x).reshape(25,2,5,4)
        self.assertAlmostEqual(f[1,0,0,1],10/12,places=6) # old best disappears inside coverage
        self.assertEqual(f[1,0,-1,2],0) # new worst previously outside coverage
        self.assertEqual(f[1,0,:4,0].sum(),0) # no fake additions at shared prices
    def test_joint_timing_differs_but_single_order_burst_marginals_match(self):
        # Same center/start support; sample sizes are engineering-only, not finance results.
        x=book();durations={k:[] for k in ('layered','benign_burst')}
        for kind in durations:
            rng=np.random.default_rng(1)
            for _ in range(1000):
                _,r=intervention(x,rng,kind);durations[kind].extend(np.array(r['withdrawal_steps'])-r['placement_steps'])
        self.assertLess(abs(np.mean(durations['layered'])-np.mean(durations['benign_burst'])),.2)

if __name__=='__main__':unittest.main()
