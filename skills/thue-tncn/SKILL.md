---
name: thue-tncn
description: Tính thuế thu nhập cá nhân (TNCN) Việt Nam từ tiền lương theo quy định 2026 - biểu lũy tiến 5 bậc, giảm trừ gia cảnh 15,5 triệu và 6,2 triệu/người phụ thuộc, đổi lương gross sang net và net sang gross. Use when the user asks about Vietnamese personal income tax, thuế TNCN, lương gross/net, giảm trừ gia cảnh, or how much tax a salary in Vietnam pays.
---

# Thuế TNCN từ tiền lương (Việt Nam, 2026)

Luôn tính bằng script, không nhẩm:

```bash
python scripts/tncn.py gross 30000000 --phu-thuoc 1
python scripts/tncn.py gross 60000000 --bao-hiem 4914000    # nhập tiền bảo hiểm thực tế
python scripts/tncn.py net 20000000                          # NET 20 triệu -> GROSS bao nhiêu
python scripts/tncn.py --json gross 25000000
```

## Căn cứ đang dùng

- Biểu lũy tiến 5 bậc theo tháng (Điều 9 Luật Thuế TNCN số 109/2025/QH15):
  đến 10 triệu 5%; trên 10 đến 30 triệu 10%; trên 30 đến 60 triệu 20%;
  trên 60 đến 100 triệu 30%; trên 100 triệu 35%.
- Giảm trừ gia cảnh: 15,5 triệu/tháng (bản thân), 6,2 triệu/tháng mỗi người phụ thuộc
  (Nghị quyết 110/2025/UBTVQH15, từ kỳ tính thuế 2026).
- Thu nhập tính thuế = lương gross - bảo hiểm bắt buộc phần người lao động - giảm trừ gia cảnh.

## Khi trả lời

- Script chỉ áp dụng cho **cá nhân cư trú, thu nhập từ tiền lương, tiền công**. Không dùng cho
  cá nhân không cư trú (thuế suất 20% toàn phần), hộ kinh doanh, cho thuê tài sản, chuyển nhượng.
- Nếu người dùng không cho biết tiền bảo hiểm, script ước tính 10,5% lương gross (BHXH 8%,
  BHYT 1,5%, BHTN 1%) và **không áp mức trần** đóng bảo hiểm. Hãy nói rõ giả định này; với
  lương cao hoặc lương đóng bảo hiểm thấp hơn lương thực nhận, hỏi số tiền bảo hiểm thực tế.
- Các khoản phụ cấp miễn thuế (ăn trưa, điện thoại, trang phục... trong hạn mức) không được
  trừ tự động. Hỏi người dùng nếu có.
- Đây là ước tính để tham khảo, không phải tư vấn thuế. Với quyết toán thuế, khuyên người dùng
  đối chiếu với kế toán hoặc cơ quan thuế.
