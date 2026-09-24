#!/usr/bin/env python3
"""构建产物上传到 Komari 并切换为当前主题。
用法: deploy-nexus.py <zip> [--no-activate]
凭据: 环境变量 KOMARI_PASSWORD，或 ~/.hermes/cache/scratch/komari-admin.pw（0600）。
"""
import json, os, sys, uuid, urllib.request, urllib.error, http.cookiejar

BASE = os.environ.get("KOMARI_BASE", "http://127.0.0.1:25774")
USER = os.environ.get("KOMARI_USER", "admin")
PWF = os.path.expanduser("~/.hermes/cache/scratch/komari-admin.pw")
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
UA = {"Origin": BASE, "User-Agent": "Mozilla/5.0 komari-nexus-deploy"}


def req(method, path, body=None, ctype="application/json"):
    h = dict(UA)
    if body is not None:
        h["Content-Type"] = ctype
    r = urllib.request.Request(BASE + path, data=body, method=method, headers=h)
    try:
        raw = op.open(r, timeout=60).read()
    except urllib.error.HTTPError as e:
        raw = e.read()
    d = json.loads(raw)
    if d.get("status") != "success":
        sys.exit(f"{method} {path} failed: {d.get('message')}")
    return d.get("data")


def multipart(fields, fname, fdata):
    b = uuid.uuid4().hex
    out = []
    for k, v in fields.items():
        out.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    out.append(f"--{b}\r\nContent-Disposition: form-data; name=\"chunk_data\"; filename=\"{fname}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode())
    out.append(fdata)
    out.append(f"\r\n--{b}--\r\n".encode())
    return b"".join(out), f"multipart/form-data; boundary={b}"


def main():
    zp = sys.argv[1]
    data = open(zp, "rb").read()
    pw = os.environ.get("KOMARI_PASSWORD") or open(PWF).read()
    req("POST", "/api/login", json.dumps({"username": USER, "password": pw}).encode())
    init = req("POST", "/api/admin/upload/init",
               json.dumps({"purpose": "theme", "size": len(data), "filename": os.path.basename(zp)}).encode())
    uid, cs = init["upload_id"], init["chunk_size"]
    for i in range(0, (len(data) + cs - 1) // cs):
        body, ct = multipart({"upload_id": uid, "chunk_index": str(i)}, "chunk", data[i * cs:(i + 1) * cs])
        req("POST", "/api/admin/upload/chunk", body, ct)
    res = req("POST", "/api/admin/upload/merge", json.dumps({"upload_id": uid}).encode())
    print("uploaded:", json.dumps(res, ensure_ascii=False)[:300])
    if "--no-activate" not in sys.argv:
        short = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "komari-theme.json")))["short"]
        req("GET", f"/api/admin/theme/set?theme={short}")
        print("active theme:", short)


if __name__ == "__main__":
    main()
