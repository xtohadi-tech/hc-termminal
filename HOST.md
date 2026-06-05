# HC Terminal — App Maintenance & Monitoring

## Ringkasan
HC Terminal adalah frontend statis yang di-hosting via GitHub Pages. Tidak ada backend khusus kecuali cronjob/reloader lokal di Hermes.

## Cek Kesehatan (Health Check)
- URL: `https://xtohadi-tech.github.io/hc-termminal/`
- Harus mengembalikan status `200` dan judul `HC Terminal Pro — Hotelier Crypto`.
- Jika gagal: cek GitHub Pages di repo Settings > Pages, pastikan branch `main` aktif.

## Watchdog
- Jika `initialScan()` gagal atau halaman menampilkan `Scan dulu` lebih dari 10 menit, restart service reloader lokal.
- Jika export CSV/JSON kosong, pastikan `buildRouteStrengthRows()` dan `buildBacktestRows()` terdefinisi.

## Monitoring
- Review GitHub Pages traffic di repo Insights setiap akhir minggu.
- Simpan log perubahan di `releases.md`.
- Catat error dari feedback user ke dalam file ini sebagai `Known Issues`.

## Rollback
- Gunakan commit sebelumnya jika update menimbulkan bug:
  - `git log --oneline -5`
  - `git revert <commit-hash>`
  - `git push origin main`
