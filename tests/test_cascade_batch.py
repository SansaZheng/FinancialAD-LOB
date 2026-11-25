"""Device isolation under concurrent completions and exceptions."""
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Lock
import time
import unittest
from unittest.mock import patch
from scripts.run_cascade_batch import leased_execute


class DeviceLeaseTests(unittest.TestCase):
    def test_concurrent_children_never_share_device(self):
        devices=Queue();devices.put(0);devices.put(1)
        active=set();seen=[];lock=Lock()
        def child(index,gpu_id):
            with lock:
                self.assertNotIn(gpu_id,active);active.add(gpu_id);seen.append(gpu_id)
            time.sleep(.01 if index%2 else .02)
            with lock:active.remove(gpu_id)
        with patch('scripts.run_cascade_batch.execute',side_effect=child):
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda i:leased_execute(devices,i),range(8)))
        self.assertEqual(set(seen),{0,1});self.assertEqual(devices.qsize(),2)

    def test_exception_returns_device(self):
        devices=Queue();devices.put(1)
        with patch('scripts.run_cascade_batch.execute',side_effect=RuntimeError('child failed')):
            with self.assertRaises(RuntimeError):leased_execute(devices,0)
        self.assertEqual(devices.get_nowait(),1)
