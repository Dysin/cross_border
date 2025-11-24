'''
@Desc:   汇率获取与转换工具，支持人民币 (CNY) 与外币相互转换
         实时汇率网址：
         1.ExchangeRate-API，支持 160 多种货币，https://www.exchangerate-api.com/?utm_source
         2.CurrencyAPI.com，免费额度 + 实时更新，简单易用，https://currencyapi.com/?utm_source
@Author: Dysin
@Time:   2025/9/16
@Email:  dysinqiu@163.com
'''
import os
import requests
import pandas as pd
from typing import Optional

# 从环境变量读取 API Key（推荐做法）
exchange_api_key = os.getenv("EXCHANGE_RATE_API_KEY", "49fd6c05ddce9d3a359410f1")

class ExchangeRateManager:
    def __init__(self, api_key: str = exchange_api_key, csv_path: str = "exchange_rates.csv"):
        """
        汇率管理器，基于 ExchangeRate-API
        :param api_key: 在 https://www.exchangerate-api.com/ 注册获取的 API key
        :param csv_path: 本地存储汇率的 CSV 文件路径
        """
        self.api_key = api_key
        self.csv_path = csv_path
        self.base_currency = "CNY"  # 固定人民币作为基准

    def fetch_rates(self) -> Optional[pd.DataFrame]:
        """
        从 ExchangeRate-API 拉取实时汇率（对人民币）
        :return: 汇率 DataFrame 或 None
        """
        try:
            url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/{self.base_currency}"
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()

            if "conversion_rates" not in data:
                print("[Error] API返回数据不完整")
                return None

            rates = data["conversion_rates"]
            df = pd.DataFrame(rates.items(), columns=["Currency", "Rate"])
            return df

        except Exception as e:
            print(f"[Error] 获取汇率失败: {e}")
            return None

    def save_rates(self, df: pd.DataFrame):
        """保存汇率到CSV"""
        df.to_csv(self.csv_path, index=False, encoding="utf-8-sig")
        print(f"[Info] 汇率已保存到 {self.csv_path}")

    def load_rates(self) -> Optional[pd.DataFrame]:
        """从CSV读取汇率"""
        if not os.path.exists(self.csv_path):
            print("[Error] CSV文件不存在，请先调用 fetch_rates 保存数据")
            return None
        return pd.read_csv(self.csv_path)

    def convert_to_cny(self, amount: float, currency: str) -> Optional[float]:
        """
        将外币转换成人民币
        :param amount: 金额
        :param currency: 外币币种 (USD, EUR...)
        :return: 人民币金额
        """
        df = self.load_rates()
        if df is None:
            return None

        rate_row = df[df["Currency"] == currency.upper()]
        if rate_row.empty:
            print(f"[Error] 不支持的币种: {currency}")
            return None

        rate = float(rate_row["Rate"].values[0])
        return amount / rate  # 因为基准是 CNY，所以外币->CNY = 金额 / 汇率

    def convert_from_cny(self, amount: float, currency: str) -> Optional[float]:
        """
        将人民币转换为外币
        :param amount: 人民币金额
        :param currency: 外币币种 (USD, EUR...)
        :return: 外币金额
        """
        df = self.load_rates()
        if df is None:
            return None

        rate_row = df[df["Currency"] == currency.upper()]
        if rate_row.empty:
            print(f"[Error] 不支持的币种: {currency}")
            return None

        rate = float(rate_row["Rate"].values[0])
        return amount * rate


if __name__ == "__main__":
    # 是否获取汇率
    bool_get_rates = False

    manager = ExchangeRateManager()

    # 第一次运行时拉取最新汇率并保存
    if bool_get_rates:
        df_rates = manager.fetch_rates()
        if df_rates is not None:
            manager.save_rates(df_rates)

    # 示例：读取并转换
    df_loaded = manager.load_rates()
    if df_loaded is not None:
        print(df_loaded.head())

        print("100 USD = ", manager.convert_to_cny(100, "USD"), "CNY")
        print("1000 CNY = ", manager.convert_from_cny(1000, "USD"), "USD")
