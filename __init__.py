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
from .schemas.xsc.redcaptcha import CaptchaXSC, CaptchaXSCV2
from .encrypt.xs_encrypt import XsEncrypt
from .encrypt.xsc_encrypt import XscEncrypt
from .encrypt.generate_local_id import generate_local_id, generate_web_id

__all__ = ['encrypt', 'xhs', 'XsEncrypt', 'code', 'CaptchaXSC', 'CaptchaXSCV2', 'XscEncrypt', 'generate_local_id', 'generate_web_id']


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
