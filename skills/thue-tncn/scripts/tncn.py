"""Tính thuế thu nhập cá nhân từ tiền lương, tiền công (cá nhân cư trú) theo quy định năm 2026.

- Biểu thuế lũy tiến 5 bậc: Điều 9 Luật Thuế thu nhập cá nhân số 109/2025/QH15.
- Giảm trừ gia cảnh: 15,5 triệu/tháng cho bản thân, 6,2 triệu/tháng cho mỗi người phụ thuộc
  (Nghị quyết 110/2025/UBTVQH15, áp dụng từ kỳ tính thuế năm 2026).

Ví dụ:
  python tncn.py gross 30000000 --phu-thuoc 1
  python tncn.py gross 60000000 --bao-hiem 4914000
  python tncn.py net 20000000                # lương NET 20 triệu thì GROSS bao nhiêu?
  python tncn.py --json gross 25000000
"""

from __future__ import annotations

import argparse
import json
import sys

GIAM_TRU_BAN_THAN = 15_500_000
GIAM_TRU_PHU_THUOC = 6_200_000
# (ngưỡng trên của bậc, thuế suất) - thu nhập tính thuế theo tháng
BIEU_THUE = [
    (10_000_000, 0.05),
    (30_000_000, 0.10),
    (60_000_000, 0.20),
    (100_000_000, 0.30),
    (None, 0.35),
]
TY_LE_BAO_HIEM_NLD = 0.105  # BHXH 8% + BHYT 1.5% + BHTN 1% (phần người lao động đóng)


def thue_luy_tien(thu_nhap_tinh_thue: float) -> tuple[float, list[dict]]:
    """Thuế phải nộp theo biểu lũy tiến từng phần, kèm chi tiết từng bậc."""
    con_lai = max(thu_nhap_tinh_thue, 0)
    duoi = 0
    tong = 0.0
    chi_tiet = []
    for bac, (tren, suat) in enumerate(BIEU_THUE, start=1):
        if con_lai <= 0:
            break
        rong = (tren - duoi) if tren is not None else con_lai
        phan = min(con_lai, rong)
        thue = phan * suat
        chi_tiet.append({"bac": bac, "thu_nhap_trong_bac": round(phan), "thue_suat": f"{suat:.0%}", "thue": round(thue)})
        tong += thue
        con_lai -= phan
        duoi = tren if tren is not None else duoi
    return tong, chi_tiet


def tinh_tu_gross(gross: float, phu_thuoc: int = 0, bao_hiem: float | None = None) -> dict:
    canh_bao = []
    if bao_hiem is None:
        bao_hiem = gross * TY_LE_BAO_HIEM_NLD
        canh_bao.append("Bảo hiểm ước tính 10,5% lương gross, chưa áp mức trần đóng bảo hiểm và có thể "
                        "khác với lương đóng bảo hiểm thực tế. Dùng --bao-hiem để nhập số chính xác.")
    giam_tru = GIAM_TRU_BAN_THAN + GIAM_TRU_PHU_THUOC * phu_thuoc
    tinh_thue = max(gross - bao_hiem - giam_tru, 0)
    thue, chi_tiet = thue_luy_tien(tinh_thue)
    return {
        "luong_gross": round(gross),
        "bao_hiem_nguoi_lao_dong": round(bao_hiem),
        "giam_tru_gia_canh": giam_tru,
        "so_nguoi_phu_thuoc": phu_thuoc,
        "thu_nhap_tinh_thue": round(tinh_thue),
        "thue_tncn": round(thue),
        "luong_net": round(gross - bao_hiem - thue),
        "chi_tiet_bac": chi_tiet,
        "canh_bao": canh_bao,
    }


def tinh_tu_net(net: float, phu_thuoc: int = 0) -> dict:
    """Tìm lương gross cho ra lương net mong muốn (bảo hiểm ước tính 10,5%)."""
    lo, hi = int(net), int(net * 3) + 50_000_000
    while lo < hi:  # smallest whole-dong gross whose net reaches the target
        mid = (lo + hi) // 2
        if tinh_tu_gross(mid, phu_thuoc)["luong_net"] < net:
            lo = mid + 1
        else:
            hi = mid
    result = tinh_tu_gross(lo, phu_thuoc)
    result["luong_net_mong_muon"] = round(net)
    return result


def vnd(x: float) -> str:
    return f"{round(x):,}".replace(",", ".") + " đ"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Tính thuế TNCN từ tiền lương (2026)")
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gross", help="từ lương gross tính thuế và lương net")
    g.add_argument("so_tien", type=float)
    g.add_argument("--phu-thuoc", type=int, default=0, help="số người phụ thuộc đã đăng ký")
    g.add_argument("--bao-hiem", type=float, help="tiền bảo hiểm bắt buộc người lao động đóng mỗi tháng")
    n = sub.add_parser("net", help="từ lương net mong muốn tìm lương gross")
    n.add_argument("so_tien", type=float)
    n.add_argument("--phu-thuoc", type=int, default=0)
    args = p.parse_args(argv)
    if args.so_tien < 0 or args.phu_thuoc < 0:
        print("Lỗi: số tiền và số người phụ thuộc không được âm", file=sys.stderr)
        return 2

    r = (tinh_tu_gross(args.so_tien, args.phu_thuoc, args.bao_hiem) if args.cmd == "gross"
         else tinh_tu_net(args.so_tien, args.phu_thuoc))
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    print(f"Lương gross:          {vnd(r['luong_gross'])}")
    print(f"Bảo hiểm (NLĐ đóng):  {vnd(r['bao_hiem_nguoi_lao_dong'])}")
    print(f"Giảm trừ gia cảnh:    {vnd(r['giam_tru_gia_canh'])} ({r['so_nguoi_phu_thuoc']} người phụ thuộc)")
    print(f"Thu nhập tính thuế:   {vnd(r['thu_nhap_tinh_thue'])}")
    for b in r["chi_tiet_bac"]:
        print(f"  Bậc {b['bac']} ({b['thue_suat']}): {vnd(b['thu_nhap_trong_bac'])} -> {vnd(b['thue'])}")
    print(f"Thuế TNCN:            {vnd(r['thue_tncn'])}")
    print(f"Lương net:            {vnd(r['luong_net'])}")
    for c in r["canh_bao"]:
        print(f"Lưu ý: {c}")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
