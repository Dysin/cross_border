'''
@Desc:   Amazon爬虫
         调用库：
            (1) https://github.com/theonlyanil/amzpy
                AmzPy 是一个轻量级的 Python 库，用于从亚马逊抓取产品信息。它提供了一个简单的接口来获取产品详情，例如标题、价格、货币和图片 URL，同时使用 curl_cffi 自动处理反机器人措施，以增强安全性。
@Author: Dysin
@Time:   2025/9/22
'''

import csv
import json
import os.path
import pandas as pd
from amzpy import AmazonScraper
from source.utils.paths import PathManager
from source.utils.excel import Excel
from source.utils.images import ImageUtils

class AmazonUtils:
    def __init__(self):
        self.pm = PathManager()
        self.path_data = os.path.join(self.pm.data_dir, 'amazon_data')
        self.path_amazon_img = os.path.join(self.path_data, 'images')

    def search_by_query(
            self,
            country_code: str = 'com',
            query: str = None,
            max_pages: int = 2
    ):
        search_name = query.replace(' ', '_')
        print(search_name)
        file_name = f'amazon_products_{search_name}'
        file_csv = os.path.join(self.path_data, f'{file_name}.csv')
        file_json = os.path.join(self.path_data,f'{file_name}.json')
        # Create a scraper with configuration
        scraper = AmazonScraper(
            country_code=country_code,
            impersonate='chrome119'
        )
        # Method 1: Search for shoes on Amazon India
        print('\n--- Method 1: Enhanced Search by Keyword ---')
        print(f'Searching for: "{query}" on Amazon')
        # Search with 5 pages of results for demonstration
        products = scraper.search_products(query=query, max_pages=max_pages)
        # Display the enhanced results
        if products:
            print(f'\nFound {len(products)} products:')
            # 输出字段
            fields = [
                'asin',
                'title',
                'price',
                'currency',
                'rating',
                'reviews_count',
                'url',
                'img_url'
            ]
            # 写入 csv
            with open(file_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for item in products:
                    writer.writerow({
                        'asin': item.get('asin', ''),
                        'title': item.get('title', ''),
                        'price': item.get('price', ''),
                        'currency': item.get('currency', ''),
                        'rating': item.get('rating', ''),
                        'reviews_count': item.get('reviews_count', ''),
                        'url': item.get('url', ''),
                        'img_url': item.get('img_url', '')
                    })
            with open(file_json, "w") as f:
                json.dump(products, f, indent=2)
                print(f"\nFull search results saved to enhanced_search_results_by_url.json")

    def to_xlsx(self, csv_name):
        # 1. 读取 CSV
        file_csv = os.path.join(self.path_data, csv_name + '.csv')
        df = pd.read_csv(file_csv)
        # 2. 删除所有重复行
        df.drop_duplicates(keep=False, inplace=True)
        df = df.reset_index(drop=True)
        # 3. 排除 img_url 列
        df_new = df.drop(columns=['img_url'])
        # 4. 表头
        headers = [
            'asin',
            'title',
            'price',
            'currency',
            'rating',
            'reviews_count'
            'url',
            'image'
        ]
        # 5. 创建 Excel 工具
        excel_utils = Excel(
            path_target=self.path_data,
            name_target=csv_name,
            bool_new=True
        )
        excel_utils.insert_header(headers)
        # 6. 循环写入数据
        for i in range(len(df_new)):
            asin_value = df_new.iloc[i]['asin']  # 使用 iloc 按位置获取
            img_name = f'asin_{asin_value}'
            file_img = os.path.join(self.path_amazon_img, img_name + '.png')
            image_utils = ImageUtils(
                path_target=self.path_amazon_img,
                name_target=img_name
            )
            # image_utils.download(df.loc[i, 'img_url'])
            # 插入数据行
            data_row = df_new.iloc[i, :].tolist()
            excel_utils.insert_row_values(i + 2, data_row)
            # 插入图片
            excel_utils.insert_image(i + 2, len(headers), file_img)
        # 7. 保存 Excel
        excel_utils.save()

if __name__ == "__main__":
    # Uncomment the examples you want to run
    # example_config()
    # example_product_detail()
    # example_search_by_url("https://www.amazon.in/s?k=shoes+for+men&rh=n%3A1571283031%2Cp_6%3AA1WYWER0W24N8S&dc", max_pages=200)
    amazon_utils = AmazonUtils()
    amazon_utils.search_by_query(
        country_code='com.au',
        query='men sneakers size 9',
        max_pages=2
    )
    # amazon_utils.to_xlsx('amazon_products_mini_fan')