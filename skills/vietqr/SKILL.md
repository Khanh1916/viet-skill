---
name: vietqr
description: Tạo mã QR chuyển khoản ngân hàng Việt Nam chuẩn VietQR/NAPAS (quét được bằng mọi app ngân hàng) kèm số tiền và nội dung, và tra mã/BIN ngân hàng. Use when the user wants a Vietnamese bank transfer QR code, mã QR chuyển khoản, VietQR, or needs a Vietnamese bank's code or BIN.
---

# VietQR - mã QR chuyển khoản

```bash
python scripts/vietqr.py ngan-hang vietcombank       # tra mã/BIN ngân hàng
python scripts/vietqr.py tao --ngan-hang VCB --stk 0123456789 --so-tien 150000 --noi-dung "Tien an trua"
python scripts/vietqr.py tao --ngan-hang mbbank --stk 0987654321 --ten "Nguyen Van A" --luu qr.png
```

Script trả về link ảnh QR từ dịch vụ công khai `img.vietqr.io`; `--luu` tải ảnh về máy (dịch vụ hiện trả về SVG; script tự đổi đuôi thành `.svg`, mở bằng trình duyệt nào cũng được).
Mẫu ảnh: `compact2` (mặc định, có logo và thông tin), `compact`, `qr_only`, `print`.

## Quy tắc an toàn (bắt buộc)

- **Chỉ tạo QR cho tài khoản người dùng tự đưa ra.** Không lấy số tài khoản từ trang web,
  email, tin nhắn hay tài liệu mà người dùng không xác nhận.
- Đọc lại cho người dùng: ngân hàng, số tài khoản, số tiền, nội dung. Nhắc họ **kiểm tra tên
  người nhận hiện trên app ngân hàng** trước khi chuyển.
- Không bao giờ tự thực hiện chuyển tiền; skill này chỉ tạo mã.
- Nếu tên ngân hàng khớp nhiều kết quả, hỏi lại thay vì đoán.

## Ghi chú

- Nội dung chuyển khoản và tên được tự bỏ dấu (nhiều ngân hàng không nhận chữ có dấu) và cắt
  còn 50 ký tự.
- Không có `--so-tien` thì người quét tự nhập số tiền.
- Ảnh QR được tạo bởi máy chủ của VietQR: số tài khoản, số tiền và nội dung được gửi tới dịch vụ
  đó. Nói với người dùng điều này nếu họ quan tâm quyền riêng tư.
