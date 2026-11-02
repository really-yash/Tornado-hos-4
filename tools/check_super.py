#!/usr/bin/env python3
"""Hard validation of an Android sparse super.img. Exit 0 only if fully consistent."""
import os, struct, subprocess, sys

f = sys.argv[1]
raw = sys.argv[2] if len(sys.argv) > 2 else "/tmp/super_raw.img"
sz = os.path.getsize(f)
d = open(f, "rb")
if struct.unpack("<I", d.read(4))[0] != 0xED26FF3A:
    sys.exit("FAIL: not an Android sparse image")
d.seek(0)
_, ma, mi, fh, ch, bs, tb, tc, _ = struct.unpack("<IHHHHIIII", d.read(28))
print(f"sparse v{ma}.{mi} blk={bs} blocks={tb} chunks={tc} raw={tb*bs/2**20:.0f}MiB")
d.seek(fh)
blocks = bad = 0
for i in range(tc):
    h = d.read(ch)
    if len(h) < ch:
        sys.exit(f"FAIL: truncated at chunk {i}")
    t, _, cs, ts = struct.unpack("<HHII", h[:12])
    exp = {0xCAC1: ch + cs * bs, 0xCAC2: ch + 4, 0xCAC3: ch, 0xCAC4: ch + 4}.get(t)
    if exp is None or exp != ts:
        bad += 1
    d.seek(ts - ch, 1)
    blocks += cs
pos = d.tell()
if bad or blocks != tb or pos != sz:
    sys.exit(f"FAIL: bad_chunks={bad} blocks={blocks}/{tb} end={pos} size={sz}")
print("chunk structure OK")
subprocess.run(["simg2img", f, raw], check=True)
rsz = os.path.getsize(raw)
if rsz != tb * bs:
    sys.exit(f"FAIL: decoded size {rsz} != {tb*bs}")
with open(raw, "rb") as r:
    r.seek(4096)
    magic = struct.unpack("<I", r.read(4))[0]
os.remove(raw)
if magic != 0x616C4467:
    sys.exit("FAIL: LP geometry magic missing (not a valid super image)")
print("simg2img decode OK, LP geometry OK")

