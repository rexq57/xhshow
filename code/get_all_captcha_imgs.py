import asyncio
import base64
import json
import time
import sys
import uuid
from xhshow.code.captcha import CaptchaSolver
from typing import Dict, List, Optional

from pyDes import ECB, PAD_PKCS5, des

from xhshow.encrypt import XsEncrypt
from xhshow.xhs.request.AsyncRequestFramework import AsyncRequestFramework


class ProxyProvider:
    def __init__(self):
        self.arf = AsyncRequestFramework()

    async def get_proxies(self) -> List[str]:
        """获取代理IP列表

        Returns:
            List[str]: 代理IP列表
        """
        proxy_url = "http://bapi.51daili.com/getapi2"
        params = {
            "linePoolIndex": -1,
            "packid": 2,
            "time": 5,
            "qty": 100,
            "port": 1,
            "format": "txt",
            "sep": "\\n",
            "dt": 1,
            "ct": 1,
            "usertype": 17,
            "uid": 50940,
            "accessName": "",
            "accessPassword": ""
        }

        response = await self.arf.send_http_request(
            url=proxy_url,
            method="GET",
            params=params,
            back_fun=True,
            auto_sign=False
        )
        content = await response.acontent()
        proxy_list = content.decode().strip().split("\n")
        return proxy_list


class CaptchaService:
    def __init__(self):
        self.arf = AsyncRequestFramework()
        self.solver = CaptchaSolver()

    async def get_captcha_info(self, 
                              proxy: Optional[str] = None,
                              captcha_version: str = "1.3.0",
                              verify_uuid: str = "",
                              verify_biz: str = "461",
                              biz: str = "",
                              source_site: str = "") -> Dict:
        """获取验证码信息

        Args:
            proxy: 代理地址(可选)
            captcha_version: 验证码版本 ("1.3.0" 或 "2.0.0")
            verify_uuid: 验证UUID (仅2.0.0版本需要)
            verify_biz: 验证业务类型 (默认461，2.0.0版本可能为471)
            biz: 业务标识 (仅2.0.0版本)
            source_site: 来源站点URL (仅2.0.0版本)

        Returns:
            Dict: 验证码信息
        """
        url = "http://edith.xiaohongshu.com/api/redcaptcha/v2/captcha/register"
        
        # 根据版本构建不同的payload
        if captcha_version == "2.0.0":
            payload = {
                "secretId": "000",
                "verifyType": "102",
                "verifyUuid": verify_uuid,
                "verifyBiz": verify_biz or "471",  # 2.0.0版本默认471
                "biz": biz,
                "sourceSite": source_site,
                "captchaVersion": "2.0.0"
            }
        else:  # 默认使用1.3.0版本
            payload = {
                "secretId": "000",
                "verifyType": "102",
                "verifyUuid": "",
                "verifyBiz": verify_biz or "461",  # 1.3.0版本默认461
                "sourceSite": "",
                "captchaVersion": "1.3.0"
            }

        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://www.xiaohongshu.com',
            'referer': 'https://www.xiaohongshu.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        ts = str(int(time.time() * 1000))
        headers['x-s'] = await XsEncrypt.encrypt_sign(
            ts=ts,
            payload=payload
        )
        headers['x-t'] = ts

        kwargs = {
            'url': url,
            'method': "POST",
            'json': payload,
            'headers': headers,
            'auto_sign': False
        }

        if proxy:
            kwargs['proxy'] = f"http://{proxy}"

        response = await self.arf.send_http_request(**kwargs)

        if not response:
            return {}

        captcha_info = json.loads(self.solver.decrypt_data(
            encoded_data=response['data']['captchaInfo']
        ))

        bg_tag = captcha_info['backgroundUrl'].split('/')[-1].split('.')[0]

        return {
            bg_tag: [
                captcha_info['backgroundUrl'],
                captcha_info['captchaUrl']
            ]
        }

    async def get_captcha_info_v2(self,
                                verify_uuid: str,
                                source_site: str,
                                proxy: Optional[str] = None,
                                verify_biz: str = "471",
                                biz: str = "") -> Dict:
        """获取验证码信息 (2.0.0版本的便捷方法)

        Args:
            verify_uuid: 验证UUID (必需)
            source_site: 来源站点URL (必需)
            proxy: 代理地址(可选)
            verify_biz: 验证业务类型 (默认471)
            biz: 业务标识 (默认为空)

        Returns:
            Dict: 验证码信息
        """
        return await self.get_captcha_info(
            proxy=proxy,
            captcha_version="2.0.0",
            verify_uuid=verify_uuid,
            verify_biz=verify_biz,
            biz=biz,
            source_site=source_site
        )
    
    async def get_captcha_info_v1(self, 
                                proxy: Optional[str] = None,
                                verify_biz: str = "461") -> Dict:
        """获取验证码信息 (1.3.0版本的便捷方法)

        Args:
            proxy: 代理地址(可选)
            verify_biz: 验证业务类型 (默认461)

        Returns:
            Dict: 验证码信息
        """
        return await self.get_captcha_info(
            proxy=proxy,
            captcha_version="1.3.0",
            verify_biz=verify_biz
        )


