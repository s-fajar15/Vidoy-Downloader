"""
Vidoy Downloader
by s.fajar15

Created : 2026-07-20
Version : 1.0.0
"""

import os, re, subprocess, requests
from dataclasses import dataclass
from typing import Optional 
from rich.progress import BarColumn, DownloadColumn, Progress, TimeRemainingColumn, TransferSpeedColumn
STREAM_URL = "https://vdy.to/stream.php"
USER_AGENT = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"
CHUNK_SIZE = 1024 * 1024

TITLE_PATTERN = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
POSTER_PATTERN = re.compile(r'poster=["\']([^"\']+)["\']', re.IGNORECASE)
SOURCE_PATTERN = re.compile(r'<source\s+src=["\']([^"\']+)["\']', re.IGNORECASE)
VIDEO_ID_PATTERN = re.compile(r"https?://([^/]+)/d/([^/?#]+)")
STREAM_PATTERN = re.compile(r"embedToken\s*=\s*['\"]([^'\"]+)['\"]")

@dataclass
class DetailVideo:
    id_video: str
    name_host: str
    title: Optional[str] = None
    poster: Optional[str] = None
    url_cdn: Optional[str] = None

def get_user_headers():
    return {"User-Agent": USER_AGENT}

def get_meiva_headers(url):
    return {
        "Host": "meiva.overfetch.video",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Android"',
        "Accept-Encoding": "identity;q=1, *;q=0",
        "User-Agent": USER_AGENT,
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Brave";v="150"',
        "sec-ch-ua-mobile": "?1",
        "Accept": "*/*",
        "Sec-GPC": "1",
        "Accept-Language": "id-ID,id;q=0.6",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "video",
        "Referer": url,
    }

def download_video(url, output):
    print(f"Memulai proses unduhan video ke {output}")
    if "hls.overfetch.video" in url:
        return download_hls(url, output)
    return download_direct(url, output)

def download_direct(url, output):
    try:
        headers = get_meiva_headers(url)
        with requests.get(url, headers=headers, stream=True, timeout=30) as response:
            response.raise_for_status()
            file_size = int(response.headers.get("Content-Length", 0))
            if file_size == 0:
                print("Ukuran file tidak diketahui. Progress bar tidak dapat ditampilkan.")
                return False

            with open(output, "wb") as file, Progress(
                "[progress.description]{task.description}", BarColumn(),
                "[progress.percentage]{task.percentage:>3.1f}%", "•",
                DownloadColumn(), "•", TransferSpeedColumn(), "•", TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task(f"Mengunduh: {os.path.basename(output)}", total=file_size)
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        file.write(chunk)
                        progress.update(task, advance=len(chunk))

        print(f"Video berhasil diunduh dan disimpan di: {output}")
        return True
    except requests.exceptions.RequestException as error:
        print(f"Gagal unduh video: {error}")
        return False
    except IOError as error:
        print(f"Gagal menyimpan file video: {error}")
        return False
    except Exception as error:
        print(f"Exception: {error}")
        return False

def get_video_duration(url):
    try:
        command = [
            "ffprobe", "-v", "error", "-protocol_whitelist", "file,http,https,tcp,tls,crypto",
            "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", url,
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        duration = result.stdout.strip()
        return float(duration) if duration else 0
    except Exception:
        return 0

def download_hls(url, output):
    print("Mendeteksi HLS M3U8")
    try:
        duration = get_video_duration(url)
        if duration <= 0:
            print("Durasi video tidak ditemukan")
            return False

        command = [
            "ffmpeg", "-y", "-protocol_whitelist", "file,http,https,tcp,tls,crypto",
            "-i", url, "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac",
            "-movflags", "+faststart", "-progress", "pipe:1", "-nostats", output,
        ]
        print("Mengonversi video agar kompatibel...")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        with Progress(
            "[progress.description]{task.description}", BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%", "•",
            TransferSpeedColumn(), "•", TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task(f"Memproses: {os.path.basename(output)}", total=duration)
            for line in process.stdout:
                line = line.strip()
                if not line.startswith("out_time_ms="):
                    continue
                time_value = line.split("=", 1)[1]
                if time_value == "N/A":
                    continue
                try:
                    time_ms = int(time_value)
                    current_time = time_ms / 1_000_000
                    progress.update(task, completed=min(current_time, duration))
                except ValueError:
                    continue

        process.wait()
        if process.returncode != 0:
            error = process.stderr.read()
            print("Gagal mengunduh HLS\n", error)
            return False

        print(f"Video berhasil diunduh dan disimpan di: {output}")
        return True
    except FileNotFoundError:
        print("FFmpeg atau FFprobe belum terinstall")
        return False
    except Exception as error:
        print(f"Gagal HLS: {error}")
        return False

def stream_detail(video_id, host, stream_token):
    try:
        params = {"bucket": "vidoycdn", "id": video_id, "t": stream_token}
        headers = {"Host": host, "User-Agent": USER_AGENT, "Referer": f"https://{host}/"}
        response = requests.get(STREAM_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as error:
        print(f"Gagal mengambil detail stream: {error}")
        return None

def extract_video_data(url):
    print(f"\nMengambil konten dari URL: {url}")
    try:
        video_match = VIDEO_ID_PATTERN.search(url)
        if not video_match:
            print("Tidak dapat menemukan ID video atau Host Name dari URL.")
            return None

        host, video_id = video_match.groups()
        print(f"ID Video ditemukan: {video_id} | Host: {host}")

        response = requests.get(url, headers=get_user_headers(), timeout=30)
        response.raise_for_status()
        details = DetailVideo(id_video=video_id, name_host=host)

        stream_match = STREAM_PATTERN.search(response.text)
        if not stream_match:
            print("Stream token tidak ditemukan")
            return None

        print(f"\nMencari detail stream: {video_id}")
        stream = stream_detail(video_id, host, stream_match.group(1))
        if not stream:
            return None

        print("Mengekstrak judul, thumbnail, dan CDN URL")
        title_match = TITLE_PATTERN.search(stream)
        poster_match = POSTER_PATTERN.search(stream)
        source_match = SOURCE_PATTERN.search(stream)

        details.title = title_match.group(1).strip() if title_match else None
        details.poster = poster_match.group(1) if poster_match else None
        details.url_cdn = source_match.group(1) if source_match else None
        print("Proses Extract Selesai")
        return details
    except requests.exceptions.RequestException as error:
        print(f"Gagal mengambil data: {error}")
        return None
    except Exception as error:
        print(f"Error extract video: {error}")
        return None

def main():
    os.system("clear")
    print("Vidoy Downloader")
    url = input("Masukkan URL: ")
    detail = extract_video_data(url)

    if not detail:
        print("Gagal mengambil detail video")
        return

    print(f"\nHasil Video Dari ID: {detail.id_video}\nJudul: {detail.title}\nThumbnail: {detail.poster}\nURL CDN: {detail.url_cdn}\n")

    if not detail.url_cdn:
        print("Tidak dapat mengunduh karena URL CDN tidak ditemukan!")
        return

    output = f"{detail.id_video}.mp4"
    print(f"Mengunduh Video {output}")
    success = download_video(detail.url_cdn, output)

    if success:
        print(f"Unduhan {output} Berhasil.")
    else:
        print("Gagal mengunduh video. Periksa log atau koneksi Anda.")

if __name__ == "__main__":
    main()
