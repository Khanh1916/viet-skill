"""Tạo mã QR chuyển khoản ngân hàng chuẩn VietQR (NAPAS) qua dịch vụ công khai img.vietqr.io.

Ví dụ:
  python vietqr.py ngan-hang vietcombank              # tìm mã ngân hàng
  python vietqr.py tao --ngan-hang VCB --stk 0123456789 --so-tien 150000 --noi-dung "Tien an trua"
  python vietqr.py tao --ngan-hang mbbank --stk 0987654321 --ten "NGUYEN VAN A" --luu qr.png
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import unicodedata
import urllib.parse
import urllib.request

BANKS_URL = "https://api.vietqr.io/v2/banks"
IMAGE_URL = "https://img.vietqr.io/image/{bank}-{account}-{template}.png"
TEMPLATES = ("compact2", "compact", "qr_only", "print")
CACHE = os.path.join(tempfile.gettempdir(), "viet-skill-vietqr-banks.json")
UA = {"User-Agent": "viet-skill/0.1 (+https://github.com/Khanh1916/viet-skill)"}


def bo_dau(text: str) -> str:
    """Bỏ dấu tiếng Việt (VietQR chỉ nhận ký tự không dấu trong nội dung và tên)."""
    text = text.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def load_banks(max_age: int = 7 * 86400) -> list[dict]:
    try:
        if time.time() - os.path.getmtime(CACHE) < max_age:
            with open(CACHE, encoding="utf-8") as f:
                return json.load(f)
    except OSError:
        pass
    req = urllib.request.Request(BANKS_URL, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)["data"]
    try:
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError:
        pass
    return data


def find_banks(query: str, banks: list[dict]) -> list[dict]:
    q = bo_dau(query).lower().replace(" ", "")
    exact, partial = [], []
    for b in banks:
        keys = [b.get("code", ""), b.get("bin", ""), b.get("shortName", ""), b.get("name", "")]
        norm = [bo_dau(k).lower().replace(" ", "") for k in keys]
        if q in norm[:3]:
            exact.append(b)
        elif any(q in k for k in norm):
            partial.append(b)
    return exact or partial


def build_url(bank_bin: str, account: str, amount: int | None = None, note: str = "",
              name: str = "", template: str = "compact2") -> str:
    if not account.isdigit() and not account.replace("-", "").isalnum():
        raise ValueError("số tài khoản không hợp lệ")
    if template not in TEMPLATES:
        raise ValueError(f"template phải là một trong {TEMPLATES}")
    params = {}
    if amount:
        if amount < 0:
            raise ValueError("số tiền không được âm")
        params["amount"] = str(int(amount))
    if note:
        params["addInfo"] = bo_dau(note)[:50]
    if name:
        params["accountName"] = bo_dau(name).upper()
    url = IMAGE_URL.format(bank=bank_bin, account=account, template=template)
    return url + ("?" + urllib.parse.urlencode(params) if params else "")


def save_image(data: bytes, path: str) -> str:
    """Save the QR image and return the path actually written.

    img.vietqr.io may answer a ``.png`` URL with an SVG. The QR modules are SVG paths drawn
    over an embedded PNG *frame*, so the embedded PNG alone has no QR code in it: never
    extract it. Keep the SVG and give it the right extension instead.
    """
    if data.startswith(b"\x89PNG"):
        out = path
    elif data.lstrip()[:5] in (b"<svg ", b"<?xml") and b"<path" in data:
        root, ext = os.path.splitext(path)
        out = root + ".svg" if ext.lower() in (".png", ".jpg", ".jpeg", "") else path
    else:
        raise ValueError("dịch vụ VietQR không trả về ảnh QR hợp lệ")
    with open(out, "wb") as f:
        f.write(data)
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Tạo mã QR chuyển khoản VietQR")
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("ngan-hang", help="tìm ngân hàng theo tên hoặc mã")
    s1.add_argument("ten")
    s2 = sub.add_parser("tao", help="tạo link ảnh QR chuyển khoản")
    s2.add_argument("--ngan-hang", required=True, help="tên, mã (VCB, MB...) hoặc BIN ngân hàng")
    s2.add_argument("--stk", required=True, help="số tài khoản nhận")
    s2.add_argument("--so-tien", type=int, help="số tiền (VND)")
    s2.add_argument("--noi-dung", default="", help="nội dung chuyển khoản (tự bỏ dấu)")
    s2.add_argument("--ten", default="", help="tên chủ tài khoản (tự bỏ dấu, in hoa)")
    s2.add_argument("--mau", default="compact2", choices=TEMPLATES, help="kiểu ảnh")
    s2.add_argument("--luu", help="tải ảnh PNG về đường dẫn này")
    args = p.parse_args(argv)

    try:
        banks = load_banks()
    except OSError as exc:
        print(f"Lỗi: không tải được danh sách ngân hàng ({exc})", file=sys.stderr)
        return 1

    if args.cmd == "ngan-hang":
        found = find_banks(args.ten, banks)
        rows = [{"ma": b["code"], "bin": b["bin"], "ten_ngan": b["shortName"], "ten_day_du": b["name"]} for b in found]
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            for r in rows or [{"ma": "-", "bin": "-", "ten_ngan": "không tìm thấy", "ten_day_du": ""}]:
                print(f"{r['ma']:<10} {r['bin']:<8} {r['ten_ngan']:<16} {r['ten_day_du']}")
        return 0 if rows else 1

    found = find_banks(args.ngan_hang, banks)
    if len(found) != 1:
        names = ", ".join(b["shortName"] for b in found[:8]) or "không có"
        print(f"Lỗi: cần đúng 1 ngân hàng, tìm thấy {len(found)} ({names}). Hãy ghi rõ hơn.", file=sys.stderr)
        return 2
    bank = found[0]
    try:
        url = build_url(bank["bin"], args.stk, args.so_tien, args.noi_dung, args.ten, args.mau)
    except ValueError as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2
    result = {"ngan_hang": bank["shortName"], "bin": bank["bin"], "so_tai_khoan": args.stk,
              "so_tien": args.so_tien, "noi_dung": bo_dau(args.noi_dung)[:50], "anh_qr": url}
    if args.luu:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        try:
            result["da_luu"] = os.path.abspath(save_image(data, args.luu))
        except ValueError as exc:
            print(f"Lỗi: {exc}", file=sys.stderr)
            return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
