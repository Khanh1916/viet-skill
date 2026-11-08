# Đóng góp cho viet-skill

Cảm ơn bạn! Mỗi skill là một thư mục trong `skills/`:

```
skills/ten-skill/
  SKILL.md            # bắt buộc: frontmatter `name` (trùng tên thư mục) và `description`
  scripts/ten.py      # tùy chọn: script Python chỉ dùng thư viện chuẩn
```

## Tiêu chí

1. **Đúng và có nguồn.** Ghi rõ văn bản pháp luật, số hiệu, hoặc nguồn dữ liệu. Số liệu thay
   đổi theo thời gian (thuế, lương cơ sở, ngày nghỉ) phải ghi năm áp dụng.
2. **Hợp lệ.** Chỉ dùng nguồn công khai. Không vượt CAPTCHA, không vượt chặn bot, không giả
   trình duyệt, không cần tài khoản hay mật khẩu của người dùng. Tôn trọng giới hạn truy cập và
   cache khi cần.
3. **An toàn.** Skill liên quan tiền, pháp lý, sức khỏe phải dặn agent nói rõ giới hạn, xác nhận
   lại với người dùng, và không tự thực hiện giao dịch.
4. **Không thư viện ngoài** nếu có thể; Python 3.10+.
5. **Có test** trong `tests/`, chạy offline (dùng dữ liệu mẫu thay cho gọi mạng).
6. `description` trong SKILL.md viết cả tiếng Việt và vài từ khóa tiếng Anh để agent nhận ra
   khi nào nên dùng.

## Chạy test

```bash
python -m pip install pytest
python -m pytest -q
```

Muốn đề xuất skill mới nhưng chưa code được? Cứ mở issue mô tả việc bạn muốn agent làm.
