"""Bounded, read-only HTTP range access; never silently download a whole archive."""
import io
import urllib.request


class HTTPRangeFile(io.RawIOBase):
    def __init__(self, url, size, max_bytes=16 * 1024**2, block_size=65536, headers=None):
        super().__init__()
        if size <= 0 or max_bytes <= 0 or block_size <= 0:
            raise ValueError("size and budgets must be positive")
        self.url, self.size = url, size
        self.max_bytes, self.block_size = max_bytes, block_size
        self.headers = dict(headers or {})
        self.position, self.downloaded, self.requests = 0, 0, 0
        self.range_rejections = 0
        self.cache = {}

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        if whence not in (0, 1, 2):
            raise ValueError("invalid whence")
        pos = offset + (0 if whence == 0 else self.position if whence == 1 else self.size)
        if pos < 0:
            raise ValueError("negative seek")
        self.position = pos
        return pos

    def _block(self, number):
        if number not in self.cache:
            start = number * self.block_size
            end = min(start + self.block_size, self.size) - 1
            length = end - start + 1
            if self.downloaded + length > self.max_bytes:
                raise RuntimeError("HTTP sample byte budget exhausted")
            headers = {**self.headers, "Range": f"bytes={start}-{end}", "Accept-Encoding": "identity",
                       "Cache-Control": "no-cache"}
            # Public CDN occasionally returns HTTP 200 for a range. Close it
            # without reading its body; at most three identical bounded tries.
            for attempt in range(3):
                request = urllib.request.Request(self.url, headers=headers)
                self.requests += 1
                with urllib.request.urlopen(request, timeout=30) as response:
                    expected = f"bytes {start}-{end}/{self.size}"
                    if response.status != 206 or response.headers.get("Content-Range") != expected:
                        self.range_rejections += 1
                        error = (f"Range mismatch: expected {expected}; got status={response.status}, "
                                 f"Content-Range={response.headers.get('Content-Range')}")
                        continue
                    data = response.read(length + 1)
                    self.downloaded += len(data)
                    if len(data) != length:
                        raise RuntimeError("Incomplete or oversized HTTP range")
                    self.cache[number] = data
                    break
            else:
                raise RuntimeError(error)
        return self.cache[number]

    def read(self, size=-1):
        if size is None or size < 0:
            size = self.size - self.position
        count = max(0, min(size, self.size - self.position))
        if count > self.max_bytes:
            raise RuntimeError("Read exceeds HTTP sample byte budget")
        chunks = []
        while count:
            number, offset = divmod(self.position, self.block_size)
            block = self._block(number)
            n = min(count, len(block) - offset)
            chunks.append(block[offset:offset+n])
            self.position += n
            count -= n
        return b"".join(chunks)

    def readinto(self, buffer):
        data = self.read(len(buffer))
        buffer[:len(data)] = data
        return len(data)
