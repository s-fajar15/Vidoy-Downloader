"""
Vidoy Downloader
by s.fajar15

Created : 2026-07-20
Version : 1.0.0
"""

import os, re, subprocess, requests, time
from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Optional 
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import BarColumn, DownloadColumn, Progress, TimeRemainingColumn, TransferSpeedColumn

STREAM_URL = "https://vdy.to/stream.php"
USER_AGENT = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"
CHUNK_SIZE = 1024 * 1024

TITLE_PATTERN = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
POSTER_PATTERN = re.compile(r'poster=["\']([^"\']+)["\']', re.IGNORECASE)
SOURCE_PATTERN = re.compile(r'<source\s+src=["\']([^"\']+)["\']', re.IGNORECASE)
VIDEO_ID_PATTERN = re.compile(r'https?://([^/]+)/[ed]/([a-zA-Z0-9_-]+)')
STREAM_PATTERN = re.compile(r"embedToken\s*=\s*['\"]([^'\"]+)['\"]")

@dataclass
class DetailVideo:
    id_video: str
    name_host: str
    title: Optional[str] = None
    poster: Optional[str] = None
    url_cdn: Optional[str] = None

def get_user_headers(host):
	return {
		'host': host,
		'sec-ch-ua-mobile': '?1',
		'sec-ch-ua-platform': '"Android"',
		'upgrade-insecure-requests': '1',
		'user-agent': USER_AGENT,
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
		'sec-fetch-site': 'none',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-user': '?1',
		'sec-fetch-dest': 'document',
		'accept-language': 'id-ID,id;q=0.8',
	}

def get_meiva_headers(url):
    return {
        "Host": urlparse(url).hostname,
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Android"',
        "Accept-Encoding": "identity;q=1, *;q=0",
        "User-Agent": USER_AGENT,
        "sec-ch-ua-mobile": "?1",
        "Accept": "*/*",
        'Sec-GPC': '1',
        'Accept-Language': 'id-ID,id;q=0.8',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'no-cors',
        "Sec-Fetch-Dest": "video",
        'Sec-Fetch-Storage-Access': 'none',
        "Referer": url,
    }

def download_video(url, output):
    print(f"Memulai proses unduhan video ke {output}")

    url_lower = url.lower()

    if (
        url_lower.endswith(".m3u8")
        or ".m3u8?" in url_lower
        or "overfetch.video" in url_lower
    ):
        return download_hls(url, output)

    return download_direct(url, output)

def download_direct(url, output):
    headers = get_meiva_headers(url)

    try:
        head_req = requests.get(url, headers=headers, stream=True, timeout=15)
        total_size = int(head_req.headers.get("Content-Length", 0))
        head_req.close()
    except Exception as e:
        print(f"Gagal mendapatkan ukuran file: {e}")
        return False

    if total_size == 0:
        print("Ukuran file tidak terdeteksi oleh server CDN.")
        return False

    chunk_size = 1024 * 1024
    downloaded_size = os.path.getsize(output) if os.path.exists(output) else 0

    if downloaded_size >= total_size:
        print(f"Video sudah selesai diunduh: {output}")
        return True

    print(f"Memulai unduhan dengan mode Chunked Request (Target: {total_size} bytes)")

    with open(output, "ab" if downloaded_size > 0 else "wb") as file, Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    ) as progress:

        task = progress.add_task(
            f"Mengunduh: {os.path.basename(output)}",
            total=total_size,
            completed=downloaded_size
        )

        while downloaded_size < total_size:
            end_byte = min(downloaded_size + chunk_size - 1, total_size - 1)
            headers["Range"] = f"bytes={downloaded_size}-{end_byte}"

            try:
                response = requests.get(url, headers=headers, stream=True, timeout=30)
                response.raise_for_status()

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        progress.update(task, advance=len(chunk))

                response.close()

            except (requests.exceptions.RequestException, IOError) as e:
                print(f"\nRetry: {e}")
                time.sleep(2)

    print(f"\nVideo berhasil diunduh dan disimpan di: {output}")
    return True
    

def get_video_duration(url):
    headers = (
        f"User-Agent: {USER_AGENT}\r\n"
        f"Referer: https://vdy.to/\r\n"
        f"Origin: https://vdy.to\r\n"
    )

    command = [
        "ffprobe",
        "-v", "error",
        "-headers", headers,
        "-user_agent", USER_AGENT,
        "-protocol_whitelist", "file,http,https,tcp,tls,crypto",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        url,
    ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            print("FFprobe Error:")
            print(result.stderr)
            return None

        duration = result.stdout.strip()

        if duration:
            return float(duration)

        return None

    except Exception as e:
        print(f"FFprobe Exception: {e}")
        return None

def download_hls(url, output):
    print("Mendeteksi HLS M3U8")
    headers = (
        f"User-Agent: {USER_AGENT}\r\n"
        f"Referer: https://vdy.to/\r\n"
        f"Origin: https://vdy.to\r\n"
    )
    try:
        duration = get_video_duration(url)
        if duration is None or duration <= 0:
            print("Durasi tidak diketahui, melanjutkan proses...")
            duration = 100
            unknown_duration = True
        else:
            unknown_duration = False

        command = [
            "ffmpeg",
            "-y",
            "-headers", headers,
            "-user_agent", USER_AGENT,
            "-protocol_whitelist", "file,http,https,tcp,tls,crypto",
            "-i", url,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-c:a", "aac",
            "-movflags", "+faststart",
            "-progress", "pipe:1",
            "-nostats",
            output,
        ]
        print("Mengonversi video agar kompatibel...")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        with Progress("[progress.description]{task.description}", BarColumn(), "[progress.percentage]{task.percentage:>3.1f}%", "•", TransferSpeedColumn(), "•", TimeRemainingColumn()) as progress:
            task = progress.add_task(f"Memproses: {os.path.basename(output)}", total=duration)
            for line in process.stdout:
                line = line.strip()
                if not line.startswith("out_time_ms="):
                    continue
                try:
                    current_time = int(line.split("=",1)[1]) / 1_000_000
                    progress.update(task, completed=current_time % 100 if unknown_duration else min(current_time, duration))
                except (ValueError, IndexError):
                    pass

        process.wait()
        if process.returncode != 0:
            print("Gagal mengunduh HLS\n", process.stderr.read())
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
        response = requests.get(STREAM_URL, params=params, headers=headers)
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

        response = requests.get(url, headers=get_user_headers(host))
        response.raise_for_status()
        details = DetailVideo(id_video=video_id, name_host=host)

        stream_match = STREAM_PATTERN.search(response.text)
        if not stream_match:
            print("Stream token tidak ditemukan")
            return None

        print(f"\nMencari detail stream: {video_id}")
        stream = stream_detail(video_id, host, stream_match.group(1))
        print(stream[:3000])
        open('stream.html', 'w').write(stream)
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
