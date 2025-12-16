# 📧 EMAIL REGISTRATION GATE – BUSINESS SPEC (VIBE CODING)

---

## 1. Mục tiêu (Business Goal)

- Thu thập **email người dùng** ngay lần đầu sử dụng ứng dụng
- Không cần backend riêng
- Sử dụng **Google Form** để lưu trữ và quản lý email
- Đảm bảo:
  - Người dùng **bắt buộc nhập email** để sử dụng app
  - Chỉ hiển thị **1 lần duy nhất** trên mỗi máy

---

## 2. Phạm vi áp dụng

- Desktop App (Windows / macOS)
- Python Window App (Tkinter / PyQt / Custom UI)
- Không phụ thuộc server riêng

---

## 3. Điều kiện hiển thị Modal

### Khi app khởi động
- Nếu **chưa đăng ký email trên máy**
  → **Hiển thị modal bắt buộc**
- Nếu **đã đăng ký email**
  → **Không hiển thị modal**

> Trạng thái đăng ký được lưu **local** (file / local storage / registry / key-value)

---

## 4. Modal đăng ký email (BẮT BUỘC)

### 4.1 Hành vi

- Modal **không thể tắt**
- Không có nút Close / X / ESC
- Toàn bộ UI phía sau:
  - Bị **blur**
  - Bị **disable interaction**
- Chỉ khi đăng ký thành công → app mới sử dụng được

---

### 4.2 Nội dung Modal

#### Title
```
Đăng ký để tiếp tục sử dụng ứng dụng
```

#### Nội dung mô tả
```
Để sử dụng ứng dụng, bạn cần nhập email của mình.

Email sẽ được dùng để:
• Thông báo khi có bản cập nhật mới
• Gửi các thông tin quan trọng liên quan đến ứng dụng

Chúng tôi cam kết không spam và không chia sẻ email của bạn.
```

---

### 4.3 Input Email

- 1 ô input duy nhất
- Placeholder:
```
Nhập email của bạn (ví dụ: example@email.com)
```

#### Validate
- Bắt buộc nhập
- Đúng định dạng email

---

### 4.4 Button

```
[ Đăng ký & Tiếp tục ]
```

---

## 5. Gửi Email qua Google Form

### Endpoint
```
POST https://docs.google.com/forms/d/e/1FAIpQLSe03QktsJ50P-LZME7iS4bGhjbFLkHVQUIqFzZvN-jxbmQPfg/formResponse
```

### Payload
| Field | Value |
|------|------|
| entry.818918261 | Email người dùng |

---

## 6. Sau khi gửi thành công

- Hiển thị thông báo cảm ơn
- Lưu `email_registered = true`
- Mở khóa toàn bộ ứng dụng

---

## 7. Lần mở app tiếp theo

- Không hiển thị modal
- Vào thẳng app

---

## 8. Xử lý lỗi

- Hiển thị lỗi mạng
- Cho phép retry
- Không đóng modal

---

## 9. Pseudo Flow

```
IF app_start AND email_not_registered:
    show_blocking_modal()

ON submit_valid_email:
    POST to google_form
    IF success:
        save_local_flag
        unlock_app
```
