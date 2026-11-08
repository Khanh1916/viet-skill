---
name: lich-am
description: Lịch âm Việt Nam - đổi ngày dương lịch sang âm lịch và ngược lại, can chi (ngày/tháng/năm), tháng nhuận, ngày Tết Nguyên Đán, Giỗ Tổ, Trung thu và các ngày lễ Việt Nam. Use when the user asks about the Vietnamese lunar calendar, âm lịch, ngày Tết, ngày rằm, mùng 1, can chi, tuổi con giáp, or Vietnamese public holidays. Works offline.
---

# Lịch âm Việt Nam

Không bao giờ tự nhẩm ngày âm lịch: lịch âm phụ thuộc thời điểm trăng mới theo múi giờ
Việt Nam (+7) và có tháng nhuận, nên đoán rất dễ sai. Luôn chạy script:

```bash
python scripts/lich_am.py                              # hôm nay
python scripts/lich_am.py duong-sang-am 2026-09-25     # dương -> âm (YYYY-MM-DD hoặc DD/MM/YYYY)
python scripts/lich_am.py am-sang-duong 15/8/2026      # âm -> dương (năm âm lịch)
python scripts/lich_am.py am-sang-duong 1/6/2025 --nhuan   # tháng nhuận
python scripts/lich_am.py tet                          # Tết sắp tới, còn bao nhiêu ngày
python scripts/lich_am.py tet 2027
python scripts/lich_am.py ngay-le 2026                 # ngày lễ trong năm
```

Thêm `--json` để lấy kết quả có cấu trúc.

## Lưu ý khi trả lời

- Lịch Việt Nam dùng múi giờ +7 nên có lúc lệch một ngày so với lịch Trung Quốc (+8): từ
  2000 đến 2050 có 480 ngày như vậy, nằm trong 18 năm, gồm cả Tết 2007 và Tết 2030 (ở Việt Nam
  là 02/02/2030, Trung Quốc là 03/02). Kiến thức có sẵn của AI và các thư viện lịch Trung Quốc
  thường cho kết quả theo lịch Trung Quốc, nên đừng dùng chúng thay cho script.
- "Năm âm lịch" khác năm dương lịch: tháng Chạp năm 2026 âm lịch rơi vào đầu năm 2027 dương lịch.
- Con giáp/tuổi theo năm âm lịch: người sinh trước Tết thuộc năm âm lịch trước.
- Danh sách ngày lễ: loại "ngày nghỉ lễ" theo Điều 112 Bộ luật Lao động 2019. Số ngày nghỉ
  Tết, nghỉ bù và hoán đổi ngày làm việc do Chính phủ công bố riêng mỗi năm; nếu người dùng
  hỏi lịch nghỉ cụ thể, nói rõ cần kiểm tra thông báo chính thức của năm đó.
- Không đưa ra lời khuyên "ngày tốt/xấu" như sự thật; nếu được hỏi, nói rõ đó là quan niệm dân gian.
