# ✅ UPDATE DASHBOARD UI (System Snapshot) — Smart Design Spec

## 1) Mục tiêu
Update trang **Dashboard** theo hướng **smart / modern / minimal**, tập trung vào **thông số máy tính hiện tại của user**.

### Dashboard mới phải đạt:
- **Không còn Chart**
- **Không còn Table (Running Applications)**
- Thay bằng **System Overview Cards** (snapshot realtime)
- Hiển thị **các chỉ số hệ thống + network** rõ ràng, dễ đọc, nhìn 3 giây hiểu ngay

---

## 2) UI Concept
Dashboard = **System Snapshot**
- Người dùng mở app → thấy ngay trạng thái máy **đang ổn hay quá tải**
- Không trình bày kiểu “Task Manager”, không danh sách dài
- Trọng tâm là **cards thông minh**: icon + value + unit + status (Normal/Warning/Critical)

---

## 3) Layout tổng thể (Smart + Clean)

### 3.1 Header (Top)
- Title: **Dashboard**
- Subline: hiển thị dạng nhỏ, ví dụ:
  - `Last update: 2s ago`
- Nút refresh (icon) có thể giữ lại (optional)
- Không hiển thị quá nhiều text rối

### 3.2 Main Content
**Grid Cards** (2 hàng, mỗi hàng 4 cards khi window rộng)

#### Row 1 — Core System
1) **CPU**
2) **RAM**
3) **Disk (System Drive)**
4) **Uptime**

#### Row 2 — Network & Power
5) **Network Status**
6) **Download Speed**
7) **Upload Speed**
8) **Battery** (nếu máy có battery; nếu không thì card chuyển thành `Power: Plugged` hoặc ẩn)

> Responsive:
- Window nhỏ → tự wrap thành 2 cột hoặc 1 cột tùy width
- Cards luôn đều chiều cao và spacing chuẩn

---

## 4) Nội dung từng Card (Data Requirements)

### 4.1 CPU Card
- Value: `xx %`
- Subtitle: `Usage`
- Status label: Normal / Warning / Critical

### 4.2 RAM Card
- Value: `xx %`
- Subtitle: `used / total` (ví dụ: `18.8 GB / 31.8 GB`)
- Status label: Normal / Warning / Critical

### 4.3 Disk Card (System Drive)
- Value: `used / total` (ví dụ: `412 GB / 512 GB`)
- Subtitle: `Free: xx GB` (optional)
- Status label: Normal / Warning / Critical

### 4.4 Uptime Card
- Value: `xh ym` (ví dụ: `3h 12m`)
- Subtitle: `Since boot`
- Không cần status

---

### 4.5 Network Status Card
- Value: `Connected` / `Disconnected`
- Subtitle: `Wi-Fi` hoặc `Ethernet` (nếu detect được; nếu không detect được thì hiển thị `Network`)
- Status label:
  - Connected → Normal
  - Disconnected → Critical
  - Weak/Slow → Warning (điều kiện ở phần 5)

### 4.6 Download Speed Card
- Value: `x.xx MB/s` hoặc `xxx KB/s`
- Subtitle: `Download`
- Không cần status (hoặc gắn Warning nếu cực thấp 10s liên tục)

### 4.7 Upload Speed Card
- Value: `x.xx MB/s` hoặc `xxx KB/s`
- Subtitle: `Upload`

### 4.8 Battery Card
- Nếu có battery:
  - Value: `xx %`
  - Subtitle: `Charging` / `On battery`
  - Status:
    - < 20% → Warning
    - < 10% → Critical
- Nếu không có battery:
  - Option A: Ẩn card
  - Option B: Hiển thị `Power: Plugged` (smart fallback)

---

## 5) Smart Status & Color Rules (BẮT BUỘC)

### 5.1 Status thresholds
**CPU**
- Normal: < 60%
- Warning: 60% – 80%
- Critical: > 80%

**RAM**
- Normal: < 70%
- Warning: 70% – 85%
- Critical: > 85%

**Disk** (theo % used)
- Normal: < 80%
- Warning: 80% – 90%
- Critical: > 90%

**Network**
- Connected: Normal
- Disconnected: Critical
- Weak/Slow: Warning nếu:
  - Download < 100 KB/s trong 10s liên tục (moving average), hoặc
  - Không có traffic đáng kể trong 10s nhưng vẫn “Connected” (optional)

**Battery**
- Warning: < 20%
- Critical: < 10%

### 5.2 Visual status
- Dùng **badge + subtle glow** (không neon quá gắt)
- Màu gợi ý:
  - Normal: xanh
  - Warning: vàng/cam
  - Critical: đỏ
- Không dùng màu quá chói; ưu tiên “smart dark theme”

---

## 6) Smart UX Requirements (Quan trọng)
1) **Số không được giật liên tục**
   - Áp dụng smoothing: trung bình 3 mẫu gần nhất cho CPU/RAM/Net speed
2) **Cập nhật nhẹ**
   - Update interval: `1s – 2s` (khuyến nghị 2s)
3) **Tooltip thông minh**
   - Hover card → tooltip chi tiết ngắn gọn:
     - CPU: “Current usage”
     - RAM: “Used/Total”
     - Network: “Connected / Interface”
4) **Loading state đẹp**
   - Lần đầu load: dùng skeleton cards (không dùng spinner to giữa màn hình như hiện tại)
5) **Empty / Not supported**
   - Battery không có → fallback như mục 4.8
6) **Không hiển thị list app**
   - Dashboard chỉ snapshot
   - (Future) màn Running Apps để ở trang khác (không làm trong task này)

---

## 7) Style Guide (Smart UI)
- Dark theme hiện tại giữ lại nhưng **tối ưu typography & spacing**
- Card:
  - Border radius: 10–14px
  - Shadow nhẹ + border mỏng
  - Icon ở góc trái trên
  - Value font lớn (24–32)
  - Subtitle nhỏ (12–14)
  - Status badge nhỏ gọn (pill)
- Khoảng cách:
  - Padding card: 16–20
  - Gap grid: 12–16
- Tránh text dài; mọi thứ “nhìn là hiểu”

---

## 8) Acceptance Criteria (Checklist)
- [ ] Dashboard không còn chart
- [ ] Dashboard không còn table “Running Applications”
- [ ] Có grid cards đúng nhóm Core + Network + Battery
- [ ] Có status Normal/Warning/Critical theo rules
- [ ] Có skeleton loading cho cards
- [ ] Cập nhật realtime (1–2s) nhưng không giật (smoothing)
- [ ] Responsive khi resize cửa sổ (wrap hợp lý)
- [ ] UI tổng thể nhìn “smart, modern, clean” (không giống tool debug)

---

## 9) Out of Scope (KHÔNG làm trong task này)
- Trang chi tiết CPU/RAM theo timeline
- Danh sách process/app đang chạy dạng table
- Export log / analytics
- Settings nâng cao network/IP public

---

## 10) Gợi ý triển khai (tự do chọn)
- Python: `psutil` để lấy CPU/RAM/Disk/Network/Battery
- Network speed: tính từ `bytes_recv/sent` theo interval
- Uptime: từ boot time → format `xh ym`
- UI: Cards bằng QFrame/QWidget + QGridLayout
