---
name: ty-gia
description: Tỷ giá ngoại tệ hôm nay của Vietcombank (USD, EUR, JPY, KRW, CNY...) - giá mua tiền mặt, mua chuyển khoản, bán ra - và quy đổi giữa VND và ngoại tệ. Use when the user asks for Vietnamese exchange rates, tỷ giá, giá đô hôm nay, or to convert between VND and a foreign currency.
---

# Tỷ giá Vietcombank

Tỷ giá thay đổi trong ngày: không bao giờ dùng con số trong trí nhớ, luôn chạy script.

```bash
python scripts/ty_gia.py                      # cả bảng
python scripts/ty_gia.py USD JPY KRW
python scripts/ty_gia.py doi 100 USD          # ngoại tệ -> VND (giá mua chuyển khoản)
python scripts/ty_gia.py doi 5000000 VND JPY  # VND -> ngoại tệ (giá bán)
python scripts/ty_gia.py --json USD
```

## Khi trả lời

- Luôn nêu **thời điểm** của bảng tỷ giá và loại giá đã dùng (mua tiền mặt, mua chuyển khoản
  hay bán). Khi người dùng bán ngoại tệ cho ngân hàng thì dùng giá mua; khi mua ngoại tệ thì
  dùng giá bán.
- Đây là tỷ giá niêm yết của một ngân hàng (Vietcombank), tham khảo. Ngân hàng khác, thẻ quốc
  tế hoặc ví điện tử có tỷ giá và phí riêng.
- Vietcombank yêu cầu tối đa 1 lần lấy dữ liệu mỗi 5 phút; script tự cache. Đừng chạy lặp lại
  liên tục.
- Không có giá vàng: trang giá vàng SJC chặn truy cập tự động, và skill này không vượt qua cơ
  chế chặn đó.