async def main(target_count: int = 100, 
               use_proxy: bool = False, 
               captcha_version: str = "1.3.0",
               verify_uuid: str = "",
               source_site: str = "") -> dict:
    """主函数

    Args:
        target_count: 目标请求数量
        use_proxy: 是否使用代理
        captcha_version: 验证码版本 ("1.3.0" 或 "2.0.0")
        verify_uuid: 验证UUID (2.0.0版本需要)
        source_site: 来源站点URL (2.0.0版本需要)

    Returns:
        Dict: 验证码信息字典
    """
    captcha_service = CaptchaService()

    if use_proxy:
        proxy_provider = ProxyProvider()
        proxy_list = await proxy_provider.get_proxies()
        # 如果代理数量不够，循环使用
        while len(proxy_list) < target_count:
            proxy_list.extend(proxy_list)
        proxy_list = proxy_list[:target_count]
    else:
        proxy_list = [None] * target_count

    # 根据版本构建不同的参数
    if captcha_version == "2.0.0":
        # 2.0.0版本需要verify_uuid和source_site
        if not verify_uuid:
            import uuid
            verify_uuid = str(uuid.uuid4())
        if not source_site:
            source_site = "https://edith.xiaohongshu.com/api/sns/v1/system_service/vfc_code?phone=94908551&type=login&zone=852"
        
        # 并发请求验证码 (v2.0.0)
        tasks = [captcha_service.get_captcha_info(
            proxy=proxy,
            captcha_version="2.0.0",
            verify_uuid=verify_uuid,
            verify_biz="471",
            biz="",
            source_site=source_site
        ) for proxy in proxy_list]
    else:
        # 1.3.0版本 (默认)
        tasks = [captcha_service.get_captcha_info(
            proxy=proxy,
            captcha_version="1.3.0"
        ) for proxy in proxy_list]
    results = await asyncio.gather(*tasks)

    # 合并结果
    captcha_dict = {}
    for result in results:
        if result:
            captcha_dict.update(result)

    return captcha_dict


if __name__ == "__main__":
    # 读取captcha_info.json
    existing_data = {}
    try:
        with open('captcha_info.json', 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        print("未找到现有文件，将创建新文件")

    # 根据操作系统设置事件循环策略
    if sys.platform == 'win32':
        try:
            from asyncio import WindowsSelectorEventLoopPolicy
            asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
        except ImportError:
            # 如果导入失败，使用默认策略
            pass
    else:
        # Linux 和 macOS 系统使用默认的事件循环策略
        # 在某些Linux发行版中可能需要特殊处理
        try:
            # 尝试获取当前事件循环，如果没有则创建新的
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # 如果获取失败，设置新的事件循环
            asyncio.set_event_loop(asyncio.new_event_loop())
    
    # 配置验证码版本和参数
    # 设置为 "2.0.0" 以使用新版本验证码API
    CAPTCHA_VERSION = "2.0.0"  # 可以改为 "2.0.0"
    
    if CAPTCHA_VERSION == "2.0.0":
        # v2.0.0 示例参数
        import uuid
        verify_uuid = str(uuid.uuid4())
        source_site = "https://edith.xiaohongshu.com/api/sns/v1/system_service/vfc_code?phone=94908551&type=login&zone=852"
        
        print(f"使用验证码版本: {CAPTCHA_VERSION}")
        print(f"验证UUID: {verify_uuid}")
        print(f"来源站点: {source_site}")
        
        new_result = asyncio.run(main(
            target_count=10, 
            use_proxy=False,
            captcha_version=CAPTCHA_VERSION,
            verify_uuid=verify_uuid,
            source_site=source_site
        ))
    else:
        # v1.3.0 (默认)
        print(f"使用验证码版本: {CAPTCHA_VERSION} (默认)")
        new_result = asyncio.run(main(
            target_count=10, 
            use_proxy=False,
            captcha_version=CAPTCHA_VERSION
        ))
    
    print(f"本次获取数据数量: {len(new_result)}")

    # 合并数据
    existing_data.update(new_result)
    print(f"合并后总数据数量: {len(existing_data)}")

    with open('captcha_info.json', 'w') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
