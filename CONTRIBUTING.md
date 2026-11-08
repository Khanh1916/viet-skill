# Đóng góp cho viet-skill

Cảm ơn bạn đã ghé qua. Mỗi skill là một thư mục trong `skills/`:

```
skills/ten-skill/
  SKILL.md            # bắt buộc: frontmatter `name` (trùng tên thư mục) và `description`
  scripts/ten.py      # không bắt buộc: script Python chỉ dùng thư viện chuẩn
```

## Trước khi làm skill mới

Cho mình thấy AI đang sai. Gửi kèm vài câu hỏi thực tế mà ít nhất một model phổ biến trả lời sai
khi chưa có skill, và trả lời đúng khi có. Nếu AI đã tự làm đúng thì thêm skill chỉ làm agent
chậm đi.

## Yêu cầu

1. Có nguồn. Ghi rõ văn bản pháp luật, số hiệu hoặc nguồn dữ liệu. Thứ gì thay đổi theo năm
   (thuế, lương cơ sở, ngày nghỉ) thì ghi năm áp dụng.
2. Lấy dữ liệu đàng hoàng. Chỉ dùng nguồn công khai, không vượt CAPTCHA hay chặn bot, không giả
   trình duyệt, không đòi tài khoản hay mật khẩu của người dùng. Có gọi mạng thì tôn trọng giới
   hạn truy cập của nguồn và lưu cache khi cần.
3. Việc dính đến tiền, pháp lý hay sức khỏe thì skill phải dặn agent nói rõ giới hạn, hỏi lại
   người dùng trước khi làm, và không tự thực hiện giao dịch.
4. Script viết bằng Python 3.10 trở lên, cố gắng chỉ dùng thư viện chuẩn.
5. Có test trong `tests/` chạy được khi không có mạng. Chỗ nào cần gọi mạng thì dùng dữ liệu mẫu.
6. Phần `description` trong SKILL.md viết bằng tiếng Việt, thêm vài từ khóa tiếng Anh để agent
   biết lúc nào nên dùng skill.

## Chạy test

```bash
python -m pip install pytest
python -m pytest -q
```

Có ý tưởng mà chưa code được thì cứ mở issue, kể việc bạn muốn agent làm.
