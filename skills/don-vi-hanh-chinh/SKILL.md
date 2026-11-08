---
name: don-vi-hanh-chinh
description: Tra cứu đơn vị hành chính Việt Nam sau sắp xếp năm 2025 - 34 tỉnh/thành phố, chính quyền 2 cấp (tỉnh - xã/phường/đặc khu), tìm một xã/phường thuộc tỉnh nào, liệt kê xã/phường của một tỉnh. Use when the user asks about Vietnamese provinces, wards, communes, addresses after the 2025 administrative merger, "tỉnh mới", "phường mới", or needs Vietnamese administrative codes.
---

# Đơn vị hành chính Việt Nam (từ 01/7/2025)

Từ 01/7/2025 Việt Nam còn **34 tỉnh/thành phố** và bỏ cấp huyện (chính quyền 2 cấp: tỉnh và
xã/phường/đặc khu). Kiến thức có sẵn của mô hình phần lớn là danh sách **63 tỉnh, 3 cấp** cũ, nên
luôn tra bằng script thay vì trả lời theo trí nhớ:

```bash
python scripts/dvhc.py tinh                 # 34 tỉnh/thành
python scripts/dvhc.py tim "ba đình"        # xã/phường tên này thuộc tỉnh nào (có dấu hoặc không)
python scripts/dvhc.py xa "hồ chí minh"     # danh sách xã/phường của một tỉnh (tên hoặc mã)
python scripts/dvhc.py --json tim "an khánh"
```

## Khi trả lời

- Địa chỉ mới có dạng: số nhà, đường, **xã/phường**, **tỉnh/thành phố** (không còn quận/huyện).
- Nhiều xã/phường trùng tên ở các tỉnh khác nhau: nếu có nhiều kết quả, hỏi lại tỉnh.
- Script chưa có bảng đối chiếu địa chỉ cũ (63 tỉnh, có huyện) sang địa chỉ mới. Nếu người dùng
  đưa địa chỉ cũ, nói rõ điều này và gợi ý tra cứu trên cổng thông tin chính thức của tỉnh.
- Dữ liệu từ dự án mã nguồn mở provinces.open-api.vn, cache 1 ngày. Với giấy tờ pháp lý, đối
  chiếu với nghị quyết sắp xếp đơn vị hành chính của Ủy ban Thường vụ Quốc hội.
