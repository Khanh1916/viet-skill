"""Tỷ giá ngoại tệ của Vietcombank (mua tiền mặt, mua chuyển khoản, bán) và quy đổi sang VND.

Nguồn: bảng tỷ giá XML công khai của Vietcombank. Vietcombank yêu cầu tối đa 1 lần gọi mỗi
5 phút, nên kết quả được cache 5 phút.

Ví dụ:
  python ty_gia.py                     # toàn bộ bảng tỷ giá
  python ty_gia.py USD JPY
  python ty_gia.py doi 100 USD         # 100 USD bằng bao nhiêu VND (theo giá mua chuyển khoản)
  python ty_gia.py doi 5000000 VND JPY # 5 triệu VND đổi được bao nhiêu JPY (theo giá bán)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import urllib.request
import xml.etree.ElementTree as ET

URL = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx"
UA = {"User-Agent": "viet-skill/0.1 (+https://github.com/Khanh1916/viet-skill)"}
CACHE = os.path.join(tempfile.gettempdir(), "viet-skill-tygia-vcb.xml")
MIN_INTERVAL = 300


def num(text: str | None) -> float | None:
    text = (text or "").strip().replace(",", "")
    if not text or text == "-":
        return None
    return float(text)


def parse(xml_bytes: bytes) -> dict:
    root = ET.fromstring(xml_bytes)
    rates = {}
    for e in root.iter("Exrate"):
        code = e.get("CurrencyCode", "").strip()
        rates[code] = {
            "ten": e.get("CurrencyName", "").strip(),
            "mua_tien_mat": num(e.get("Buy")),
            "mua_chuyen_khoan": num(e.get("Transfer")),
            "ban": num(e.get("Sell")),
        }
    when = (root.findtext("DateTime") or "").strip()
    return {"nguon": "Vietcombank", "thoi_diem": when, "ty_gia": rates}


def fetch() -> bytes:
    try:
        if time.time() - os.path.getmtime(CACHE) < MIN_INTERVAL:
            with open(CACHE, "rb") as f:
                return f.read()
    except OSError:
        pass
    with urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=20) as r:
        data = r.read()
    try:
        with open(CACHE, "wb") as f:
            f.write(data)
    except OSError:
        pass
    return data


def convert(amount: float, src: str, dst: str, data: dict) -> dict:
    rates = data["ty_gia"]
    src, dst = src.upper(), dst.upper()
    if src == dst:
        raise ValueError("hai loại tiền giống nhau")
    if src != "VND" and dst != "VND":
        raise ValueError("chỉ hỗ trợ đổi giữa VND và một ngoại tệ")
    if src != "VND":
        r = rates.get(src)
        if not r or r["mua_chuyen_khoan"] is None:
            raise ValueError(f"không có tỷ giá mua chuyển khoản cho {src}")
        return {"so_tien": amount, "tu": src, "sang": "VND", "ket_qua": round(amount * r["mua_chuyen_khoan"]),
                "ty_gia_ap_dung": r["mua_chuyen_khoan"], "loai_gia": "Vietcombank mua chuyển khoản"}
    r = rates.get(dst)
    if not r or r["ban"] is None:
        raise ValueError(f"không có tỷ giá bán cho {dst}")
    return {"so_tien": amount, "tu": "VND", "sang": dst, "ket_qua": round(amount / r["ban"], 2),
            "ty_gia_ap_dung": r["ban"], "loai_gia": "Vietcombank bán ra"}


def fmt(x: float | None) -> str:
    return "-" if x is None else f"{x:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    try:
        data = parse(fetch())
    except (OSError, ET.ParseError) as exc:
        print(f"Lỗi: không lấy được tỷ giá Vietcombank ({exc})", file=sys.stderr)
        return 1

    if argv and argv[0] == "doi":
        p = argparse.ArgumentParser(prog="ty_gia.py doi")
        p.add_argument("so_tien", type=float)
        p.add_argument("tu")
        p.add_argument("sang", nargs="?", default="VND")
        a = p.parse_args(argv[1:])
        try:
            result = convert(a.so_tien, a.tu, a.sang, data)
        except ValueError as exc:
            print(f"Lỗi: {exc}", file=sys.stderr)
            return 2
        result["thoi_diem"] = data["thoi_diem"]
        if as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"{fmt(result['so_tien'])} {result['tu']} = {fmt(result['ket_qua'])} {result['sang']}")
            print(f"Tỷ giá: {fmt(result['ty_gia_ap_dung'])} ({result['loai_gia']}, {data['thoi_diem']})")
        return 0

    codes = [c.upper() for c in argv]
    rows = {c: v for c, v in data["ty_gia"].items() if not codes or c in codes}
    missing = [c for c in codes if c not in rows]
    if as_json:
        print(json.dumps({**data, "ty_gia": rows}, ensure_ascii=False, indent=2))
    else:
        print(f"Tỷ giá Vietcombank lúc {data['thoi_diem']} (VND)")
        print(f"{'Mã':<5}{'Mua tiền mặt':>16}{'Mua chuyển khoản':>20}{'Bán':>16}")
        for c, v in rows.items():
            print(f"{c:<5}{fmt(v['mua_tien_mat']):>16}{fmt(v['mua_chuyen_khoan']):>20}{fmt(v['ban']):>16}")
    if missing:
        print(f"Không có tỷ giá cho: {', '.join(missing)}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
