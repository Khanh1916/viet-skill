"""Offline tests for every skill. Network calls are replaced by recorded sample data."""

import re
from datetime import date, timedelta
from pathlib import Path

import pytest

import dvhc
import lich_am
import tncn
import ty_gia
import vietqr

ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- SKILL.md format

SKILLS = sorted(p.parent for p in (ROOT / "skills").glob("*/SKILL.md"))


def test_every_skill_folder_has_a_skill_md():
    folders = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    assert folders == SKILLS


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_skill_md_frontmatter(skill):
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "missing YAML frontmatter"
    fields = dict(line.split(": ", 1) for line in m.group(1).splitlines())
    assert fields["name"] == skill.name
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fields["name"])
    assert 50 < len(fields["description"]) <= 1024


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_scripts_mentioned_in_skill_md_exist(skill):
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    for script in re.findall(r"scripts/([\w.]+\.py)", text):
        assert (skill / "scripts" / script).is_file(), script


# ---------------------------------------------------------------- lich-am

@pytest.mark.parametrize("year, tet", [
    (2023, date(2023, 1, 22)), (2024, date(2024, 2, 10)), (2025, date(2025, 1, 29)),
    (2026, date(2026, 2, 17)), (2027, date(2027, 2, 6)),
    (2030, date(2030, 2, 2)),  # Vietnam (UTC+7) celebrates one day before China this year
])
def test_tet_dates(year, tet):
    assert lich_am.lunar_to_solar(1, 1, year) == tet
    assert lich_am.solar_to_lunar(tet) == {"ngay": 1, "thang": 1, "nam": year, "nhuan": False}


def test_leap_month_2025():
    assert lich_am.solar_to_lunar(date(2025, 7, 25)) == {"ngay": 1, "thang": 6, "nam": 2025, "nhuan": True}
    assert lich_am.lunar_to_solar(1, 6, 2025, leap=True) == date(2025, 7, 25)
    with pytest.raises(ValueError):
        lich_am.lunar_to_solar(1, 5, 2025, leap=True)


def test_round_trip_every_day_2020_2032():
    d = date(2020, 1, 1)
    while d < date(2033, 1, 1):
        lunar = lich_am.solar_to_lunar(d)
        assert lich_am.lunar_to_solar(lunar["ngay"], lunar["thang"], lunar["nam"], lunar["nhuan"]) == d
        d += timedelta(days=1)


def test_invalid_lunar_day():
    with pytest.raises(ValueError):
        lich_am.lunar_to_solar(31, 1, 2026)


def test_can_chi():
    assert lich_am.year_can_chi(2026) == "Bính Ngọ"
    assert lich_am.year_can_chi(2024) == "Giáp Thìn"
    assert lich_am.month_can_chi(1, 2026) == "Canh Dần"
    assert lich_am.day_can_chi(date(2000, 1, 1)) == "Mậu Ngọ"  # well-known anchor
    assert lich_am.day_can_chi(date(2026, 2, 17)) == "Nhâm Tuất"


def test_holidays_2026():
    names = {name: d for d, name, _ in lich_am.holidays(2026)}
    assert names["Tết Trung thu"] == date(2026, 9, 25)
    assert names["Giỗ Tổ Hùng Vương"] == date(2026, 4, 26)
    assert names["Giao thừa (ngày cuối năm âm lịch)"] == date(2026, 2, 16)
    assert names["Quốc khánh"] == date(2026, 9, 2)


def test_lich_am_cli(capsys):
    assert lich_am.main(["--json", "duong-sang-am", "25/09/2026"]) == 0
    assert '"Tết Trung thu"' in capsys.readouterr().out
    assert lich_am.main(["am-sang-duong", "31/1/2026"]) == 2


# ---------------------------------------------------------------- thue-tncn

@pytest.mark.parametrize("taxable, tax", [
    (0, 0), (10_000_000, 500_000), (25_000_000, 2_000_000), (30_000_000, 2_500_000),
    (60_000_000, 8_500_000), (100_000_000, 20_500_000), (120_000_000, 27_500_000),
])
def test_progressive_tax(taxable, tax):
    assert round(tncn.thue_luy_tien(taxable)[0]) == tax


def test_gross_with_explicit_insurance():
    r = tncn.tinh_tu_gross(40_000_000, phu_thuoc=1, bao_hiem=4_200_000)
    assert r["thu_nhap_tinh_thue"] == 40_000_000 - 4_200_000 - 15_500_000 - 6_200_000
    assert r["thue_tncn"] == 500_000 + 4_100_000 * 0.10
    assert r["canh_bao"] == []


def test_no_tax_below_deductions():
    r = tncn.tinh_tu_gross(15_000_000)
    assert r["thue_tncn"] == 0 and r["canh_bao"]


@pytest.mark.parametrize("net", [12_000_000, 20_000_000, 55_000_000])
def test_net_to_gross_is_minimal(net):
    r = tncn.tinh_tu_net(net)
    assert r["luong_net"] >= net
    assert tncn.tinh_tu_gross(r["luong_gross"] - 1)["luong_net"] < net


# ---------------------------------------------------------------- vietqr

