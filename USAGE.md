# ✅ Build Hoàn Thành!

## 📍 File Executable đã tạo

**Location:** `dist/StarterAppLauncher.exe` (~49 MB)

## 🚀 Cách sử dụng

### 1. Chạy App
#### Option A: Double-click
- Vào thư mục `dist/`
- **Double-click** vào file `StarterAppLauncher.exe`
- App sẽ mở ra mà không cần Python!

#### Option B: Dùng script (Recommended)
```batch
# Chạy từ project root
run.bat
```

### 2. Build lại (sau khi sửa code)
```batch
# Chạy từ project root
build.bat
```

Hoặc manual:
```bash
pyinstaller --onefile --windowed --clean --name "StarterAppLauncher" --paths "src" --add-data "src/i18n/locales;i18n/locales" --hidden-import ui.main_window --hidden-import ui.pages.dashboard_page --hidden-import ui.pages.starter_page --hidden-import ui.pages.admin_page --hidden-import ui.pages.coming_soon_page --hidden-import ui.tabs.startup_status_tab --hidden-import ui.tabs.favourite_tab --hidden-import ui.tabs.all_apps_tab --hidden-import ui.tabs.settings_tab --hidden-import ui.tabs.languages_tab --hidden-import ui.tabs.trigger_tab --hidden-import ui.tabs.rules_tab --hidden-import ui.theme --hidden-import i18n.translator --hidden-import storage.config_store --hidden-import services.system_metrics_service --hidden-import services.startup_monitor_service --hidden-import services.discovery_service --hidden-import services.launcher_service --hidden-import services.startup_service --hidden-import services.url_service --hidden-import models.config_models --hidden-import utils.paths --hidden-import PySide6.QtCore --hidden-import PySide6.QtGui --hidden-import PySide6.QtWidgets --hidden-import qtawesome --hidden-import psutil src/app/main.py
```

### 2. Tạo Shortcut trên Desktop
1. Click chuột phải vào `StarterAppLauncher.exe`
2. Chọn "Send to" → "Desktop (create shortcut)"
3. Hoặc "Create shortcut" rồi kéo ra Desktop

### 3. Chạy với quyền Administrator (khi cần)

**App chạy bình thường không cần admin!**

Chỉ cần admin khi:
- ✅ Bật/tắt Autostart (Trigger tab)
- ✅ Kill system processes
- ✅ Remove system startup entries

**Cách chạy với admin:**
- **Option A:** Click chuột phải vào `StarterAppLauncher.exe` → **"Run as administrator"**
- **Option B:** Properties → Compatibility → ✅ "Run this program as an administrator"
- **Option C:** Dùng Rules tab trong app để request admin (app sẽ tự restart)

### 4. Pin vào Taskbar
- Click chuột phải vào `StarterAppLauncher.exe`
- Chọn "Pin to taskbar"

## 📦 Distribution (Chia sẻ cho người khác)

### Cách 1: Chia sẻ single file (Dễ nhất)
- Chỉ cần copy file `StarterAppLauncher.exe` (~70-100MB)
- Gửi cho người khác qua email, USB, cloud...
- Người nhận chỉ cần double-click là chạy được!

### Cách 2: Tạo Installer (Professional)
Dùng **Inno Setup** hoặc **NSIS** để tạo file installer.exe

## ⚙️ Build Options

### Đã build với các tùy chọn:
- ✅ `--onefile`: Single executable file
- ✅ `--windowed`: No console window (GUI only)
- ✅ `--add-data`: Include locale files (vi/en/ru)
- ✅ Hidden imports: PySide6, qtawesome, psutil

### Nếu muốn rebuild:
```bash
# Quick rebuild
pyinstaller --onefile --windowed --name "StarterAppLauncher" ^
  --add-data "src/i18n/locales;i18n/locales" ^
  --hidden-import PySide6.QtCore ^
  --hidden-import PySide6.QtGui ^
  --hidden-import PySide6.QtWidgets ^
  --hidden-import qtawesome ^
  --hidden-import psutil ^
  src/app/main.py

# Or use spec file
pyinstaller StarterAppLauncher.spec
```

## 🎯 Features của file .exe

✅ **Không cần cài Python**
✅ **Không cần cài dependencies**
✅ **Single file - portable**
✅ **Double-click để chạy**
✅ **Có thể chạy trên máy Windows khác**
✅ **Hỗ trợ quyền Admin**
✅ **Dark theme UI**
✅ **Multi-language (vi/en/ru)**

## 📝 Notes

### File size
- **~70-100MB** (single file bao gồm Python runtime + tất cả dependencies)

### Requirements
- **Windows 10/11** (64-bit)
- **Không cần Python** trên máy đích
- **Không cần dependencies** (tất cả đã bundle)

### First run
- Lần đầu chạy có thể hơi chậm (2-3 giây)
- App sẽ extract files vào temp folder
- Lần chạy sau sẽ nhanh hơn

### Antivirus warning
- Một số antivirus có thể cảnh báo (false positive)
- Vì PyInstaller packed executable
- Bình thường và an toàn!

## 🐛 Troubleshooting

### App không mở được
- Chạy từ Command Prompt để xem error:
  ```
  cd dist
  StarterAppLauncher.exe
  ```

### Thiếu icons
- Build lại với qtawesome fonts

### Thiếu translations
- Check locale files đã được include chưa

## 🎨 Thêm Custom Icon (Optional)

1. Tạo file `icon.ico` (256x256 recommended)
2. Build lại với `--icon`:
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico ^
     --name "StarterAppLauncher" ^
     src/app/main.py
   ```

## ✨ Hoàn thành!

File executable của bạn đã sẵn sàng:
📍 **`dist/StarterAppLauncher.exe`**

Bây giờ bạn có thể:
- ✅ Double-click để chạy
- ✅ Tạo shortcut
- ✅ Pin vào taskbar
- ✅ Chia sẻ cho người khác
- ✅ Deploy lên máy khác

Chúc mừng! 🎉

