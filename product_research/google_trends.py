'''
@Desc:   分析不同国家的搜索热度趋势
@Author: Dysin
@Time:   2025/9/17
'''

import sys
import os
import time

# 将项目根目录加入 Python 路径，方便跨目录导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px  # 用于绘制世界热力图

from source.utils.plot_config import PlotManager
from source.utils.paths import PathManager
from source.utils.proxy import *
from requests.exceptions import SSLError, ConnectionError

class GoogleTrendsManager:
    """
    Google Trends 数据抓取与可视化管理类
    - 支持时间序列趋势抓取
    - 支持区域兴趣度抓取
    - 支持趋势图与世界热力图绘制
    """

    def __init__(
        self,
        keywords: list,
        start_date: str,
        end_date: str,
        geo: str = ''
    ):
        self.paths = PathManager()
        self.keywords = keywords
        self.start_date = start_date
        self.end_date = end_date
        self.geo = geo
        self.proxy = clash_proxy("http")

    def safe_build_payload(self, keyword, retries=3, delay=3):
        """
        安全构建 payload，支持重试
        """
        requests_args = {'proxies': {'https': self.proxy}} if self.proxy else {}
        pytrends = TrendReq(hl='en-US', tz=360, requests_args=requests_args, timeout=(10,20))
        for attempt in range(1, retries + 1):
            try:
                print(f"[INFO] 构建 payload，关键词: {keyword}, 尝试: {attempt}")
                pytrends.build_payload(
                    [keyword],
                    timeframe=f"{self.start_date} {self.end_date}",
                    geo=self.geo
                )
            except (SSLError, ConnectionError) as e:
                print(f"[WARN] 构建失败: {e}, 等待 {delay}s 后重试...")
                time.sleep(delay)
        print("[ERROR] 构建 payload 失败，请检查代理或网络")
        return pytrends

    # ---------------- 时间趋势 ----------------
    def fetch_trends(
        self,
        regenerate: bool = True
    ) -> pd.DataFrame:
        """
        抓取 Google Trends 指定关键词兴趣数据并保存为 CSV
        支持多关键词多次抓取
        """
        csv_name = f"google_trends_{self.start_date.replace('-', '')}_{self.end_date.replace('-', '')}.csv"
        csv_path = self.paths.join_data_path(csv_name)

        # 删除已有 CSV 或加载
        if regenerate and os.path.exists(csv_path):
            os.remove(csv_path)
            print(f"已删除旧 CSV 文件 {csv_path}")
            trends_data = pd.DataFrame()
        elif os.path.exists(csv_path):
            trends_data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
            print(f"已加载旧 CSV 文件 {csv_path}")
        else:
            trends_data = pd.DataFrame()

        # 遍历关键词抓取
        for kw in self.keywords:
            pytrends = self.safe_build_payload(kw)
            pytrends.build_payload(
                [kw],
                timeframe=f"{self.start_date} {self.end_date}",
                geo=self.geo
            )
            data = pytrends.interest_over_time()

            if data.empty:
                print(f"关键词 '{kw}' 未获取到数据，跳过")
                continue

            if 'isPartial' in data.columns:
                data = data.drop(columns=['isPartial'])

            if trends_data.empty:
                trends_data = data[[kw]]
            else:
                trends_data[kw] = data[kw]

        # 保存 CSV
        trends_data.to_csv(csv_path)
        print(f"趋势数据已保存到 {csv_path}")
        return trends_data

    def plot_trends(self):
        """
        绘制时间趋势图
        """
        title = "Google Trends"
        file_name = f"google_trends_{self.start_date.replace('-', '')}_{self.end_date.replace('-', '')}"
        csv_name = file_name + '.csv'
        img_name = file_name + '.png'
        csv_path = self.paths.join_data_path(csv_name)
        if not os.path.exists(csv_path):
            print(f"CSV 文件 {csv_path} 不存在")
            return None
        df = pd.read_csv(csv_path, parse_dates=True)
        # 第一列转换为日期格式
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors="raise")
        y_columns = list(range(1, len(df.columns)))
        save_path = self.paths.join_image_path(img_name)
        plot_manager = PlotManager()
        plot_manager.plot_lines(
            df,
            y_columns=y_columns,
            x_column=0,
            x_label="Date",
            y_label="Interest",
            line_labels=[df.columns[i] for i in y_columns],
            title=title,
            save_path=save_path
        )

    # ---------------- 区域兴趣度 ----------------
    def fetch_region_interest(self, regenerate=True) -> pd.DataFrame:
        """
        获取全球或指定地区各国家兴趣度并保存 CSV
        """
        csv_name = f"google_region_{self.start_date.replace('-', '')}_{self.end_date.replace('-', '')}.csv"
        csv_path = self.paths.join_data_path(csv_name)

        # 删除已有 CSV 或加载
        if regenerate and os.path.exists(csv_path):
            os.remove(csv_path)
            print(f"已删除旧 CSV 文件 {csv_path}")
            region_data = pd.DataFrame()
        elif os.path.exists(csv_path):
            region_data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
            print(f"已加载旧 CSV 文件 {csv_path}")
        else:
            region_data = pd.DataFrame()

        for kw in self.keywords:
            pytrends = self.safe_build_payload(kw)
            pytrends.build_payload(
                [kw],
                timeframe=f"{self.start_date} {self.end_date}",
                geo=self.geo
            )
            data = pytrends.interest_by_region(
                resolution='COUNTRY',
                inc_low_vol=True,
                inc_geo_code=False
            )

            if data.empty:
                print(f"关键词 '{kw}' 未获取到数据，跳过")
                continue

            if 'isPartial' in data.columns:
                data = data.drop(columns=['isPartial'])

            if region_data.empty:
                region_data = data[[kw]]
            else:
                region_data[kw] = data[kw]

        # 保存 CSV
        region_data.to_csv(csv_path)
        print(f"趋势数据已保存到 {csv_path}")
        return region_data

    def load_latest_region_csv(self) -> pd.DataFrame:
        """
        读取最新区域兴趣度 CSV
        """
        files = [f for f in os.listdir(self.paths.get_data_dir())
                 if f.startswith("google_region_") and f.endswith(".csv")]
        if not files:
            print("未找到区域 CSV 文件")
            return None
        latest_file = max(files)
        return pd.read_csv(os.path.join(self.paths.get_data_dir(), latest_file))

    def plot_world_heatmap(
        self,
        save_name: str = "heatmap_google_trends.html"
    ):
        """
        绘制全球兴趣热力图
        """
        df = self.load_latest_region_csv()
        print(df)
        save_path = self.paths.join_image_path(save_name)

        plot_manager = PlotManager()
        plot_manager.plot_world_heatmap(
            df,
            country_column="geoName",
            value_column=1,
            save_path=save_path,
            color_scale='Reds',
            color_title='点击率'
        )


if __name__ == "__main__":
    # 配置关键词与时间
    keywords = ["dehumidifier"]
    start_date = "2023-01-01"
    end_date = "2025-07-01"

    google_trends = GoogleTrendsManager(
        keywords,
        start_date,
        end_date,
        geo=''
    )
    google_trends.fetch_trends(False)
    google_trends.plot_trends()
    google_trends.fetch_region_interest()
    google_trends.plot_world_heatmap()