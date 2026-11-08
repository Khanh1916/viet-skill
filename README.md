# viet-skill 🇻🇳

Hai skill cho AI agent: một skill xem lịch âm theo giờ Việt Nam, một skill soạn văn bản hành chính
đúng Nghị định 30. Dùng được với Claude Code, Codex, Cursor, Gemini CLI, OpenCode và các agent
theo chuẩn [Agent Skills](https://github.com/agentskills/agentskills).

[![ci](https://github.com/Khanh1916/viet-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/Khanh1916/viet-skill/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green)
![python](https://img.shields.io/badge/python-3.10%2B-blue)

*English below.*

## Tết 2030 là ngày nào?

Mình hỏi Claude Haiku, Sonnet và Opus câu này mà không cho dùng công cụ. Cả ba đều trả lời
03/02/2030, Opus còn tự nhận chắc 90%. Nhưng ở Việt Nam, mùng 1 Tết năm đó là **ngày 02/02/2030**.
Ngày 03/02 là Tết của Trung Quốc.

Lịch âm Việt Nam tính theo giờ Hà Nội (UTC+7), lịch Trung Quốc tính theo giờ Bắc Kinh (UTC+8).
Đầu năm 2030, trăng mới rơi vào lúc 23h09 giờ Hà Nội, tức 0h09 hôm sau ở Bắc Kinh. Vậy là
ngày 02/02 đã là mùng 1 ở Việt Nam, còn bên Trung Quốc vẫn là ngày cuối năm cũ. Chuyện này
không hiếm: từ 2000 đến 2050 có 480 ngày âm lịch hai nước lệch nhau một ngày, nằm trong 18 năm.
Năm 2007 cũng vậy, Việt Nam ăn Tết ngày 17/2 còn Trung Quốc ngày 18/2.

Mình đoán AI nghiêng về lịch Trung Quốc vì lịch âm trên mạng phần lớn là của Trung Quốc. Ngày
thường nó vẫn trả lời ổn, nhưng đến đúng những ngày hai lịch lệch nhau thì sai, và sai mà vẫn
chắc như lúc đúng. Model nhỏ thì sai cả ngày thường.

| Câu hỏi (không cho dùng công cụ) | Đáp án đúng | Haiku | Sonnet | Opus |
|---|---|---|---|---|
| Mùng 1 Tết 2030 ở Việt Nam | 02/02/2030 | 03/02 ❌ | 03/02 ❌ | 03/02 ❌ |
| Rằm tháng Giêng 2028 | 09/02/2028 | 11/02 ❌ | đúng | đúng |
| 4 câu đổi ngày, can chi, tháng nhuận | | 4/4 | 4/4 | 4/4 |
| Soạn công văn, chấm theo 10 tiêu chí thể thức NĐ 30 | | 8/10 | 9/10 | 10/10 |

Mỗi câu mình chỉ hỏi một lần, vào ngày 7 và 8/11/2026, nên đây là thử nhanh chứ chưa phải
benchmark.

## Hai skill

### lich-am

Agent không nhẩm lịch nữa mà chạy một script Python tính theo giờ Việt Nam. Script đổi ngày âm
sang dương và ngược lại, tính can chi, tháng nhuận, ngày Tết, Giỗ Tổ, Trung thu và các ngày nghỉ
lễ trong năm. Nó chạy ngay trên máy, không cần mạng, không cài thêm thư viện.

Bạn có thể hỏi agent kiểu: *"Giỗ ông ngày 23 tháng 7 âm, năm sau rơi vào thứ mấy?"*

### van-ban-hanh-chinh

Soạn hoặc soát công văn, tờ trình, thông báo, quyết định, giấy mời theo thể thức ở Phụ lục I
Nghị định 30/2020/NĐ-CP, từ Quốc hiệu, số và ký hiệu, trích yếu cho tới nơi nhận, chữ ký, phông
chữ và lề. Lúc chưa có skill, Haiku đặt Quốc hiệu sai chỗ, in nghiêng phần trích yếu và tự đặt
ký hiệu "CV". Có skill thì những lỗi đó không còn.

Skill dặn agent hỏi đủ thông tin trước khi viết, và không bịa số văn bản, căn cứ pháp lý hay tên
người. Văn bản agent soạn ra vẫn là bản nháp, người có thẩm quyền cần đọc lại trước khi ký.

Ví dụ: *"Soạn công văn xin phép tổ chức hội trại ở trường."*

## Cài đặt

Máy có Node.js 22.20 trở lên thì dùng [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add Khanh1916/viet-skill --all -g           # cả hai skill
npx skills add Khanh1916/viet-skill --skill lich-am -g  # chỉ lịch âm
```

Không dùng Node thì tải repo về rồi chép hai thư mục trong `skills/` vào thư mục skill của
agent. Với Claude Code là `~/.claude/skills/`.

Script lịch âm cần Python 3.10 trở lên.

## Mình kiểm tra thế nào

`lich-am` dùng thuật toán thiên văn của Hồ Ngọc Đức, dựa trên công thức trong sách của Jean
Meeus. Bộ test đổi qua đổi lại từng ngày từ 2020 đến 2032, so với ngày Tết các năm đã biết, rồi
tính lại Tết 2007 và 2030 theo giờ Bắc Kinh để chắc rằng kết quả lệch đúng một ngày như ngoài
đời. CI chạy bộ test này trên Windows, macOS và Linux.

`van-ban-hanh-chinh` lấy quy định từ Phụ lục I Nghị định 30/2020/NĐ-CP.

## Sắp tới

Mình định làm tiếp mấy việc này:

- Xuất ngày giỗ, rằm, mùng 1 ra file `.ics` để thêm vào Google Calendar hay lịch trên điện thoại.
  Các app lịch phổ biến chưa lặp sự kiện theo âm lịch Việt Nam, nên nhiều người vẫn phải tra rồi
  nhập tay mỗi năm.
- Thêm lịch nghỉ Tết và nghỉ lễ chính thức của từng năm, sau khi Chính phủ công bố.
- Cho `van-ban-hanh-chinh` xuất thẳng file Word đúng phông, cỡ chữ và lề, khỏi phải chỉnh lại.
- Làm skill mới cho những chỗ khác mà AI hay sai về Việt Nam.

Bạn gặp AI trả lời sai chuyện gì về Việt Nam thì
[mở issue](https://github.com/Khanh1916/viet-skill/issues) kèm câu hỏi và câu trả lời của nó.
Mình sẽ hỏi lại trên vài model, sai thật thì làm skill.

## Đóng góp

Đọc [CONTRIBUTING.md](CONTRIBUTING.md) trước khi gửi PR. Điều mình cần nhất ở một skill mới là
bằng chứng AI làm sai khi chưa có nó.

Thấy có ích thì cho mình một ⭐ nhé.

---

## English

I made these two Agent Skills because AI agents get some very Vietnamese things wrong. Ask Claude
Haiku, Sonnet or Opus when Lunar New Year (Tết) 2030 falls and all three say February 3. That's
the date in China. In Vietnam it's February 2. The Vietnamese calendar runs on UTC+7 and the
Chinese one on UTC+8, and the new moon that starts that year arrives at 23:09 in Hanoi, which is
already 00:09 the next day in Beijing. Between 2000 and 2050 the two calendars disagree on 480
days.

`lich-am` has the agent run a small Python script instead of guessing. It uses only the standard
library and works offline. `van-ban-hanh-chinh` drafts and checks Vietnamese official documents
in the format set by Decree 30/2020.

Install with `npx skills add Khanh1916/viet-skill --all -g` (needs Node.js 22.20+), or copy the
folders in `skills/` into your agent's skills directory.

## Giấy phép

[MIT](LICENSE)
