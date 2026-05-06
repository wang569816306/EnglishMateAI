"""
视频下载API路由
提供视频解析、下载、直链获取等功能
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import os
import shutil
from app.services.video_downloader import VideoDownloader

router = APIRouter(tags=["视频下载"])

# 初始化视频下载器
video_downloader = VideoDownloader()


class VideoParseRequest(BaseModel):
    """视频解析请求"""
    url: str


class VideoDownloadRequest(BaseModel):
    """视频下载请求"""
    url: str
    format_id: str


class VideoDirectUrlRequest(BaseModel):
    """视频直链请求"""
    url: str
    format_id: str


@router.post("/parse")
async def parse_video(request: VideoParseRequest):
    """
    解析视频信息
    支持1800+平台：YouTube、Bilibili、抖音、TikTok等
    """
    try:
        # 验证URL格式
        if not request.url or not request.url.strip():
            raise HTTPException(status_code=400, detail="视频链接不能为空")
        
        # 解析视频
        video_info = video_downloader.parse_video(request.url)
        
        return {
            "code": 200,
            "message": "解析成功",
            "data": video_info
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.post("/download")
async def download_video(request: VideoDownloadRequest, background_tasks: BackgroundTasks):
    """
    下载视频到服务器
    返回文件路径，前端可通过/file接口下载
    """
    try:
        # 验证参数
        if not request.url or not request.url.strip():
            raise HTTPException(status_code=400, detail="视频链接不能为空")
        
        if not request.format_id:
            raise HTTPException(status_code=400, detail="请选择视频格式")
        
        # 下载视频
        result = video_downloader.download_video(request.url, request.format_id)
        
        # 生成下载URL
        filename = result["filename"]
        download_url = f"/api/v1/videos/file/{filename}"
        
        return {
            "code": 200,
            "message": "下载成功",
            "data": {
                "title": result["title"],
                "filename": filename,
                "ext": result["ext"],
                "download_url": download_url,
                "filepath": result["filepath"]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.post("/direct-url")
async def get_direct_url(request: VideoDirectUrlRequest):
    """
    获取视频直链
    前端可直接通过该链接下载，不经过服务器
    """
    try:
        # 验证参数
        if not request.url or not request.url.strip():
            raise HTTPException(status_code=400, detail="视频链接不能为空")
        
        if not request.format_id:
            raise HTTPException(status_code=400, detail="请选择视频格式")
        
        # 获取直链
        result = video_downloader.get_direct_url(request.url, request.format_id)
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取直链失败: {str(e)}")


@router.post("/proxy-download")
async def proxy_download(request: VideoDirectUrlRequest):
    """
    代理下载视频（通过后端转发，避免CORS和HTTP头问题）
    适合B站、YouTube等需要特殊HTTP头的平台
    """
    try:
        # 验证参数
        if not request.url or not request.url.strip():
            raise HTTPException(status_code=400, detail="视频链接不能为空")
        
        if not request.format_id:
            raise HTTPException(status_code=400, detail="请选择视频格式")
        
        # 对于B站视频，如果format_id不是'best'相关，先尝试解析并选择最佳格式
        format_id = request.format_id
        if 'bilibili.com' in request.url or 'b23.tv' in request.url:
            # 如果format_id包含+或者是best相关，保持原样
            if '+' not in format_id and 'best' not in format_id:
                # 对于B站，优先使用合并格式
                format_id = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        
        # 使用yt-dlp下载视频
        result = video_downloader.download_video(request.url, format_id)
        
        # 返回文件
        return FileResponse(
            path=result["filepath"],
            filename=result["filename"],
            media_type="video/mp4"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/file/{filename}")
async def download_file(filename: str):
    """
    下载已保存的视频文件
    """
    try:
        filepath = os.path.join(video_downloader.DOWNLOAD_DIR, filename)
        
        # 安全检查：防止目录遍历攻击
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        if not os.path.abspath(filepath).startswith(os.path.abspath(video_downloader.DOWNLOAD_DIR)):
            raise HTTPException(status_code=403, detail="非法访问")
        
        # 返回文件
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")


@router.get("/history")
async def get_download_history():
    """
    获取下载历史记录
    返回downloads目录下的所有文件
    """
    try:
        download_dir = video_downloader.DOWNLOAD_DIR
        
        if not os.path.exists(download_dir):
            return {
                "code": 200,
                "message": "成功",
                "data": []
            }
        
        files = []
        for filename in os.listdir(download_dir):
            filepath = os.path.join(download_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created_time": stat.st_ctime,
                    "modified_time": stat.st_mtime,
                    "download_url": f"/api/v1/videos/file/{filename}"
                })
        
        # 按修改时间降序排序
        files.sort(key=lambda x: x["modified_time"], reverse=True)
        
        return {
            "code": 200,
            "message": "成功",
            "data": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.delete("/file/{filename}")
async def delete_file(filename: str):
    """
    删除已下载的视频文件
    """
    try:
        filepath = os.path.join(video_downloader.DOWNLOAD_DIR, filename)
        
        # 安全检查
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        if not os.path.abspath(filepath).startswith(os.path.abspath(video_downloader.DOWNLOAD_DIR)):
            raise HTTPException(status_code=403, detail="非法访问")
        
        # 删除文件
        os.remove(filepath)
        
        return {
            "code": 200,
            "message": "删除成功",
            "data": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# 需要导入FileResponse
from fastapi.responses import FileResponse
