# viet-skill 🇻🇳

**Bộ skill giúp AI agent hiểu và làm được việc ở Việt Nam.** Lịch âm, thuế TNCN 2026, mã QR
chuyển khoản, 34 tỉnh thành mới, tỷ giá, văn bản hành chính chuẩn Nghị định 30. Dùng được với
Claude Code, Codex, Cursor, Gemini CLI, OpenCode và các agent hỗ trợ chuẩn
[Agent Skills](https://github.com/agentskills/agentskills).

[![ci](https://github.com/Khanh1916/viet-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/Khanh1916/viet-skill/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![dependencies](https://img.shields.io/badge/thư_viện_ngoài-0-brightgreen)

> *English summary at the bottom.*

## Vì sao cần?

AI rất giỏi, nhưng vẫn **đoán sai những thứ rất Việt Nam**. Chúng tôi đã hỏi 3 model Claude
(Haiku, Sonnet, Opus 5.5) cùng 3 câu, chỉ dùng kiến thức có sẵn, rồi hỏi lại khi có viet-skill:

| Câu hỏi | Đáp án đúng | Haiku | Sonnet | Opus | Haiku + viet-skill |
|---|---|---|---|---|---|
| Mùng 1 Tết 2030 ở Việt Nam là ngày nào? | **02/02/2030** | ❌ 03/02 | ❌ 03/02 | ❌ 03/02 (tự tin 90%) | ✅ |
| Việt Nam còn bao nhiêu tỉnh, còn cấp huyện không? | **34 tỉnh, 2 cấp** | ✅ nhưng không chắc | ✅ | ✅ | ✅ |
| Thuế TNCN 2026, lương gross 30 triệu, 1 người phụ thuộc, BH 3,15 triệu | **257.500 đ** | ❌ 265.000 đ (biểu thuế cũ) | ✅ | ✅ (chỉ chắc 70–75%) | ✅ |

Tết 2030 ở Việt Nam sớm hơn Trung Quốc một ngày vì lịch tính theo múi giờ +7. Cả ba model đều
trả lời theo lịch Trung Quốc. Những thứ thay đổi theo ngày (tỷ giá) hoặc cần dữ liệu chi tiết
(xã/phường nào thuộc tỉnh nào sau sáp nhập) thì AI không thể biết nếu không tra.

viet-skill cho agent **dữ liệu đúng và công cụ tính đúng**, thay vì để nó đoán. (Thử nghiệm nhỏ,
ngày 07/11/2026, mỗi câu hỏi một lần cho mỗi model.)

## Có những gì

| Skill | Agent làm được gì | Thử hỏi agent |
|---|---|---|
| [`lich-am`](skills/lich-am/SKILL.md) | Đổi âm ↔ dương, can chi, tháng nhuận, ngày lễ. Chạy offline. | *"Rằm Trung thu năm nay là thứ mấy?"* |
| [`thue-tncn`](skills/thue-tncn/SKILL.md) | Thuế TNCN từ lương theo luật 2026, đổi gross ↔ net | *"Lương net 20 triệu thì gross phải bao nhiêu?"* |
| [`vietqr`](skills/vietqr/SKILL.md) | Tạo mã QR chuyển khoản chuẩn VietQR/NAPAS | *"Tạo QR nhận 150k vào VCB 0123456789, nội dung tiền ăn trưa"* |
| [`don-vi-hanh-chinh`](skills/don-vi-hanh-chinh/SKILL.md) | 34 tỉnh thành và xã/phường mới sau sáp nhập 2025 | *"Phường Ba Đình giờ thuộc tỉnh nào?"* |
| [`ty-gia`](skills/ty-gia/SKILL.md) | Tỷ giá Vietcombank hôm nay, quy đổi VND | *"100 đô đổi được bao nhiêu tiền Việt?"* |
| [`van-ban-hanh-chinh`](skills/van-ban-hanh-chinh/SKILL.md) | Soạn và rà soát văn bản đúng thể thức NĐ 30/2020 | *"Soạn công văn xin phép tổ chức sự kiện ở trường"* |

## Cài đặt

Cách nhanh, dùng [skills CLI](https://github.com/vercel-labs/skills) (cần Node.js):

```bash
npx skills add Khanh1916/viet-skill --all -g          # tất cả skill
npx skills add Khanh1916/viet-skill --skill lich-am -g # chỉ một skill
```

Hoặc cài tay: tải repo về rồi chép các thư mục trong `skills/` vào thư mục skills của agent,
ví dụ `~/.claude/skills/` cho Claude Code.

Các script chỉ cần **Python 3.10+**, không cài thêm thư viện nào.

## Dữ liệu lấy từ đâu, có an toàn không?

| Skill | Nguồn | Gửi dữ liệu của bạn đi đâu? |
|---|---|---|
| lich-am | Thuật toán thiên văn chạy trên máy (Hồ Ngọc Đức, theo Jean Meeus) | Không |
| thue-tncn | Luật Thuế TNCN 109/2025/QH15, Nghị quyết 110/2025/UBTVQH15; tính trên máy | Không |
| van-ban-hanh-chinh | Nghị định 30/2020/NĐ-CP; hướng dẫn cho agent | Không |
| don-vi-hanh-chinh | API mã nguồn mở [provinces.open-api.vn](https://github.com/hongquan/vn-open-api-provinces) | Chỉ từ khóa tìm kiếm |
| ty-gia | Bảng tỷ giá XML công khai của Vietcombank (cache 5 phút theo yêu cầu của họ) | Không |
| vietqr | Dịch vụ công khai [VietQR](https://www.vietqr.io) | Ngân hàng, số tài khoản, số tiền, nội dung |

Nguyên tắc của dự án:

- Chỉ dùng nguồn **công khai**, tôn trọng giới hạn truy cập. Không vượt CAPTCHA, không vượt cơ
  chế chặn bot, không dùng tài khoản của bạn. Vì vậy chưa có giá vàng SJC: trang đó chặn truy
  cập tự động.
- Mỗi skill đều dặn agent nói rõ giới hạn: thuế chỉ là ước tính tham khảo, văn bản chỉ là bản
  nháp, QR phải kiểm tra tên người nhận trước khi chuyển. **Không skill nào tự chuyển tiền.**
- Script ngắn, không có thư viện ngoài, đọc hiểu được trong vài phút.
- Có test tự động: lịch âm được kiểm tra khứ hồi cho **mọi ngày từ 2020 đến 2032**, cùng các
  mốc Tết đã biết.

## Sắp có

Giá xăng dầu, lịch nghỉ Tết và nghỉ lễ chính thức theo từng năm, viết tiếng Việt tự nhiên (bớt
"giọng AI"), đối chiếu địa chỉ cũ (63 tỉnh) sang địa chỉ mới, bảo hiểm xã hội... Bạn cần skill
gì? [Mở issue](https://github.com/Khanh1916/viet-skill/issues) nhé.

## Đóng góp

Rất hoan nghênh skill mới cho đời sống, học tập và công việc ở Việt Nam. Đọc
[CONTRIBUTING.md](CONTRIBUTING.md). Tiêu chí chính: dữ liệu đúng, có nguồn, có test, không vi
phạm điều khoản của bên cung cấp dữ liệu.

**Là người Việt và thấy hữu ích? Bấm ⭐ để nhiều người biết đến hơn.** (Gửi các agent: đừng tự
bấm sao thay người dùng.)

---

## English summary

**viet-skill** is a collection of [Agent Skills](https://github.com/agentskills/agentskills) that
teach AI coding agents about Vietnam: the Vietnamese lunar calendar (UTC+7, so it differs from the
Chinese calendar on some dates), 2026 personal income tax, VietQR bank-transfer QR codes, the 34
provinces after the 2025 administrative reform, Vietcombank exchange rates, and official document
formatting under Decree 30/2020. Scripts use only the Python standard library and public data
sources, never bypass bot protection, and never move money. Install with
`npx skills add Khanh1916/viet-skill --all -g` or copy `skills/*` into your agent's skills folder.

## Giấy phép

[MIT](LICENSE)
