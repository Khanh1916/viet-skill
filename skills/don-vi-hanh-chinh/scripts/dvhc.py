"""Tra cứu đơn vị hành chính Việt Nam sau sắp xếp 2025: 34 tỉnh/thành, chính quyền 2 cấp (tỉnh - xã).

Dữ liệu từ API công khai provinces.open-api.vn (phiên bản v2, mã nguồn mở:
https://github.com/hongquan/vn-open-api-provinces). Kết quả được cache 1 ngày.

Ví dụ:
  python dvhc.py tinh                      # 34 tỉnh/thành
  python dvhc.py tim "ba đình"             # tìm xã/phường theo tên
  python dvhc.py xa "hà nội"               # các xã/phường của một tỉnh (tên hoặc mã)
  python dvhc.py --json tim "an khanh"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
import unicodedata
import urllib.parse
import urllib.request

BASE = "https://provinces.open-api.vn/api/v2"
UA = {"User-Agent": "viet-skill/0.1 (+https://github.com/Khanh1916/viet-skill)"}
CACHE_DIR = os.path.join(tempfile.gettempdir(), "viet-skill-dvhc")


def norm(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    text = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    return " ".join(text.lower().split())


def get(path: str, params: dict | None = None, max_age: int = 86400):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache = os.path.join(CACHE_DIR, hashlib.sha1(url.encode()).hexdigest() + ".json")
    try:
        if time.time() - os.path.getmtime(cache) < max_age:
            with open(cache, encoding="utf-8") as f:
                return json.load(f)
    except OSError:
        pass
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        data = json.load(r)
    try:
        with open(cache, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError:
        pass
    return data


def provinces() -> list[dict]:
    return get("/p/")


def find_province(query: str, items: list[dict]) -> list[dict]:
    if query.strip().isdigit():
        return [p for p in items if p["code"] == int(query)]
    q = norm(query)
    exact = [p for p in items if norm(p["name"]) == q or p["codename"].replace("_", " ") == q]
    if exact:
        return exact
    return [p for p in items if q in norm(p["name"])]


def search_wards(query: str, items: list[dict], wards: list[dict]) -> list[dict]:
    q = norm(query)
    by_code = {p["code"]: p["name"] for p in items}
    hits = [w for w in wards if q in norm(w["name"])]
    # exact name matches (ignoring "Phường"/"Xã" prefix) first
    hits.sort(key=lambda w: (norm(w["name"]).split(" ", 1)[-1] != q, w["province_code"], w["name"]))
    return [{"ten": w["name"], "ma": w["code"], "loai": w["division_type"],
             "tinh": by_code.get(w["province_code"], "?"), "ma_tinh": w["province_code"]} for w in hits]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Tra cứu đơn vị hành chính Việt Nam (34 tỉnh, 2 cấp)")
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("tinh", help="danh sách 34 tỉnh/thành phố")
    s2 = sub.add_parser("tim", help="tìm xã/phường/đặc khu theo tên (có dấu hoặc không dấu)")
    s2.add_argument("ten")
    s3 = sub.add_parser("xa", help="các xã/phường của một tỉnh")
    s3.add_argument("tinh", help="tên hoặc mã tỉnh")
    args = p.parse_args(argv)

    try:
        items = provinces()
        if args.cmd == "tinh":
            result = [{"ma": x["code"], "ten": x["name"], "loai": x["division_type"], "ma_dien_thoai": x["phone_code"]}
                      for x in items]
        elif args.cmd == "tim":
            result = search_wards(args.ten, items, get("/w/", {"search": args.ten}))
            if not result:  # the API search is accent-sensitive; fall back to a full scan
                all_wards = [w for x in items for w in get(f"/p/{x['code']}", {"depth": 2})["wards"]]
                result = search_wards(args.ten, items, all_wards)
        else:
            found = find_province(args.tinh, items)
            if len(found) != 1:
                names = ", ".join(x["name"] for x in found) or "không có"
                print(f"Lỗi: cần đúng 1 tỉnh, tìm thấy {len(found)} ({names})", file=sys.stderr)
                return 2
            detail = get(f"/p/{found[0]['code']}", {"depth": 2})
            result = {"tinh": detail["name"], "ma": detail["code"], "so_xa_phuong": len(detail["wards"]),
                      "xa_phuong": [{"ten": w["name"], "ma": w["code"]} for w in detail["wards"]]}
    except OSError as exc:
        print(f"Lỗi: không kết nối được provinces.open-api.vn ({exc})", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cmd == "tinh":
        for x in result:
            print(f"{x['ma']:>3}  {x['ten']}")
        print(f"Tổng: {len(result)} tỉnh/thành phố")
    elif args.cmd == "tim":
        for x in result[:50]:
            print(f"{x['ten']} ({x['loai']}), {x['tinh']}  [mã {x['ma']}]")
        print(f"Tìm thấy {len(result)} kết quả" + (" (hiện 50 đầu tiên)" if len(result) > 50 else ""))
    else:
        print(f"{result['tinh']} có {result['so_xa_phuong']} xã/phường/đặc khu:")
        print(", ".join(w["ten"] for w in result["xa_phuong"]))
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