BANKS = [
    {"code": "VCB", "bin": "970436", "shortName": "Vietcombank", "name": "Ngân hàng TMCP Ngoại Thương Việt Nam"},
    {"code": "MB", "bin": "970422", "shortName": "MBBank", "name": "Ngân hàng TMCP Quân đội"},
    {"code": "ICB", "bin": "970415", "shortName": "VietinBank", "name": "Ngân hàng TMCP Công thương Việt Nam"},
]


def test_remove_accents():
    assert vietqr.bo_dau("Tiền ăn trưa Đà Nẵng") == "Tien an trua Da Nang"


@pytest.mark.parametrize("query, code", [("vcb", "VCB"), ("970422", "MB"), ("ngoại thương", "VCB"), ("vietin", "ICB")])
def test_find_bank(query, code):
    assert [b["code"] for b in vietqr.find_banks(query, BANKS)] == [code]


def test_ambiguous_bank_returns_several():
    assert len(vietqr.find_banks("viet", BANKS)) == 2


def test_build_url():
    url = vietqr.build_url("970436", "0123456789", 150000, "Tiền ăn trưa", "Nguyễn Văn A")
    assert url == ("https://img.vietqr.io/image/970436-0123456789-compact2.png"
                   "?amount=150000&addInfo=Tien+an+trua&accountName=NGUYEN+VAN+A")
    with pytest.raises(ValueError):
        vietqr.build_url("970436", "0123456789", template="nope")


def test_save_image_keeps_svg_with_qr(tmp_path):
    svg = b'<svg xmlns="x"><image href="data:image/png;base64,AAAA"/><path d="M0 0h7v1h-7z"/></svg>'
    out = vietqr.save_image(svg, str(tmp_path / "qr.png"))
    assert out.endswith("qr.svg") and Path(out).read_bytes() == svg


def test_save_image_png_and_garbage(tmp_path):
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 10
    assert vietqr.save_image(png, str(tmp_path / "a.png")).endswith("a.png")
    with pytest.raises(ValueError):
        vietqr.save_image(b"<html>blocked</html>", str(tmp_path / "b.png"))


# ---------------------------------------------------------------- don-vi-hanh-chinh

PROVINCES = [
    {"name": "Thành phố Hà Nội", "code": 1, "codename": "ha_noi", "division_type": "thành phố trung ương", "phone_code": 24},
    {"name": "Tỉnh Thanh Hóa", "code": 38, "codename": "thanh_hoa", "division_type": "tỉnh", "phone_code": 237},
    {"name": "Thành phố Hồ Chí Minh", "code": 79, "codename": "ho_chi_minh", "division_type": "thành phố trung ương", "phone_code": 28},
]
WARDS = [
    {"name": "Xã Ba Đình", "code": 16171, "division_type": "xã", "province_code": 38},
    {"name": "Phường Ba Đình", "code": 4, "division_type": "phường", "province_code": 1},
    {"name": "Phường Sài Gòn", "code": 26734, "division_type": "phường", "province_code": 79},
]


def test_norm():
    assert dvhc.norm("  Đà   Nẵng ") == "da nang"


@pytest.mark.parametrize("query, code", [("hà nội", 1), ("ha noi", 1), ("79", 79), ("hồ chí minh", 79)])
def test_find_province(query, code):
    assert [p["code"] for p in dvhc.find_province(query, PROVINCES)] == [code]


def test_search_wards_accent_insensitive_and_ranked():
    hits = dvhc.search_wards("ba dinh", PROVINCES, WARDS)
    assert [(h["ten"], h["tinh"]) for h in hits] == [("Phường Ba Đình", "Thành phố Hà Nội"),
                                                     ("Xã Ba Đình", "Tỉnh Thanh Hóa")]


# ---------------------------------------------------------------- ty-gia

SAMPLE_XML = """<?xml version="1.0" encoding="utf-8"?><!--For reference only.-->
<ExrateList><DateTime>11/7/2026 6:09:04 PM</DateTime>
<Exrate CurrencyCode="USD" CurrencyName="US DOLLAR           " Buy="25,370.00" Transfer="25,400.00" Sell="25,780.00" />
<Exrate CurrencyCode="KWD" CurrencyName="KUWAITI DINAR       " Buy="-" Transfer="82,000.00" Sell="85,000.00" />
<Source>Joint Stock Commercial Bank for Foreign Trade of Vietnam - Vietcombank</Source></ExrateList>"""


def test_parse_rates():
    data = ty_gia.parse(SAMPLE_XML.encode())
    assert data["thoi_diem"] == "11/7/2026 6:09:04 PM"
    assert data["ty_gia"]["USD"] == {"ten": "US DOLLAR", "mua_tien_mat": 25370.0,
                                     "mua_chuyen_khoan": 25400.0, "ban": 25780.0}
    assert data["ty_gia"]["KWD"]["mua_tien_mat"] is None


def test_convert_both_directions():
    data = ty_gia.parse(SAMPLE_XML.encode())
    assert ty_gia.convert(100, "usd", "VND", data)["ket_qua"] == 2_540_000
    assert ty_gia.convert(2_578_000, "VND", "USD", data)["ket_qua"] == 100.0
    with pytest.raises(ValueError):
        ty_gia.convert(1, "USD", "KWD", data)
