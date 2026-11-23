import unittest
import torch
from lobbench.models import LiquidityDynamics, paired_loss

torch.set_num_threads(1)


class ModelChecks(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(0)
        self.model = LiquidityDynamics(width=16).eval()
        self.x = torch.randn(2, 12, 10, 8)

    def test_future_perturbation_cannot_change_past_logits(self):
        changed = self.x.clone()
        changed[:, 7:] += 100
        with torch.no_grad():
            torch.testing.assert_close(self.model(self.x)[:, :7], self.model(changed)[:, :7])

    def test_reordering_price_tokens_preserves_output(self):
        with torch.no_grad():
            torch.testing.assert_close(self.model(self.x), self.model(self.x[:, :, torch.randperm(10)]))

    def test_optimizer_step_is_finite(self):
        optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)
        before = self.model.head.weight.detach().clone()
        labels = torch.tensor([0., 1.])
        loss = paired_loss(self.model(self.x)[:, -1], self.model(self.x)[:, -1], labels)
        loss.backward()
        self.assertTrue(all(torch.isfinite(p.grad).all() for p in self.model.parameters() if p.grad is not None))
        optimizer.step()
        self.assertFalse(torch.equal(before, self.model.head.weight))


if __name__ == "__main__": unittest.main()
