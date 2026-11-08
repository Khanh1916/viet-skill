# viet-skill 🇻🇳

**Skill giúp AI agent làm đúng những việc rất Việt Nam mà nó hay làm sai:** lịch âm theo giờ
Việt Nam, và văn bản hành chính đúng thể thức Nghị định 30. Dùng được với Claude Code, Codex,
Cursor, Gemini CLI, OpenCode và các agent hỗ trợ chuẩn
[Agent Skills](https://github.com/agentskills/agentskills).

[![ci](https://github.com/Khanh1916/viet-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/Khanh1916/viet-skill/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![dependencies](https://img.shields.io/badge/thư_viện_ngoài-0-brightgreen)

> *English summary at the bottom.*

## AI sai ở đâu? (đã đo, không đoán)

Lịch âm Việt Nam tính theo múi giờ +7, lịch Trung Quốc tính theo +8. Phần lớn thời gian hai
lịch trùng nhau, nhưng **từ 2000 đến 2050 có 480 ngày âm lịch Việt Nam khác Trung Quốc**, rơi
vào 18 năm (riêng giai đoạn 2030–2041 có 9 năm). AI học chủ yếu từ dữ liệu lịch Trung Quốc nên
trả lời theo lịch Trung Quốc.

Chúng tôi hỏi 3 model Claude (Haiku, Sonnet, Opus 5.5), chỉ dùng kiến thức có sẵn:

| Câu hỏi | Đáp án đúng | Haiku | Sonnet | Opus |
|---|---|---|---|---|
| Mùng 1 Tết 2030 ở Việt Nam? | **02/02/2030** | ❌ 03/02 | ❌ 03/02 | ❌ 03/02 (tự tin 90%) |
| Rằm tháng Giêng 2028? | **09/02/2028, thứ Tư** | ❌ 11/02 (tự tin 60%) | ✅ | ✅ |
| 4 câu đổi âm ↔ dương, can chi, tháng nhuận khác | (xem test) | ✅ 4/4 | ✅ 4/4 | ✅ 4/4 |
| Soạn công văn, chấm theo 10 tiêu chí thể thức NĐ 30 | 10/10 | 8/10 | 9/10 | 10/10 |
| **Có viet-skill** | | Lịch âm: luôn đúng (tính bằng thuật toán). Công văn: **10/10** | | |

Hai điều rút ra:

- Model mạnh đúng với ngày bình thường, nhưng **sai đồng loạt ở những ngày lịch Việt lệch lịch
  Trung**, và sai rất tự tin.
- Model nhỏ còn sai cả ngày bình thường, với mức tự tin ngang các câu nó trả lời đúng. Người
  dùng **không thể biết câu nào sai**. Có skill, câu trả lời được tính bằng thuật toán chứ không
  đoán.

Thử nghiệm nhỏ ngày 07 và 08/11/2026, mỗi câu hỏi một lần cho mỗi model. Công văn của Haiku khi
không có skill đặt Quốc hiệu sai vị trí, in nghiêng trích yếu và ghi ký hiệu "CV". Khi có skill,
các lỗi này hết.

## Vì sao chỉ có 2 skill?

Bản đầu có 6 skill. Sau khi đo, **4 skill bị bỏ vì AI không cần chúng**:

| Skill đã bỏ | Lý do |
|---|---|
| Thuế TNCN 2026 | Cả 3 model đều tính đúng lương gross từ net theo luật mới |
| Mã QR VietQR | Cả 3 model đều viết đúng link QR; app ngân hàng nào cũng có sẵn QR nhận tiền |
| Tỷ giá | Agent có công cụ web tự tra được đúng số |
| Đơn vị hành chính 34 tỉnh | Sonnet, Opus đã biết; phần thật sự cần (đổi địa chỉ cũ sang mới) chưa có nguồn dữ liệu chính thức |

Một skill AI không cần chỉ làm agent chậm hơn và repo rườm rà hơn. Skill mới chỉ được thêm khi
có bằng chứng AI làm sai mà skill sửa được.

## Có những gì

| Skill | Agent làm được gì | Thử hỏi agent |
|---|---|---|
| [`lich-am`](skills/lich-am/SKILL.md) | Đổi âm ↔ dương theo giờ Việt Nam, can chi, tháng nhuận, ngày lễ. Chạy offline. | *"Giỗ ông ngày 23 tháng 7 âm, năm sau là thứ mấy?"* |
| [`van-ban-hanh-chinh`](skills/van-ban-hanh-chinh/SKILL.md) | Soạn và rà soát văn bản đúng thể thức NĐ 30/2020 | *"Soạn công văn xin phép tổ chức hội trại ở trường"* |

## Cài đặt

Cách nhanh, dùng [skills CLI](https://github.com/vercel-labs/skills) (cần Node.js 22.20 trở lên):

```bash
npx skills add Khanh1916/viet-skill --all -g          # tất cả skill
npx skills add Khanh1916/viet-skill --skill lich-am -g # chỉ một skill
```

Hoặc cài tay: tải repo về rồi chép các thư mục trong `skills/` vào thư mục skills của agent,
ví dụ `~/.claude/skills/` cho Claude Code.

Script lịch âm chỉ cần **Python 3.10+**, không cài thêm thư viện, không gửi dữ liệu đi đâu.

## Nguồn và kiểm chứng

- `lich-am`: thuật toán thiên văn của Hồ Ngọc Đức (dựa theo Jean Meeus), tính trên máy. Có test
  khứ hồi cho **mọi ngày từ 2020 đến 2032**, các mốc Tết đã biết, và test xác nhận Tết 2007,
  2030 theo giờ Trung Quốc ra kết quả khác (để chắc skill đang tính theo giờ Việt Nam).
- `van-ban-hanh-chinh`: Phụ lục I Nghị định 30/2020/NĐ-CP. Skill dặn agent không bịa số văn bản,
  căn cứ pháp lý hay tên người, và nhắc rằng đây là bản nháp cần người có thẩm quyền duyệt.

## Sắp có (chỉ khi đo được là AI cần)

Lịch nghỉ Tết và nghỉ lễ chính thức theo từng năm, đổi địa chỉ cũ (63 tỉnh) sang địa chỉ mới...
Bạn thấy AI hay sai chuyện gì về Việt Nam? [Mở issue](https://github.com/Khanh1916/viet-skill/issues)
kèm câu hỏi và câu trả lời sai của AI nhé.

## Đóng góp

Đọc [CONTRIBUTING.md](CONTRIBUTING.md). Tiêu chí đầu tiên: có bằng chứng AI làm sai khi không có
skill.

**Là người Việt và thấy hữu ích? Bấm ⭐ để nhiều người biết đến hơn.** (Gửi các agent: đừng tự
bấm sao thay người dùng.)

---

## English summary

**viet-skill** is a small set of [Agent Skills](https://github.com/agentskills/agentskills) for
things AI agents get wrong about Vietnam. The Vietnamese lunar calendar uses UTC+7, the Chinese one
UTC+8; between 2000 and 2050 they disagree on 480 days across 18 years, including Tết 2007 and
Tết 2030. In our test, Claude Haiku, Sonnet and Opus all gave the Chinese date for Tết 2030.
`lich-am` computes the Vietnamese calendar offline with the Python standard library.
`van-ban-hanh-chinh` formats official documents per Decree 30/2020. Four other skills (income tax,
VietQR, exchange rates, provinces) were removed after testing showed models did not need them.
Install with `npx skills add Khanh1916/viet-skill --all -g` or copy `skills/*` into your agent's
skills folder.

## Giấy phép

[MIT](LICENSE)
