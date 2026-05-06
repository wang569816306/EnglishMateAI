"""
视频下载工具类 - 基于yt-dlp
支持1800+平台视频解析和下载
"""
import os
import re
import shutil
from typing import Optional
import yt_dlp


def _find_ffmpeg_path() -> Optional[str]:
    """查找 ffmpeg 可执行文件路径"""
    # 先检查系统PATH中是否有ffmpeg
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return os.path.dirname(ffmpeg_path)
    
    # 检查常见安装位置
    common_paths = [
        "/usr/local/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
        "/usr/bin/ffmpeg",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return os.path.dirname(path)
    
    return None


class VideoDownloader:
    """yt-dlp 封装层，提供视频解析、下载、直链获取能力"""

    DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "downloads")

    def __init__(self):
        os.makedirs(self.DOWNLOAD_DIR, exist_ok=True)
        self.ffmpeg_path = _find_ffmpeg_path()
        self.has_ffmpeg = self.ffmpeg_path is not None
        
        if not self.has_ffmpeg:
            print("⚠️  警告: 未找到ffmpeg，某些视频格式可能无法合并")

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """清理文件名中的非法字符"""
        return re.sub(r'[\\/*?:"<>|]', "_", name)

    @staticmethod
    def _format_filesize(size: Optional[int]) -> str:
        """格式化文件大小"""
        if not size:
            return "未知大小"
        if size < 1024 * 1024:
            return f"{size / 1024:.0f}KB"
        if size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f}MB"
        return f"{size / (1024 * 1024 * 1024):.2f}GB"

    @staticmethod
    def _format_duration(seconds: Optional[int]) -> str:
        """格式化时长"""
        if not seconds:
            return "00:00"
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    def parse_video(self, url: str) -> dict:
        """解析视频信息，不下载文件"""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "noplaylist": True,
            "socket_timeout": 30,  # 设置超时时间为30秒
            "retries": 3,  # 重试次数
            "fragment_retries": 3,
        }
        
        # Bilibili 特殊配置
        if 'bilibili.com' in url or 'b23.tv' in url:
            ydl_opts.update({
                # Bilibili 可能需要 cookie，但公开视频通常不需要
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Referer": "https://www.bilibili.com/",
                },
            })
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            error_msg = str(e)
            # 提供更友好的错误提示
            if 'timed out' in error_msg.lower():
                raise ValueError(f"网络连接超时，请检查网络连接或稍后重试。如果是B站视频，可能需要科学上网环境。")
            elif 'No video formats found' in error_msg:
                raise ValueError(f"无法获取视频格式，该视频可能已删除、需要登录或设置了访问限制。请尝试其他视频链接。")
            elif 'bilibili' in error_msg.lower():
                raise ValueError(f"B站视频解析失败，可能是视频不存在或需要登录。错误: {error_msg[:100]}")
            elif 'Unsupported URL' in error_msg or 'No suitable extractor' in error_msg:
                raise ValueError(f"不支持的视频链接，请确保链接格式正确。支持的平台: YouTube, Bilibili, 抖音, TikTok等。")
            else:
                raise ValueError(f"无法解析该链接: {error_msg[:200]}")

        if not info:
            raise ValueError("无法解析该链接")

        formats = self._extract_formats(info)
        platform = info.get("extractor", info.get("extractor_key", "Unknown"))

        return {
            "id": info.get("id", ""),
            "title": info.get("title", "未知标题"),
            "thumbnail": info.get("thumbnail", ""),
            "duration": info.get("duration"),
            "duration_string": self._format_duration(info.get("duration")),
            "uploader": info.get("uploader", info.get("channel", "未知")),
            "platform": platform,
            "view_count": info.get("view_count"),
            "upload_date": info.get("upload_date", ""),
            "description": (info.get("description") or "")[:200],
            "formats": formats,
            "subtitles": list(info.get("subtitles", {}).keys()),
            "automatic_captions": list(info.get("automatic_captions", {}).keys())[:5],
        }

    def _extract_formats(self, info: dict) -> list:
        """从 yt-dlp info 中提取并整理可用格式"""
        raw_formats = info.get("formats", [])
        if not raw_formats:
            return []

        seen = set()
        results = []

        for f in raw_formats:
            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")
            height = f.get("height")
            ext = f.get("ext", "mp4")

            has_video = vcodec and vcodec != "none"
            has_audio = acodec and acodec != "none"

            if not has_video:
                continue

            resolution = f"{f.get('width', '?')}x{height}" if height else "未知"
            filesize = f.get("filesize") or f.get("filesize_approx")
            size_label = self._format_filesize(filesize)

            if has_audio:
                label = f"{height}p {ext.upper()} ({size_label})"
                key = (height, ext, "av")
            else:
                label = f"{height}p {ext.upper()} (仅视频, {size_label})"
                key = (height, ext, "v")

            if key in seen:
                continue
            seen.add(key)

            results.append({
                "format_id": f.get("format_id", ""),
                "ext": ext,
                "resolution": resolution,
                "height": height or 0,
                "filesize": filesize,
                "filesize_approx": filesize,
                "vcodec": vcodec,
                "acodec": acodec if has_audio else None,
                "has_audio": has_audio,
                "label": label,
            })

        # 按清晰度降序排序
        results.sort(key=lambda x: x["height"], reverse=True)

        # 如果没有音视频合并的格式，添加一个最佳合并选项
        if not any(r["has_audio"] for r in results) and results:
            best_video = results[0]
            merged = {
                **best_video,
                "format_id": f"bestvideo+bestaudio/best",
                "label": f"{best_video['height']}p 最佳 (视频+音频合并)",
                "has_audio": True,
                "acodec": "merged",
            }
            results.insert(0, merged)

        # 只返回前15个格式
        return results[:15]

    def download_video(self, url: str, format_id: str) -> dict:
        """下载视频到服务器临时目录，返回文件路径和元数据"""
        
        # 如果format_id是'best'或包含'best'，使用最佳可用格式
        if format_id == 'best' or 'best' in format_id:
            format_id = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        
        ydl_opts = {
            "format": format_id,
            "outtmpl": os.path.join(self.DOWNLOAD_DIR, "%(title)s.%(ext)s"),
            "quiet": False,  # 显示日志以便调试
            "no_warnings": False,
            "noplaylist": True,
            "socket_timeout": 60,  # 下载超时时间更长
            "retries": 5,  # 增加重试次数
            "fragment_retries": 5,
            "extractor_retries": 3,  # 提取器重试次数
        }

        # Bilibili 特殊配置
        if 'bilibili.com' in url or 'b23.tv' in url:
            ydl_opts["http_headers"] = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.bilibili.com/",
            }
            # B站可能需要更多的重试
            ydl_opts["retries"] = 8
            ydl_opts["fragment_retries"] = 8

        # 如果有ffmpeg，强制合并为mp4格式
        if self.has_ffmpeg:
            ydl_opts["ffmpeg_location"] = self.ffmpeg_path
            ydl_opts["merge_output_format"] = "mp4"
            ydl_opts["postprocessors"] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
        else:
            # 如果没有ffmpeg，优先选择mp4格式
            if '+' not in format_id:
                ydl_opts["format"] = f"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 下载错误: {error_msg}")  # 打印详细错误信息
            
            # 如果是“No video formats found”错误，尝试使用更宽松的格式选择
            if 'No video formats found' in error_msg:
                print("⚠️  尝试使用备用格式选择策略...")
                # 尝试使用最宽松的格式选择
                ydl_opts["format"] = "best"
                ydl_opts["retries"] = 3
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                except Exception as retry_error:
                    raise ValueError(f"下载失败: {str(retry_error)[:200]}")
            elif 'timed out' in error_msg.lower():
                raise ValueError(f"下载超时，请检查网络连接。大文件可能需要更长时间。")
            else:
                raise ValueError(f"下载失败: {error_msg[:200]}")

        if not info:
            raise ValueError("下载失败")

        title = self._sanitize_filename(info.get("title", "video"))
        
        # 确定最终文件名和扩展名
        ext = info.get("ext", "mp4")
        # 如果请求的是合并格式，强制使用mp4
        if '+' in format_id or self.has_ffmpeg:
            ext = "mp4"
        
        filename = f"{title}.{ext}"
        filepath = os.path.join(self.DOWNLOAD_DIR, filename)

        # 如果文件不存在，尝试其他可能的文件名
        if not os.path.exists(filepath):
            prepared = ydl.prepare_filename(info)
            if os.path.exists(prepared):
                filepath = prepared
                filename = os.path.basename(prepared)
                # 如果是m4s等格式，重命名为mp4
                if filename.endswith('.m4s'):
                    new_filepath = filepath[:-4] + '.mp4'
                    os.rename(filepath, new_filepath)
                    filepath = new_filepath
                    filename = os.path.basename(new_filepath)
            else:
                # 搜索包含标题的文件
                for f in os.listdir(self.DOWNLOAD_DIR):
                    if title in f:
                        filepath = os.path.join(self.DOWNLOAD_DIR, f)
                        filename = f
                        # 如果是m4s等格式，重命名为mp4
                        if filename.endswith('.m4s'):
                            new_filepath = filepath[:-4] + '.mp4'
                            os.rename(filepath, new_filepath)
                            filepath = new_filepath
                            filename = os.path.basename(new_filepath)
                        break

        return {
            "filepath": filepath,
            "filename": filename,
            "title": info.get("title", "video"),
            "ext": "mp4",  # 统一返回mp4
        }

    def get_direct_url(self, url: str, format_id: str) -> dict:
        """获取视频直链（用于前端直接下载）"""
        
        # 对于直链下载，优先选择MP4格式，避免返回m4s等分片格式
        # 如果用户选择了合并格式（包含+），则使用best格式
        if '+' in format_id:
            format_id = "best[ext=mp4]/best"
        elif format_id == 'best':
            format_id = "best[ext=mp4]/best"
        
        ydl_opts = {
            "format": format_id,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "socket_timeout": 30,
            "retries": 3,
        }

        # Bilibili 特殊配置
        if 'bilibili.com' in url or 'b23.tv' in url:
            ydl_opts["http_headers"] = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.bilibili.com/",
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            error_msg = str(e)
            if 'timed out' in error_msg.lower():
                raise ValueError(f"获取直链超时，请检查网络连接。")
            else:
                raise ValueError(f"无法获取直链: {error_msg[:200]}")

        if not info:
            raise ValueError("无法获取直链")

        direct_url = info.get("url")
        ext = info.get("ext", "mp4")
        
        # 如果是m4s等分片格式，尝试从 requested_formats 中查找MP4格式
        if ext in ['m4s', 'm4a', 'webm']:
            # 尝试从所有格式中找到MP4格式
            all_formats = info.get("formats", [])
            for fmt in all_formats:
                if fmt.get("ext") == "mp4" and fmt.get("vcodec") != "none":
                    direct_url = fmt.get("url")
                    ext = "mp4"
                    break
        
        # 如果仍然没有找到MP4，尝试requested_formats
        if not direct_url or ext in ['m4s', 'm4a']:
            requested = info.get("requested_formats")
            if requested and len(requested) > 0:
                # 优先找MP4格式
                for fmt in requested:
                    if fmt.get("ext") == "mp4":
                        direct_url = fmt.get("url")
                        ext = "mp4"
                        break
                # 如果还是没有，使用第一个
                if not direct_url:
                    direct_url = requested[0].get("url")
                    ext = requested[0].get("ext", "mp4")

        if not direct_url:
            raise ValueError("该视频不支持直链下载，请使用服务端下载模式")

        return {
            "direct_url": direct_url,
            "ext": ext,
            "filesize": info.get("filesize") or info.get("filesize_approx"),
            "title": info.get("title", "video"),
        }
