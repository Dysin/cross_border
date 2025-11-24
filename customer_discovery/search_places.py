'''
@Desc:   搜索门店（坐标+关键词）
@Author: Dysin
@Time:   2025/9/13
'''

import googlemaps
import pandas as pd
import time
import re
import requests
from source.utils.paths import PathManager

# ========== 配置 ==========
API_KEY = "AIzaSyDzZnLKojUHcZekVS8GTzWEFiw5Ueq78Ws"   # 这里填你申请的 Google Cloud API Key
MAX_REQUESTS = 50                      # 限制 API 调用次数，避免超额计费
WAIT_TIME = 0.5                        # 每次请求间隔，降低速率限制
# =========================

client = googlemaps.Client(key=API_KEY)
request_count = 0  # 记录已调用的 API 次数

def extract_email_from_website(url):
    """
    从商家官网页面中提取邮箱
    :param url: 商家官网 URL
    :return: 邮箱字符串或 None
    """
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            html = response.text
            # 匹配常见邮箱格式
            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)
            if emails:
                return emails[0]  # 取第一个邮箱
    except Exception as e:
        print(f"爬取邮箱失败: {e}")
    return None


def search_and_save(keyword, location, radius=3000, output="results.csv"):
    """
    在指定坐标附近搜索门店，并保存到 CSV 文件
    :param keyword: 搜索关键词，例如 "vape shop"
    :param location: (lat, lng) 坐标，例如 (40.7128, -74.0060)
    :param radius: 搜索半径，单位：米
    :param output: 输出文件路径
    """
    global request_count
    results = []

    places = client.places_nearby(location=location, radius=radius, keyword=keyword)

    while places:
        for place in places.get("results", []):
            if request_count >= MAX_REQUESTS:
                print("达到 API 调用限制，停止搜索")
                break

            place_id = place.get("place_id")

            # 获取详情
            details = client.place(
                place_id=place_id,
                fields=[
                    "name", "formatted_address", "international_phone_number",
                    "geometry", "rating", "user_ratings_total", "website"
                ]
            )
            request_count += 1
            time.sleep(WAIT_TIME)

            print(f'[INFO] API调用次数：{request_count}')

            if "result" in details:
                info = details["result"]

                # 获取官网
                website = info.get("website")

                # 进一步爬官网邮箱
                email = extract_email_from_website(website) if website else None

                results.append({
                    "Name": info.get("name"),                                      # 店铺名称
                    "Address": info.get("formatted_address"),                      # 地址
                    "Phone": info.get("international_phone_number"),               # 电话
                    "Location": f"{info['geometry']['location']['lat']},{info['geometry']['location']['lng']}",  # 经纬度
                    "Rating": info.get("rating"),                                  # 平均评分
                    "UserRatingsTotal": info.get("user_ratings_total"),            # 评论数
                    "Website": website,                                            # 官网
                    "Email": email                                                 # 邮箱（爬取）
                })

        # 翻页
        if "next_page_token" in places:
            time.sleep(2)
            places = client.places_nearby(
                location=location,
                radius=radius,
                keyword=keyword,
                page_token=places["next_page_token"]
            )
        else:
            break

    df = pd.DataFrame(results)
    df.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"保存完成，共 {len(results)} 条 -> {output}")


if __name__ == "__main__":
    paths = PathManager()
    csv_path = paths.join_data_path('google_map_vape.csv')
    # 示例：在纽约曼哈顿附近搜索 3km 范围的 vape shop
    search_and_save("vape shop", (40.7128, -74.0060), 3000, output=csv_path)
