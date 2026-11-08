"""Offline tests for every skill. Network calls are replaced by recorded sample data."""

import re
from datetime import date, timedelta
from pathlib import Path

import pytest

import lich_am

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
    (2007, date(2007, 2, 17)),  # Vietnam (UTC+7) celebrated one day before China
    (2030, date(2030, 2, 2)),   # and will again in 2030
])
def test_tet_dates(year, tet):
    assert lich_am.lunar_to_solar(1, 1, year) == tet
    assert lich_am.solar_to_lunar(tet) == {"ngay": 1, "thang": 1, "nam": year, "nhuan": False}


@pytest.mark.parametrize("year, china", [(2007, date(2007, 2, 18)), (2030, date(2030, 2, 3))])
def test_china_timezone_gives_a_different_tet(monkeypatch, year, china):
    monkeypatch.setattr(lich_am, "TZ", 8.0)
    assert lich_am.lunar_to_solar(1, 1, year) == china


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
