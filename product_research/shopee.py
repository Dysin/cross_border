'''
@Desc:   
@Author: Dysin
@Time:   2025/9/22
'''

import requests
import csv
from typing import List, Dict


class ShopeeScraper:
    """
    Shopee 商品爬虫类 (基于非公开 JSON API)
    功能:
      - 根据关键词搜索商品
      - 获取商品ID, 店铺ID, 标题, 价格, 销量, 评分, 评价数
      - 支持翻页
      - 保存结果到CSV
    """

    def __init__(self, keyword: str, pages: int = 1):
        """
        初始化爬虫
        :param keyword: 搜索关键词 (例如 "drone")
        :param pages: 爬取的页数 (每页50条商品数据)
        """
        self.keyword = keyword
        self.pages = pages
        self.base_url = "https://shopee.com/api/v4/search/search_items"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          "AppleWebKit/537.36 (KHTML, like Gecko)"
                          "Chrome/140.0.0.0 Safari/537.36"
        }
        self.results: List[Dict] = []

    def scrape(self) -> List[Dict]:
        """
        执行爬取操作
        :return: 商品信息列表 (字典形式)
        """
        for page in range(self.pages):
            params = {
                "by": "relevancy",
                "keyword": self.keyword,
                "limit": 50,           # 每页最大50个
                "newest": page * 50    # 翻页偏移量
            }

            try:
                response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
                response.raise_for_status()
                data = response.json()

                for item in data.get("items", []):
                    info = item.get("item_basic", {})
                    self.results.append({
                        "itemid": info.get("itemid"),
                        "shopid": info.get("shopid"),
                        "title": info.get("name"),
                        "price": info.get("price", 0) / 100000,  # Shopee价格存储需要除以100000
                        "sold": info.get("historical_sold", 0),
                        "rating": info.get("item_rating", {}).get("rating_star", 0),
                        "rating_count": sum(info.get("item_rating", {}).get("rating_count", []))
                    })

            except Exception as e:
                print(f"第 {page+1} 页抓取失败: {e}")

        return self.results

    def save_to_csv(self, filename: str = None):
        """
        将爬取结果保存到CSV文件
        :param filename: 保存文件名 (默认为 'shopee_{keyword}.csv')
        """
        if not self.results:
            print("没有数据可保存，请先执行 scrape() 方法。")
            return

        if filename is None:
            filename = f"shopee_{self.keyword}.csv"

        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["itemid", "shopid", "title", "price", "sold", "rating", "rating_count"]
            )
            writer.writeheader()
            writer.writerows(self.results)

        print(f"数据已保存到 {filename}")


# ========== 使用示例 ==========
if __name__ == "__main__":
    scraper = ShopeeScraper(keyword="drone", pages=2)  # 搜索 "drone"，抓取2页
    products = scraper.scrape()
    print(f"共获取 {len(products)} 条商品数据")
    scraper.save_to_csv()
