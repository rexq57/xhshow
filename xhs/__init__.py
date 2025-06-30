"""
XHShow XHS 模块

提供小红书API请求和数据处理功能。
"""

# 导出 request 子模块
from . import request

# 尝试导入主要的请求类
try:
    from .request.AsyncRequestFramework import AsyncRequestFramework
    from .request.auth import Authentication
    from .request.comments import Comments
    from .request.feeds import Feeds
    from .request.file import Uploader, FileType
    from .request.note import Notes, NoteType
    from .request.notifications import Notifications
    from .request.user import UserApi
    from .request.utils import Utils
    
    __all__ = [
        'request',
        'AsyncRequestFramework',
        'Authentication',
        'Comments', 
        'Feeds',
        'Uploader',
        'FileType',
        'Notes',
        'NoteType',
        'Notifications',
        'UserApi',
        'Utils'
    ]
except ImportError:
    # 如果导入失败，只导出 request 模块
    __all__ = ['request']
