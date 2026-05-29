import yt_dlp
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs


class YouTubeService:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }

    def is_youtube_url(self, text: str) -> bool:
        """Check if text contains a YouTube URL."""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
        ]

        for pattern in youtube_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        parsed = urlparse(url)

        if parsed.hostname in ['youtube.com', 'www.youtube.com']:
            if parsed.path == '/watch':
                query = parse_qs(parsed.query)
                return query.get('v', [None])[0]
            elif parsed.path.startswith('/shorts/'):
                return parsed.path.split('/')[2]
            elif parsed.path.startswith('/embed/'):
                return parsed.path.split('/')[2]

        elif parsed.hostname == 'youtu.be':
            return parsed.path[1:]

        return None

    async def search_videos(self, query: str, limit: int = 10) -> List[Dict]:
        """Search YouTube videos."""
        search_query = f"ytsearch{limit}:{query}"

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(search_query, download=False)
                if 'entries' in info:
                    videos = []
                    for entry in info['entries']:
                        if entry:
                            videos.append({
                                'id': entry.get('id'),
                                'title': entry.get('title', 'بدون عنوان'),
                                'duration': entry.get('duration'),
                                'uploader': entry.get('uploader', 'ناشناس'),
                                'view_count': entry.get('view_count'),
                                'url': f"https://youtube.com/watch?v={entry.get('id')}",
                                'thumbnail': entry.get('thumbnail'),
                            })
                    return videos
            except Exception:
                pass

        return []

    async def get_video_info(self, url: str) -> Optional[Dict]:
        """Get video information and available formats."""
        video_id = self.extract_video_id(url)
        if not video_id:
            return None

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'format': 'best',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)

                # Extract available formats
                formats = []
                if 'formats' in info:
                    for fmt in info['formats']:
                        if fmt.get('ext') in ['mp4', 'webm', 'm4a', 'mp3']:
                            formats.append({
                                'format_id': fmt.get('format_id'),
                                'ext': fmt.get('ext'),
                                'resolution': fmt.get('resolution', 'N/A'),
                                'filesize': fmt.get('filesize'),
                                'quality': fmt.get('quality'),
                                'vcodec': fmt.get('vcodec'),
                                'acodec': fmt.get('acodec'),
                            })

                return {
                    'id': info.get('id'),
                    'title': info.get('title', 'بدون عنوان'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader', 'ناشناس'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail'),
                    'formats': formats,
                    'best_format': info.get('format_id'),
                }
            except Exception:
                return None

    async def get_download_url(self, url: str, format_id: str = 'best') -> Optional[str]:
        """Get direct download URL for a video."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': format_id,
            'forceurl': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return info.get('url')
            except Exception:
                return None


# Singleton instance
youtube_service = YouTubeService()
