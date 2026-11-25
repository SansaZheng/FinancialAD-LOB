import csv
from pathlib import Path
import unittest
import numpy as np
from scripts.full_wse_sessions import IndexedBook
from lobbench.wselob import WSEBook


class FullSessionTests(unittest.TestCase):
    def test_incremental_book_matches_reference(self):
        paths=list(Path('results').glob('**/*-prefix.csv'))
        self.assertTrue(paths)
        for path in paths:
            indexed, reference=IndexedBook(), WSEBook()
            with path.open() as stream:
                for i,row in enumerate(csv.DictReader(stream)):
                    indexed.apply(row); reference.apply(row)
                    if i % 127:
                        continue
                    x, valid=indexed.vector()
                    expected=reference.snapshot()
                    self.assertEqual(valid,expected['complete_depth'] and not expected['crossed_or_locked'])
                    for side,key in enumerate(('bid','ask')):
                        for level,(price,vol) in enumerate(expected[key]):
                            np.testing.assert_array_equal(x[side,level],[float(price),vol])

if __name__=='__main__':
    unittest.main()
