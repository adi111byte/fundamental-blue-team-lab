# Blue Team Triage Lab (Ringkasan Bahasa Indonesia)

Repo ini berisi beberapa case investigasi insiden yang saya kerjakan di home lab sendiri, dengan pfSense sebagai firewall/router di tengah jaringan. Tiap case didokumentasikan dari deteksi sampai kesimpulan, lengkap dengan detection rule dan script kecil yang saya pakai.

## Kenapa repo ini dibuat

Saya ingin portofolio yang menunjukkan cara saya benar benar melakukan triage insiden, bukan sekadar daftar tools yang pernah diinstal. Semua case mengikuti proses yang sama (lihat `docs/triage-sop.md`) supaya cara berpikirnya konsisten di tiap jenis serangan.

## Lab

pfSense berjalan sebagai router/firewall antara VM attacker dan VM target di VirtualBox. Detail topologi dan cara reproduksi ada di `docs/lab-setup.md`.

## Daftar Case

| Case | Jenis Serangan | Metode Deteksi | Status |
|---|---|---|---|
| case-01-port-scan | Nmap port scan | Suricata (pfSense) | Berjalan |
| case-02-ssh-bruteforce | SSH brute force | auth.log + script Python | Berjalan |
| case-03-dns-phishing | Domain phishing | Review header manual + script cek reputasi domain | Berjalan |

Konten teknis lengkap ditulis dalam bahasa Inggris di README utama dan tiap folder case, supaya bisa dibaca reviewer internasional juga.

Kontak: adirmadhani@gmail.com
