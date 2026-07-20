# 🎬 Vidoy Downloader

```{=html}
<p align="center">
```
`<b>`{=html}Fast, Lightweight & Smart Video Downloader`</b>`{=html}
```{=html}
</p>
```
```{=html}
<p align="center">
```
`<img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python">`{=html}
`<img src="https://img.shields.io/badge/FFmpeg-Required-green?style=for-the-badge&logo=ffmpeg">`{=html}
`<img src="https://img.shields.io/badge/Platform-Termux%20%7C%20Linux-lightgrey?style=for-the-badge">`{=html}
```{=html}
</p>
```
```{=html}
<p align="center">
```
`<b>`{=html}Vidoy Downloader`</b>`{=html} adalah downloader video
berbasis CLI yang dibuat menggunakan Python. Project ini mampu
mendeteksi CDN video secara otomatis dan memilih metode download yang
sesuai.
```{=html}
</p>
```

------------------------------------------------------------------------

## ✨ Features

-   🚀 Extract video secara otomatis
-   🆔 Automatic video ID detection
-   📝 Extract video title
-   🖼️ Extract thumbnail / poster
-   🔗 Automatic CDN detection
-   📡 Support `meiva.overfetch.video`
-   🎞️ Support HLS `.m3u8`
-   ⚡ Fast direct download
-   📊 Real-time progress bar
-   🔄 HLS video conversion
-   📱 Android-friendly output
-   🎬 H.264 + AAC compatibility
-   🧹 Clean & lightweight CLI

------------------------------------------------------------------------

## 🧠 Smart CDN Detection

Vidoy Downloader secara otomatis mendeteksi jenis CDN yang digunakan
oleh video.

### Direct CDN

``` text
meiva.overfetch.video
```

Downloader akan menggunakan `requests` untuk mengunduh video secara
langsung.

### HLS CDN

``` text
hls.overfetch.video
```

Downloader akan menggunakan FFmpeg untuk memproses playlist `.m3u8`.

Tidak perlu memilih metode download secara manual.

------------------------------------------------------------------------

## 🔄 Workflow

``` text
┌──────────────────┐
│   Video URL      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Extract Video ID │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Extract Stream   │
│ Token            │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Detect CDN       │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────────┐
│ Meiva  │ │ HLS M3U8  │
└───┬────┘ └─────┬──────┘
    │            │
    ▼            ▼
Requests      FFmpeg
    │            │
    └──────┬─────┘
           ▼
     ┌───────────┐
     │  MP4 File │
     └───────────┘
```

------------------------------------------------------------------------

## 📦 Requirements

Sebelum menjalankan project, pastikan sudah menginstall:

-   Python `3.8+`
-   FFmpeg
-   FFprobe

### Python Packages

``` bash
pip install requests rich
```

------------------------------------------------------------------------

## 🛠️ Installation

Clone repository:

``` bash
git clone https://github.com/USERNAME/vidoy-downloader.git
```

Masuk ke folder project:

``` bash
cd vidoy-downloader
```

Install dependency:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## 📱 Termux Android

Install FFmpeg melalui Termux:

``` bash
pkg update
pkg upgrade
pkg install ffmpeg
```

Cek instalasi:

``` bash
ffmpeg -version
```

``` bash
ffprobe -version
```

Jika versi FFmpeg dan FFprobe muncul, berarti instalasi berhasil.

------------------------------------------------------------------------

## 🚀 Usage

Jalankan program:

``` bash
python main.py
```

Masukkan URL video:

``` text
Masukkan URL: https://vdy.to/d/xxxxxxxx
```

Program akan memproses video secara otomatis.

### Example

``` text
Vidoy Downloader

Masukkan URL: https://vdy.to/d/xxxxxxxx

ID Video ditemukan: xxxxxxxx | Host: vdy.to

Mencari detail stream...

Mengekstrak judul, thumbnail, dan CDN URL

Proses Extract Selesai

Mengunduh Video xxxxxxxx.mp4

Mendeteksi HLS M3U8
Mengonversi video agar kompatibel...

Memproses: xxxxxxxx.mp4
━━━━━━━━━━━━━━━━━━━━━━━ 100.0%

Video berhasil diunduh dan disimpan di: xxxxxxxx.mp4
```

------------------------------------------------------------------------

## 📁 Project Structure

``` text
vidoy-downloader/
│
├── main.py
├── requirements.txt
└── README.md
```

------------------------------------------------------------------------

## 📄 requirements.txt

``` txt
requests
rich
```

------------------------------------------------------------------------

## 🎞️ HLS Conversion

Untuk video HLS, Vidoy Downloader menggunakan:

  Component     Value
  ------------- -----------
  Video Codec   H.264
  Audio Codec   AAC
  Preset        Very Fast
  Container     MP4

Konversi ini bertujuan agar video lebih kompatibel dengan berbagai media
player, khususnya Android.

------------------------------------------------------------------------

## ⚠️ Disclaimer

> Project ini dibuat untuk tujuan edukasi dan penggunaan pribadi.

Pastikan kamu memiliki hak atau izin untuk mengunduh konten yang
diproses menggunakan aplikasi ini.

Developer tidak bertanggung jawab atas penyalahgunaan project ini.

------------------------------------------------------------------------

## 👨‍💻 Author

```{=html}
<p align="center">
```
Made with 🐍 Python
```{=html}
</p>
```
```{=html}
<p align="center">
```
`<b>`{=html}Vidoy Downloader`</b>`{=html}
```{=html}
</p>
```
