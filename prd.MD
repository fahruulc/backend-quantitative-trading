Kamu adalah seorang Principal Product Manager dan Lead System Architect. Tugasmu adalah membuatkan Product Requirement Document (PRD) yang sangat komprehensif dan detail untuk proyek Hackathon "Market Intelligence System".

Berikut adalah konteks, batasan teknis, dan kebutuhan fitur proyek kami:

---

### 1. KONTEKS PROYEK & ARSITEKTUR REPO
- **Nama Folder/Struktur**:
  /program-fahrul
  ├── /frontend (Visual & Tampilan)
  └── /SectorApp (Backend & Implementasi Murni, disiapkan dengan Docker terpisah)
- **Kondisi Eksisting**: Website frontend saat ini sudah memiliki UI/UX yang sesuai tone, namun masih menggunakan data `dummy.json`.

---

### 2. BATASAN UTAMA (CRITICAL CONSTRAINTS)
- **Token API SectorApp**: Hanya dialokasikan **500 token** untuk seluruh hackathon (termasuk testing & demo).
- **Endpoint Mahal**: Panggilan `/api/v1/analysis/full-report` memakan **80 token/call**.
- **Solusi Arsitektur yang Diinginkan**:
  1. Strategi **Caching / Cron Job / Database pre-fetching**: Sistem meng-update data emiten pilihan/rekomendasi secara berkala ke database lokal/website.
  2. Integrasi Telegram Bot: Bot Telegram mengambil data dari DB lokal website, BUKAN memanggil API SectorApp langsung (kecuali jika ada permintaan emiten custom di luar list yang tersimpan).
  3. **Testing Mode / Mocking**: Fitur untuk demo dan pengujian tanpa mengurangi kuota API SectorApp.

---

### 3. FITUR KUNCI & SPESIFIKASI BISNIS
1. **Multi-Aspect Analytics**:
   - Technical Charting
   - Fundamental Analysis
   - Bandarmology Analysis
   - Heatmap Pergerakan Pasar / Sektor
2. **AI Anomaly Detection (Skripsi Integration)**:
   - Menggunakan model **Isolation Forest** (ground truth: Data IDX-UMA / Unusual Market Activity dari BEI).
   - Analisis di mana modul ini paling relevan memberikan *value added* pada sistem Market Intelligence (misal: Korelasi Anomaly Bandarmology vs. Price Action).
   - Output: Skor Anomali / Risk Score.
3. **Professional Scoring & Ranking System**:
   - Metode penilaian yang matematis dan berstandar Business Intelligence (misal: AHP / Analytic Hierarchy Process, Pearson Correlation, atau Multi-Criteria Decision Making).
4. **Navigation & Routing**:
   - Setiap menu/navbar memiliki *dedicated page* / *routed page* tersendiri (bukan modal serbaguna/single layout statis).

---

### 4. DOKUMEN PRD YANG DIBUTUHKAN (OUTPUT STRUCTURE)
Tolong susun PRD dalam format Markdown profesional yang mencakup:

1. **Executive Summary & System Architecture Diagram** (Deskripsikan alur data dari SectorApp -> DB -> Frontend/Telegram Bot).
2. **Detailed Feature Requirements**:
   - Modul Market Analytics (Chart, Fundamental, Bandarmology, Heatmap).
   - Modul AI Anomaly Detection (Integration Strategy, Ground Truth, Risk Score).
   - Modul Scoring & Ranking (Metodologi AHP / Pearson).
   - Modul Telegram Bot & Route Navigation.
3. **API Token Optimization Strategy**:
   - Rincian estimasi kalkulasi penggunaan API SectorApp (Budgeting Token).
   - Strategi Caching, Batch Fetching, dan Fallback mechanism.
   - Desain Mock/Testing Mode.
4. **Technical & Database Schema Recommendations** (Entity / Table structure utama).
5. **Future Roadmap / Planning Lanjutan** (Untuk pengembangan paska-hackathon).

Berikan analisis mendalam, realistis untuk kebutuhan lomba hackathon, dan langsung berikan PRD-nya.

note :
jika data murah atau bisa didapat dari sumber lain (yfinance dkk, gunakan itu). sector app hanya untuk data yang sulit / mahal