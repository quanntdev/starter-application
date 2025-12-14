# 🚀 Quick Start: Publish lên Microsoft Store

## ⚠️ Lưu ý Quan Trọng

**Đây là Windows app, KHÔNG thể publish lên Google Play Store.**

Để publish Windows app, bạn cần sử dụng **Microsoft Store** (không phải Google Store).

---

## Bước 1: Đăng ký Microsoft Partner Center

1. Truy cập: https://partner.microsoft.com/dashboard
2. Đăng nhập với Microsoft Account
3. Đăng ký Developer Account ($19 USD - một lần)
4. Hoàn tất verification (1-2 ngày)

---

## Bước 2: Package App thành MSIX

### Tự động (Khuyến nghị):

```powershell
.\package-msix.ps1
```

Script sẽ:
- ✅ Copy EXE file
- ✅ Tạo icons từ avatar.png
- ✅ Copy AppxManifest.xml
- ✅ Package thành MSIX

### Thủ công:

1. Cài đặt **MSIX Packaging Tool** từ Microsoft Store
2. Mở tool và chọn "Create new package"
3. Chọn thư mục `dist` (chứa StarterAppLauncher.exe)
4. Điền thông tin app
5. Export thành MSIX

---

## Bước 3: Tạo App trong Partner Center

1. Vào https://partner.microsoft.com/dashboard
2. **Apps & games** → **+ Create new app**
3. Điền:
   - **App name**: Starter App Launcher
   - **App type**: Desktop app (Win32)
   - **Reservations**: Chọn countries

---

## Bước 4: Upload Package

1. Vào **Packages** section
2. Upload file `.msix` đã tạo
3. Microsoft sẽ validate package
4. Fix lỗi nếu có

---

## Bước 5: Store Listing

### Screenshots (Bắt buộc)

- Desktop screenshots: 1-9 images (1366x768px minimum)
- Chụp các màn hình chính của app

### Description

```
# Starter App Launcher

Modern Windows desktop application for managing favorite applications, monitoring system metrics, and controlling startup programs.

## Features

- 📊 Real-time system monitoring (CPU & RAM)
- ⭐ Manage favorite apps and browsers
- 🚀 Startup app management
- 🛡️ Admin tools with multi-language support

## System Requirements

- Windows 10 (version 1809+) or Windows 11
- 50 MB free disk space
```

### Additional Info

- **Category**: Productivity / Utilities
- **Keywords**: app launcher, startup manager, system monitor
- **Privacy policy**: (nếu app thu thập data)

---

## Bước 6: Submit để Review

1. Kiểm tra checklist:
   - [ ] Package đã upload
   - [ ] Screenshots đã thêm
   - [ ] Description đầy đủ
   - [ ] Privacy policy (nếu cần)
   - [ ] App đã test kỹ

2. Click **Submit to the Store**
3. Chờ review (1-3 ngày)
4. Nhận email khi có kết quả

---

## Chi phí

- **Developer Account**: $19 USD (một lần)
- **App Listing**: Free
- **Updates**: Free
- **Revenue Share**: 15% (nếu app có phí)

---

## Timeline

- **Account Setup**: 1-2 ngày
- **Package Preparation**: 1 ngày
- **Store Listing**: 1 ngày
- **Review Process**: 1-3 ngày
- **Total**: ~1 tuần

---

## Troubleshooting

### Package Validation Failed

- Kiểm tra AppxManifest.xml format
- Đảm bảo tất cả assets tồn tại
- Test package trên Windows 10/11

### Submission Rejected

- Đọc feedback từ Microsoft
- Fix issues và resubmit

---

## Tài liệu Chi tiết

Xem `MICROSOFT_STORE_GUIDE.md` để biết hướng dẫn đầy đủ.

---

## Hỗ trợ

- [Microsoft Partner Center](https://partner.microsoft.com/)
- [Store Policies](https://docs.microsoft.com/en-us/legal/windows/agreements/store-policies)
- [MSIX Documentation](https://docs.microsoft.com/en-us/windows/msix/)

---

**Good luck! 🚀**

