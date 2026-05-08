"""
视频下载管理器 - 负责下载限制、清理和监控
"""
import os
import time
import shutil
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.settings import settings


class DownloadManager:
    """管理视频下载的限流、清理和监控"""
    
    def __init__(self):
        self.download_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "downloads"))
        os.makedirs(self.download_dir, exist_ok=True)
        
        # 下载频率限制跟踪 {user_ip: [(timestamp, count)]}
        self.rate_limit_tracker: Dict[str, list] = defaultdict(list)
        
        # 并发下载跟踪 {user_ip: current_count}
        self.concurrent_downloads: Dict[str, int] = defaultdict(int)
        
    def check_rate_limit(self, user_ip: str) -> bool:
        """
        检查用户是否超过下载频率限制
        返回 True 表示允许下载，False 表示超限
        """
        now = time.time()
        window_start = now - 60  # 1分钟窗口
        
        # 清理过期记录
        self.rate_limit_tracker[user_ip] = [
            t for t in self.rate_limit_tracker[user_ip] if t > window_start
        ]
        
        # 检查是否超限
        if len(self.rate_limit_tracker[user_ip]) >= settings.DOWNLOAD_RATE_LIMIT_PER_MINUTE:
            return False
        
        # 记录本次请求
        self.rate_limit_tracker[user_ip].append(now)
        return True
    
    def get_rate_limit_remaining(self, user_ip: str) -> int:
        """获取用户剩余下载次数"""
        now = time.time()
        window_start = now - 60
        
        current_count = len([
            t for t in self.rate_limit_tracker[user_ip] if t > window_start
        ])
        
        return max(0, settings.DOWNLOAD_RATE_LIMIT_PER_MINUTE - current_count)
    
    def increment_concurrent(self, user_ip: str) -> bool:
        """
        增加并发下载计数
        返回 True 表示允许，False 表示超限
        """
        if self.concurrent_downloads[user_ip] >= settings.MAX_CONCURRENT_DOWNLOADS:
            return False
        
        self.concurrent_downloads[user_ip] += 1
        return True
    
    def decrement_concurrent(self, user_ip: str):
        """减少并发下载计数"""
        if self.concurrent_downloads[user_ip] > 0:
            self.concurrent_downloads[user_ip] -= 1
    
    def get_download_dir_size(self) -> int:
        """获取下载目录总大小（字节）"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.download_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    pass
        return total_size
    
    def get_download_dir_size_gb(self) -> float:
        """获取下载目录总大小（GB）"""
        return self.get_download_dir_size() / (1024 ** 3)
    
    def cleanup_old_files(self, expire_hours: Optional[int] = None) -> dict:
        """
        清理过期文件
        返回清理统计信息
        """
        if expire_hours is None:
            expire_hours = settings.DOWNLOAD_FILE_EXPIRE_HOURS
        
        now = time.time()
        expire_time = now - (expire_hours * 3600)
        
        cleaned_count = 0
        cleaned_size = 0
        failed_count = 0
        
        for filename in os.listdir(self.download_dir):
            filepath = os.path.join(self.download_dir, filename)
            
            if not os.path.isfile(filepath):
                continue
            
            try:
                file_mtime = os.path.getmtime(filepath)
                
                # 如果文件修改时间早于过期时间，删除
                if file_mtime < expire_time:
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    cleaned_count += 1
                    cleaned_size += file_size
            except Exception as e:
                print(f"⚠️  清理文件失败 {filename}: {e}")
                failed_count += 1
        
        return {
            "cleaned_count": cleaned_count,
            "cleaned_size_mb": cleaned_size / (1024 ** 2),
            "failed_count": failed_count
        }
    
    def cleanup_by_size_limit(self) -> dict:
        """
        按大小限制清理文件（删除最旧的文件直到目录大小符合要求）
        返回清理统计信息
        """
        max_size_bytes = settings.MAX_DOWNLOAD_DIR_SIZE_GB * (1024 ** 3)
        current_size = self.get_download_dir_size()
        
        if current_size <= max_size_bytes:
            return {"cleaned_count": 0, "cleaned_size_mb": 0, "reason": "未超出限制"}
        
        # 获取所有文件及其修改时间
        files = []
        for filename in os.listdir(self.download_dir):
            filepath = os.path.join(self.download_dir, filename)
            if os.path.isfile(filepath):
                try:
                    mtime = os.path.getmtime(filepath)
                    size = os.path.getsize(filepath)
                    files.append((filepath, filename, mtime, size))
                except (OSError, FileNotFoundError):
                    pass
        
        # 按修改时间排序（最旧的在前）
        files.sort(key=lambda x: x[2])
        
        cleaned_count = 0
        cleaned_size = 0
        
        # 删除最旧的文件直到满足大小限制
        for filepath, filename, mtime, size in files:
            if current_size <= max_size_bytes:
                break
            
            try:
                os.remove(filepath)
                cleaned_count += 1
                cleaned_size += size
                current_size -= size
            except Exception as e:
                print(f"⚠️  清理文件失败 {filename}: {e}")
        
        return {
            "cleaned_count": cleaned_count,
            "cleaned_size_mb": cleaned_size / (1024 ** 2),
            "reason": "超出大小限制"
        }
    
    def get_storage_stats(self) -> dict:
        """获取存储空间统计信息"""
        total_size = self.get_download_dir_size()
        max_size = settings.MAX_DOWNLOAD_DIR_SIZE_GB * (1024 ** 3)
        
        file_count = 0
        try:
            for filename in os.listdir(self.download_dir):
                filepath = os.path.join(self.download_dir, filename)
                if os.path.isfile(filepath):
                    file_count += 1
        except FileNotFoundError:
            print(f"⚠️  下载目录不存在: {self.download_dir}")
        
        return {
            "total_size_mb": total_size / (1024 ** 2),
            "total_size_gb": total_size / (1024 ** 3),
            "max_size_gb": settings.MAX_DOWNLOAD_DIR_SIZE_GB,
            "usage_percent": (total_size / max_size * 100) if max_size > 0 else 0,
            "file_count": file_count,
            "expire_hours": settings.DOWNLOAD_FILE_EXPIRE_HOURS
        }
    
    def auto_cleanup(self) -> dict:
        """
        自动清理：先按时间清理，再按大小清理
        返回清理结果
        """
        # 1. 先清理过期文件
        time_cleanup = self.cleanup_old_files()
        
        # 2. 如果仍然超出大小限制，按大小清理
        size_cleanup = self.cleanup_by_size_limit()
        
        return {
            "time_based_cleanup": time_cleanup,
            "size_based_cleanup": size_cleanup,
            "storage_stats": self.get_storage_stats()
        }


# 全局单例
download_manager = DownloadManager()
