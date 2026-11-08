"""Lịch âm Việt Nam: đổi ngày dương <-> âm, can chi, ngày lễ. Chạy offline, không cần thư viện.

Thuật toán thiên văn của Hồ Ngọc Đức (dựa trên Jean Meeus), múi giờ +7.

Ví dụ:
  python lich_am.py                      # hôm nay
  python lich_am.py duong-sang-am 2026-02-17
  python lich_am.py am-sang-duong 1/1/2027        # mùng 1 Tết năm 2027
  python lich_am.py am-sang-duong 1/6/2025 --nhuan
  python lich_am.py tet 2027
  python lich_am.py ngay-le 2026
  python lich_am.py --json duong-sang-am 2026-09-25
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, timedelta

TZ = 7.0
CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
THU = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]


# ---------------------------------------------------------------- astronomy

def jd_from_date(dd: int, mm: int, yy: int) -> int:
    a = (14 - mm) // 12
    y = yy + 4800 - a
    m = mm + 12 * a - 3
    jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    if jd < 2299161:
        jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
    return jd


def jd_to_date(jd: int) -> tuple[int, int, int]:
    if jd > 2299160:
        a = jd + 32044
        b = (4 * a + 3) // 146097
        c = a - (b * 146097) // 4
    else:
        b = 0
        c = jd + 32082
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = b * 100 + d - 4800 + m // 10
    return day, month, year


def new_moon(k: int) -> float:
    t = k / 1236.85
    t2, t3 = t * t, t * t * t
    dr = math.pi / 180
    jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * t2 - 0.000000155 * t3
    jd1 += 0.00033 * math.sin((166.56 + 132.87 * t - 0.009173 * t2) * dr)
    m = 359.2242 + 29.10535608 * k - 0.0000333 * t2 - 0.00000347 * t3
    mpr = 306.0253 + 385.81691806 * k + 0.0107306 * t2 + 0.00001236 * t3
    f = 21.2964 + 390.67050646 * k - 0.0016528 * t2 - 0.00000239 * t3
    c1 = (0.1734 - 0.000393 * t) * math.sin(m * dr) + 0.0021 * math.sin(2 * dr * m)
    c1 = c1 - 0.4068 * math.sin(mpr * dr) + 0.0161 * math.sin(dr * 2 * mpr)
    c1 = c1 - 0.0004 * math.sin(dr * 3 * mpr)
    c1 = c1 + 0.0104 * math.sin(dr * 2 * f) - 0.0051 * math.sin(dr * (m + mpr))
    c1 = c1 - 0.0074 * math.sin(dr * (m - mpr)) + 0.0004 * math.sin(dr * (2 * f + m))
    c1 = c1 - 0.0004 * math.sin(dr * (2 * f - m)) - 0.0006 * math.sin(dr * (2 * f + mpr))
    c1 = c1 + 0.0010 * math.sin(dr * (2 * f - mpr)) + 0.0005 * math.sin(dr * (2 * mpr + m))
    if t < -11:
        deltat = 0.001 + 0.000839 * t + 0.0002261 * t2 - 0.00000845 * t3 - 0.000000081 * t * t3
    else:
        deltat = -0.000278 + 0.000265 * t + 0.000262 * t2
    return jd1 + c1 - deltat


def sun_longitude(jdn: float) -> float:
    t = (jdn - 2451545.0) / 36525
    t2 = t * t
    dr = math.pi / 180
    m = 357.52910 + 35999.05030 * t - 0.0001559 * t2 - 0.00000048 * t * t2
    l0 = 280.46645 + 36000.76983 * t + 0.0003032 * t2
    dl = (1.914600 - 0.004817 * t - 0.000014 * t2) * math.sin(dr * m)
    dl += (0.019993 - 0.000101 * t) * math.sin(dr * 2 * m) + 0.000290 * math.sin(dr * 3 * m)
    lon = (l0 + dl) * dr
    lon = lon - math.pi * 2 * int(lon / (math.pi * 2))
    if lon < 0:
        lon += 2 * math.pi
    return lon


def new_moon_day(k: int) -> int:
    return int(new_moon(k) + 0.5 + TZ / 24)


def sun_longitude_sector(day_number: int) -> int:
    return int(sun_longitude(day_number - 0.5 - TZ / 24) / math.pi * 6)


def lunar_month_11(yy: int) -> int:
    off = jd_from_date(31, 12, yy) - 2415021
    k = int(off / 29.530588853)
    nm = new_moon_day(k)
    if sun_longitude_sector(nm) >= 9:
        nm = new_moon_day(k - 1)
    return nm


def leap_month_offset(a11: int) -> int:
    k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    i = 1
    arc = sun_longitude_sector(new_moon_day(k + i))
    while True:
        last = arc
        i += 1
        arc = sun_longitude_sector(new_moon_day(k + i))
        if arc == last or i >= 14:
            break
    return i - 1


# ---------------------------------------------------------------- conversions

def solar_to_lunar(d: date) -> dict:
    day_number = jd_from_date(d.day, d.month, d.year)
    k = int((day_number - 2415021.076998695) / 29.530588853)
    month_start = new_moon_day(k + 1)
    if month_start > day_number:
        month_start = new_moon_day(k)
    a11 = lunar_month_11(d.year)
    b11 = a11
    if a11 >= month_start:
        lunar_year = d.year
        a11 = lunar_month_11(d.year - 1)
    else:
        lunar_year = d.year + 1
        b11 = lunar_month_11(d.year + 1)
    lunar_day = day_number - month_start + 1
    diff = (month_start - a11) // 29
    leap = False
    lunar_month = diff + 11
    if b11 - a11 > 365:
        leap_diff = leap_month_offset(a11)
        if diff >= leap_diff:
            lunar_month = diff + 10
            if diff == leap_diff:
                leap = True
    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1
    return {"ngay": lunar_day, "thang": lunar_month, "nam": lunar_year, "nhuan": leap}


def lunar_to_solar(lunar_day: int, lunar_month: int, lunar_year: int, leap: bool = False) -> date:
    if lunar_month < 11:
        a11 = lunar_month_11(lunar_year - 1)
        b11 = lunar_month_11(lunar_year)
    else:
        a11 = lunar_month_11(lunar_year)
        b11 = lunar_month_11(lunar_year + 1)
    k = int(0.5 + (a11 - 2415021.076998695) / 29.530588853)
    off = lunar_month - 11
    if off < 0:
        off += 12
    if b11 - a11 > 365:
        leap_off = leap_month_offset(a11)
        leap_month = leap_off - 2
        if leap_month < 0:
            leap_month += 12
        if leap and lunar_month != leap_month:
            raise ValueError(f"năm âm {lunar_year} không có tháng {lunar_month} nhuận")
        if leap or off >= leap_off:
            off += 1
    elif leap:
        raise ValueError(f"năm âm {lunar_year} không có tháng nhuận")
    month_start = new_moon_day(k + off)
    dd, mm, yy = jd_to_date(month_start + lunar_day - 1)
    result = date(yy, mm, dd)
    check = solar_to_lunar(result)
    if (check["ngay"], check["thang"], check["nam"]) != (lunar_day, lunar_month, lunar_year):
        raise ValueError(f"tháng {lunar_month} năm âm {lunar_year} không có ngày {lunar_day}")
    return result


# ---------------------------------------------------------------- can chi

def year_can_chi(lunar_year: int) -> str:
    return f"{CAN[(lunar_year + 6) % 10]} {CHI[(lunar_year + 8) % 12]}"


def month_can_chi(lunar_month: int, lunar_year: int) -> str:
    return f"{CAN[(lunar_year * 12 + lunar_month + 3) % 10]} {CHI[(lunar_month + 1) % 12]}"


def day_can_chi(d: date) -> str:
    jd = jd_from_date(d.day, d.month, d.year)
    return f"{CAN[(jd + 9) % 10]} {CHI[(jd + 1) % 12]}"


def describe(d: date) -> dict:
    lunar = solar_to_lunar(d)
    return {
        "duong_lich": d.isoformat(),
        "thu": THU[d.weekday()],
        "am_lich": f"{lunar['ngay']:02d}/{lunar['thang']:02d}{' (nhuận)' if lunar['nhuan'] else ''}/{lunar['nam']}",
        "ngay_am": lunar["ngay"], "thang_am": lunar["thang"], "nam_am": lunar["nam"], "thang_nhuan": lunar["nhuan"],
        "can_chi_ngay": day_can_chi(d),
        "can_chi_thang": month_can_chi(lunar["thang"], lunar["nam"]),
        "can_chi_nam": year_can_chi(lunar["nam"]),
        "le": [name for when, name, _ in holidays(d.year) if when == d],
    }


# ---------------------------------------------------------------- holidays

def holidays(year: int) -> list[tuple[date, str, str]]:
    """Ngày lễ và ngày truyền thống trong năm dương lịch ``year``.

    Loại "nghi" là ngày lễ được nghỉ theo Điều 112 Bộ luật Lao động 2019; số ngày nghỉ thực tế
    (nghỉ bù, hoán đổi) do Chính phủ công bố từng năm. Loại "truyen-thong" là ngày truyền thống,
    không phải ngày nghỉ.
    """
    out: list[tuple[date, str, str]] = [
        (date(year, 1, 1), "Tết Dương lịch", "nghi"),
        (date(year, 4, 30), "Ngày Chiến thắng (30/4)", "nghi"),
        (date(year, 5, 1), "Ngày Quốc tế Lao động", "nghi"),
        (date(year, 9, 2), "Quốc khánh", "nghi"),
    ]
    lunar_fixed = [
        (1, 1, "Tết Nguyên Đán (mùng 1)", "nghi"),
        (2, 1, "Tết Nguyên Đán (mùng 2)", "nghi"),
        (3, 1, "Tết Nguyên Đán (mùng 3)", "nghi"),
        (15, 1, "Rằm tháng Giêng (Tết Nguyên Tiêu)", "truyen-thong"),
        (10, 3, "Giỗ Tổ Hùng Vương", "nghi"),
        (5, 5, "Tết Đoan Ngọ", "truyen-thong"),
        (15, 7, "Lễ Vu Lan (Rằm tháng Bảy)", "truyen-thong"),
        (15, 8, "Tết Trung thu", "truyen-thong"),
        (23, 12, "Ông Công Ông Táo", "truyen-thong"),
    ]
    for lunar_year in (year - 1, year):
        for dd, mm, name, kind in lunar_fixed:
            try:
                d = lunar_to_solar(dd, mm, lunar_year)
            except ValueError:
                continue
            if d.year == year:
                out.append((d, name, kind))
        tet_next = lunar_to_solar(1, 1, lunar_year + 1)
        eve = tet_next - timedelta(days=1)
        if eve.year == year:
            out.append((eve, "Giao thừa (ngày cuối năm âm lịch)", "nghi"))
    return sorted(out)


# ---------------------------------------------------------------- CLI

def parse_solar(text: str) -> date:
    text = text.strip()
    if "-" in text:
        return date.fromisoformat(text)
    dd, mm, yy = (int(x) for x in text.split("/"))
    return date(yy, mm, dd)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Lịch âm Việt Nam (offline)")
    p.add_argument("--json", action="store_true", help="in kết quả dạng JSON")
    sub = p.add_subparsers(dest="cmd")
    s1 = sub.add_parser("duong-sang-am", help="đổi ngày dương lịch sang âm lịch")
    s1.add_argument("ngay", help="YYYY-MM-DD hoặc DD/MM/YYYY")
    s2 = sub.add_parser("am-sang-duong", help="đổi ngày âm lịch sang dương lịch")
    s2.add_argument("ngay", help="DD/MM/YYYY (năm âm lịch)")
    s2.add_argument("--nhuan", action="store_true", help="tháng nhuận")
    s3 = sub.add_parser("tet", help="ngày Tết Nguyên Đán và số ngày còn lại")
    s3.add_argument("nam", type=int, nargs="?", help="năm âm lịch (mặc định: Tết sắp tới)")
    s4 = sub.add_parser("ngay-le", help="ngày lễ trong năm dương lịch")
    s4.add_argument("nam", type=int, nargs="?", default=date.today().year)
    args = p.parse_args(argv)

    try:
        if args.cmd in (None, "duong-sang-am"):
            d = parse_solar(args.ngay) if args.cmd else date.today()
            result = describe(d)
        elif args.cmd == "am-sang-duong":
            dd, mm, yy = (int(x) for x in args.ngay.split("/"))
            result = describe(lunar_to_solar(dd, mm, yy, args.nhuan))
        elif args.cmd == "tet":
            today = date.today()
            year = args.nam
            if year is None:
                year = solar_to_lunar(today)["nam"] + 1
            tet = lunar_to_solar(1, 1, year)
            result = {"nam_am": year, "can_chi": year_can_chi(year), "mung_1": tet.isoformat(),
                      "thu": THU[tet.weekday()], "con_lai_ngay": (tet - today).days}
        else:
            result = [{"ngay": d.isoformat(), "thu": THU[d.weekday()], "ten": name,
                       "loai": "ngày nghỉ lễ" if kind == "nghi" else "ngày truyền thống"}
                      for d, name, kind in holidays(args.nam)]
    except ValueError as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif isinstance(result, list):
        for r in result:
            print(f"{r['ngay']}  {r['thu']:<9} {r['ten']}  ({r['loai']})")
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
