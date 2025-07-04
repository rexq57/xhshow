# 测试 generateLocalId 函数
# 提取相关代码并运行

import random
import time
import zlib
from enum import IntEnum

# 常量定义
CHARSET = "abcdefghijklmnopqrstuvwxyz1234567890"
LOCAL_ID_SECRET_VERSION = "0"

# PlatformCode 枚举
class PlatformCode(IntEnum):
    Windows = 0
    iOS = 1
    Android = 2
    MacOs = 3
    Linux = 4
    other = 5

# 生成随机字符串函数
def gen_random_string(length):
    return ''.join(random.choice(CHARSET) for _ in range(length))

# 获取平台代码函数
def get_platform_code(platform):
    platform_map = {
        "Android": PlatformCode.Android,
        "iOS": PlatformCode.iOS,
        "Mac OS": PlatformCode.MacOs,
        "Linux": PlatformCode.Linux,
    }
    return platform_map.get(platform, PlatformCode.other)

# CRC32 函数
def crc32(data):
    """计算字符串的CRC32值"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return zlib.crc32(data) & 0xffffffff

# 主要的 generateLocalId 函数
def generate_local_id(platform):
    platform_code = get_platform_code(platform)
    timestamp = hex(int(time.time() * 1000))[2:]  # 转换为16进制并去掉'0x'前缀
    random_string = gen_random_string(30)
    
    # 构建字符串: timestamp + randomString + platformCode + version + "000"
    base_string = timestamp + random_string + str(platform_code) + LOCAL_ID_SECRET_VERSION + "000"
    
    # 计算CRC32
    crc_value = crc32(base_string)
    
    # 最终结果: baseString + crc32值，截取前52位
    result = (base_string + str(crc_value))[:52]
    
    return result

if __name__ == "__main__":
    # 测试函数
    print("测试 generateLocalId 函数:")
    print("=" * 50)
    
    # 测试 iOS 平台
    print('调用 generate_local_id("iOS"):')
    ios_result = generate_local_id("iOS")
    print("结果:", ios_result)
    print("长度:", len(ios_result))
    
    print('\n再次调用 generate_local_id("iOS") (应该产生不同结果):')
    ios_result2 = generate_local_id("iOS")
    print("结果:", ios_result2)
    print("长度:", len(ios_result2))
    
    # 测试其他平台
    print("\n测试其他平台:")
    print("Android:", generate_local_id("Android"))
    print("Mac OS:", generate_local_id("Mac OS"))
    print("Linux:", generate_local_id("Linux"))
    print("Unknown:", generate_local_id("Unknown"))
    
    # 分析结果结构
    print("\n分析 iOS 结果结构:")
    timestamp = hex(int(time.time() * 1000))[2:]
    print(f"当前时间戳(16进制): {timestamp} (长度: {len(timestamp)})")
    print("随机字符串长度: 30")
    print("平台代码 iOS:", PlatformCode.iOS)
    print("版本号:", LOCAL_ID_SECRET_VERSION)
    print("固定后缀: 000")
