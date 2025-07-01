"""
XHShow - 小红书数据提取和处理工具包

这个包提供了小红书相关的加密、API调用和数据处理功能。
"""

__version__ = "0.1.0"
__author__ = "rexq57"
__description__ = "XiaoHongShu data extraction and processing tools"

# 导出主要模块 - 临时只导出基础模块
from . import encrypt
from . import xhs
from . import code

# 导出常用类和函数
try:
    from .encrypt.xs_encrypt import XsEncrypt
    __all__ = ['encrypt', 'xhs', 'XsEncrypt', 'code']
except ImportError:
    # 如果导入失败，只导出模块
    __all__ = ['encrypt', 'xhs', 'code']

__all__ = []

def get_version():
    """获取版本信息"""
    return __version__

def get_info():
    """获取包信息"""
    return {
        "name": "xhshow",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "modules": ["encrypt", "xhs"]
    }
