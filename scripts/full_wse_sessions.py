"""CQ-only acquisition of complete public daily HDF partitions and book snapshots.

The whole source archive is not downloaded. All source daily rows are retained;
09:00 <= Europe/Warsaw <16:50 is a declared continuous-session time filter, not
an exchange phase feed. Invalid/crossed books remain flagged and break windows.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo
import h5py
import numpy as np
from lobbench.http_range import HTTPRangeFile
from lobbench.wselob import WSEBook


class IndexedBook(WSEBook):
    """Exact incremental aggregation of WSEBook's explicit limit-order view."""
    def __init__(self):
        super().__init__()
        self.depth = [defaultdict(int), defaultdict(int)]

    def adjust(self, order, sign):
        if not order or order['order_type'] != '2' or order['price'] <= 0 or order['volume'] == 0:
            return
        side = 0 if order['side'] == 1 else 1
        price = Decimal(order['price']).scaleb(-order['price_level'])
        self.depth[side][price] += sign * order['volume']
        if self.depth[side][price] == 0:
            del self.depth[side][price]

    def apply(self, row):
        key = (int(row['symbol_idx']), int(row['order_date']), int(row['order_id']))
        old = self.orders.get(key)
        super().apply(row)  # retain fail-closed semantics before mutating index
        if row['action_type'] == 'F':
            self.depth = [defaultdict(int), defaultdict(int)]
        else:
            self.adjust(old, -1)
            self.adjust(self.orders.get(key), 1)

    def vector(self):
        bid = sorted(self.depth[0], reverse=True)[:5]
        ask = sorted(self.depth[1])[:5]
        valid = len(bid) == len(ask) == 5 and bid[0] < ask[0]
        x = np.zeros((2, 5, 2), dtype=np.float64)
        for side, prices in enumerate((bid, ask)):
            for level, price in enumerate(prices):
                x[side, level] = (float(price), self.depth[side][price])
        return x, valid


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect(manifest, output, stocks, days, stride=1):
    if not os.environ.get('CQ_JOB_ID'):
        raise RuntimeError('Full-day acquisition requires CQ; no bulk data on local Mac')
    output.mkdir(parents=True, exist_ok=True)
    source = json.loads(manifest.read_text())
    audit = dict(status='partial', evidence_class='complete_public_daily_partitions_unlabeled',
                 cq_job=os.environ['CQ_JOB_ID'], license=source['license'],
                 source=source['source_url'], full_source_archive_hash_verified=False,
                 session_timezone='Europe/Warsaw', session_start='09:00:00', session_end_exclusive='16:50:00',
                 session_filter_limitation='Clock filter only; no phase/volatility-halt feed',
                 snapshot_stride_events=stride, partitions=[], transfers=[])
    for stock in stocks:
        spec = source['files'][stock]
        remote = HTTPRangeFile(spec['url'], spec['bytes'], max_bytes=64*1024**2,
                               headers={'User-Agent':'Mozilla/5.0','Referer':source['source_url']})
        with h5py.File(remote, 'r') as hdf:
            for day in days:
                table = hdf['d'+day.replace('-','')]['table']
                values = table[:]
                if values.dtype.hasobject or not len(values):
                    raise ValueError('Unsafe or empty daily partition')
                if (np.diff(values['time']) < 0).any():
                    raise ValueError('Noncausal source ordering')
                raw = output / f'{stock}-{day}-orders.npz'
                np.savez_compressed(raw, orders=values)
                start = int(datetime.fromisoformat(day+'T09:00:00').replace(tzinfo=ZoneInfo('Europe/Warsaw')).timestamp()*1e9)
                end = int(datetime.fromisoformat(day+'T16:50:00').replace(tzinfo=ZoneInfo('Europe/Warsaw')).timestamp()*1e9)
                book = IndexedBook()
                xs, ts, ids, valid = [], [], [], []
                actions = Counter()
                fields = values.dtype.names
                for i, record in enumerate(values):
                    row = {k: (v.decode('ascii') if isinstance(v, bytes) else int(v)) for k,v in zip(fields, record)}
                    try:
                        book.apply(row)
                    except ValueError as exc:
                        raise ValueError(f'{stock} {day} row {i}: {exc}') from exc
                    actions[row['action_type']] += 1
                    if start <= row['time'] < end and i % stride == 0:
                        x, ok = book.vector()
                        xs.append(x); ts.append(row['time']); ids.append(i); valid.append(ok)
                snap = output / f'{stock}-{day}-book.npz'
                np.savez_compressed(snap, x=np.asarray(xs), time_ns=np.asarray(ts,dtype=np.int64),
                                    source_row=np.asarray(ids,dtype=np.int64), valid=np.asarray(valid,dtype=bool))
                item = dict(stock=stock,date=day,source_rows=len(table),retained_rows=len(values),
                            source_min_ns=int(values['time'][0]),source_max_ns=int(values['time'][-1]),
                            session_snapshots=len(xs),valid_snapshots=int(sum(valid)),invalid_snapshots=len(xs)-int(sum(valid)),
                            session_first_ns=int(ts[0]) if ts else None,session_last_ns=int(ts[-1]) if ts else None,
                            action_counts=dict(actions),raw_file=raw.name,raw_bytes=raw.stat().st_size,raw_sha256=digest(raw),
                            book_file=snap.name,book_bytes=snap.stat().st_size,book_sha256=digest(snap))
                audit['partitions'].append(item)
                (output/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
                print(json.dumps(item),flush=True)
        audit['transfers'].append(dict(stock=stock,bytes=remote.downloaded,requests=remote.requests,range_rejections=remote.range_rejections))
        remote.close()
    audit['status']='complete'
    (output/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    return audit


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--manifest',type=Path,default=Path('data/manifests/wselob-source-locators.json'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--stocks',nargs='+',default=['KGHM','PEKAO','PKNORLEN','PKOBP','PZU'])
    p.add_argument('--days',nargs='+',default=['2017-01-10','2017-01-11','2017-01-12'])
    args=p.parse_args()
    collect(args.manifest,args.output,args.stocks,args.days)
