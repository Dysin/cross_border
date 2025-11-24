'''
@Desc:   Google Map 信息抓取
@Author: Dysin
@Time:   2025/9/13
'''

import googlemaps

import googlemaps
import time


class GoogleMapsClient:
    """
    Google Maps API 客户端封装
    支持搜索门店、调用次数限制
    """

    def __init__(self, api_key: str, max_calls: int = 100, cooldown: float = 1.0):
        """
        初始化
        :param api_key: Google Cloud API Key
        :param max_calls: 单次运行最大 API 调用次数，防止超额
        :param cooldown: 每次请求之间的冷却时间（秒），避免触发 QPS 限制
        """
        self.client = googlemaps.Client(key=api_key)
        self.max_calls = max_calls
        self.cooldown = cooldown
        self.call_count = 0  # 当前已调用次数

    def _check_limit(self):
        """
        检查是否超过调用次数限制
        """
        if self.call_count >= self.max_calls:
            raise RuntimeError(f"API 调用次数已达上限：{self.max_calls}")
        self.call_count += 1

    def search_places(self, keyword: str, location: tuple, radius: int = 5000):
        """
        搜索指定位置附近的门店
        :param keyword: 搜索关键词 (如 "vape shop")
        :param location: (lat, lon) 坐标
        :param radius: 搜索半径，单位米（最大 50000）
        :return: 搜索结果列表
        """
        self._check_limit()  # 检查调用次数

        results = self.client.places_nearby(
            location=location,
            radius=radius,
            keyword=keyword
        )

        time.sleep(self.cooldown)  # 延迟，避免请求过快
        return results.get("results", [])

