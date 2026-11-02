#!/usr/bin/env python3
"""Resolve a gofile.io page URL to real download links, download, verify size+md5.
Exit codes: 0 ok | 3 could not list/resolve (use fallback) | 4 verification failed."""
import argparse, hashlib, json, os, re, sys, time
import requests

API = "https://api.gofile.io"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")


def log(*a):
    print(*a, flush=True)


def get_token(s):
    t = os.environ.get("GOFILE_TOKEN")
    if t:
        return t
    r = s.post(f"{API}/accounts", timeout=30)
    r.raise_for_status()
    return r.json()["data"]["token"]


def website_tokens(s):
    cands = [None]  # first try without a website token
    for u in ("https://gofile.io/dist/js/global.js",
              "https://gofile.io/dist/js/alljs.js",
              "https://gofile.io/dist/js/wt.obf.js"):
        try:
            txt = s.get(u, timeout=30).text
            for m in re.finditer(r'wt\s*[:=]\s*["\']([A-Za-z0-9]{6,})["\']', txt):
                if m.group(1) not in cands:
                    cands.append(m.group(1))
        except Exception as e:
            log("  wt fetch failed:", u, e)
    return cands


def list_content(s, cid, token):
    last = None
    for wt in website_tokens(s):
        h = {"Authorization": f"Bearer {token}"}
        params = {"cache": "true"}
        if wt:
            h["X-Website-Token"] = wt
            params["wt"] = wt
        try:
            j = s.get(f"{API}/contents/{cid}", headers=h, params=params, timeout=30).json()
        except Exception as e:
            last = e
            continue
        if j.get("status") == "ok":
            return j["data"]
        last = j.get("status")
        log(f"  contents request failed ({last}), website-token used: {bool(wt)}")
    raise RuntimeError(f"cannot list {cid}: {last}")


def walk(node, out):
    if node.get("type") == "file":
        out.append(node)
        return
    for c in (node.get("children") or {}).values():
        walk(c, out)


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def download(s, f, outdir, token):
    name, size, md5, link = f["name"], f.get("size"), f.get("md5"), f["link"]
    path = os.path.join(outdir, name)
    log(f"-> {name}  size={size}  md5={md5}")
    for attempt in range(1, 11):
        have = os.path.getsize(path) if os.path.exists(path) else 0
        if size and have == size:
            break
        if size and have > size:
            os.remove(path)
            have = 0
        h = {"Cookie": f"accountToken={token}", "User-Agent": UA,
             "Referer": "https://gofile.io/"}
        if have:
            h["Range"] = f"bytes={have}-"
        try:
            with s.get(link, headers=h, stream=True, timeout=60) as r:
                if r.status_code not in (200, 206):
                    raise RuntimeError(f"HTTP {r.status_code}")
                mode = "ab" if (have and r.status_code == 206) else "wb"
                with open(path, mode) as fh:
                    for chunk in r.iter_content(1 << 20):
                        fh.write(chunk)
        except Exception as e:
            log(f"   attempt {attempt} failed: {e}")
            time.sleep(5 * attempt)
    got = os.path.getsize(path) if os.path.exists(path) else -1
    if size and got != size:
        log(f"   SIZE MISMATCH {got} != {size}")
        sys.exit(4)
    if md5:
        m = md5_of(path)
        if m != md5:
            log(f"   MD5 MISMATCH {m} != {md5}")
            sys.exit(4)
        log("   size + md5 verified")
    else:
        log("   (no md5 from API, size checked only)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("outdir")
    ap.add_argument("--only", nargs="*", default=None, help="only these file names")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    cid = a.url.rstrip("/").split("/")[-1]
    s = requests.Session()
    s.headers["User-Agent"] = UA
    try:
        token = get_token(s)
        files = []
        walk(list_content(s, cid, token), files)
    except Exception as e:
        log("RESOLVE FAILED:", e)
        sys.exit(3)
    if a.only:
        files = [f for f in files if f["name"] in a.only]
    if not files:
        log("no matching files on page")
        sys.exit(3)
    for f in files:
        download(s, f, a.outdir, token)
    log("done")


if __name__ == "__main__":
    main()
