# 测试 generateLocalId 函数
# 提取相关代码并运行

import random
import time
import zlib
import hashlib
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

# 计算webId函数
def generate_web_id(local_id):
    """
    根据localId计算webId
    webId = MD5(localId)
    """
    if isinstance(local_id, str):
        local_id = local_id.encode('utf-8')
    return hashlib.md5(local_id).hexdigest()

# 生成完整的ID对 (localId + webId)
def generate_id_pair(platform):
    """
    生成localId和webId的配对
    返回: (local_id, web_id)
    """
    local_id = generate_local_id(platform)
    web_id = generate_web_id(local_id)
    return local_id, web_id

if __name__ == "__main__":
    # 测试函数
    print("测试 generateLocalId 和 webId 生成:")
    print("=" * 60)
    
    # 测试 iOS 平台
    print('调用 generate_local_id("iOS"):')
    ios_local_id = generate_local_id("iOS")
    ios_web_id = generate_web_id(ios_local_id)
    print("localId:", ios_local_id)
    print("webId:  ", ios_web_id)
    print("localId长度:", len(ios_local_id))
    print("webId长度:  ", len(ios_web_id))
    
    print('\n再次调用 generate_id_pair("iOS") (应该产生不同结果):')
    ios_local_id2, ios_web_id2 = generate_id_pair("iOS")
    print("localId:", ios_local_id2)
    print("webId:  ", ios_web_id2)
    
    # 验证相同localId产生相同webId
    print("\n验证相同localId产生相同webId:")
    test_web_id = generate_web_id(ios_local_id)
    print("原始webId:", ios_web_id)
    print("验证webId:", test_web_id)
    print("是否相同:", ios_web_id == test_web_id)
    
    # 测试其他平台
    print("\n测试其他平台:")
    for platform in ["Android", "Mac OS", "Linux", "Unknown"]:
        local_id, web_id = generate_id_pair(platform)
        print(f"{platform:8}: localId={local_id}, webId={web_id}")
    
    # 分析结果结构
    print("\n分析结果结构:")
    timestamp = hex(int(time.time() * 1000))[2:]
    print(f"当前时间戳(16进制): {timestamp} (长度: {len(timestamp)})")
    print("随机字符串长度: 30")
    print("平台代码 iOS:", PlatformCode.iOS)
    print("版本号:", LOCAL_ID_SECRET_VERSION)
    print("固定后缀: 000")
    print("localId总长度: 52位")
    print("webId总长度: 32位 (MD5哈希)")
    
    # 提供独立的webId计算示例
    print("\n独立webId计算示例:")
    example_local_id = "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z"[:52]
    example_web_id = generate_web_id(example_local_id)
    print(f"示例localId: {example_local_id}")
    print(f"对应webId:   {example_web_id}")
