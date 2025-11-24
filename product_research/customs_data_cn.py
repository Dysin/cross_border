'''
@Desc:   海关统计数据分析
         1.数据来源
         (1) 官方海关网站：
             中国海关总署：http://www.customs.gov.cn/
             中国海关总署 | 海关统计数据在线查询平台：http://stats.customs.gov.cn/
             数据类型：进出口总值、品类明细、按国家/地区分类
             格式：HTML 表格、PDF 报表、Excel
         (2) 海关数据开放平台/第三方
             如：CEIC、阿里数据、Wind 等（部分付费）
             数据格式：Excel/CSV/API
         (3) UN Comtrade Database
             网址：https://comtradeplus.un.org/
             API：https://comtradedeveloper.un.org/
@Author: Dysin
@Time:   2025/9/18
'''

import os
import sys
import pandas as pd
from source.utils.paths import PathManager
from source.utils.plot_config import PlotManager

# 将项目根目录加入 Python 路径，方便跨目录导入
sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))

class CustomsDataAnalyzer:
    """
    海关数据分析类
    用于读取、清洗并进行多维度的出口数据分析
    """

    def __init__(self, file_name: str):
        """
        初始化类，读取并清洗数据
        :param file_name: str, CSV 文件名
        """
        self.file_name = file_name
        self.paths = PathManager()
        self.plt_manager = PlotManager()
        self.df = self._load_and_clean_data()

    # ================== 基础分析 ==================

    def _load_and_clean_data(self) -> pd.DataFrame:
        """
        读取并清洗数据
        - 自动尝试 UTF-8 / GBK 解码
        - 去除千分位符
        - 转换为数值
        """
        encodings = ["utf-8", "gbk"]

        csv_name = self.file_name + '.csv'
        csv_file = os.path.join(self.paths.data_dir, 'customs_data_cn', csv_name)

        for enc in encodings:
            try:
                df = pd.read_csv(csv_file, encoding=enc)
                print(f"[INFO] 成功读取文件: {csv_file} (编码: {enc})")
                break
            except Exception as e:
                print(f"[WARN] 尝试编码 {enc} 失败: {e}")
        else:
            raise ValueError(f"[ERROR] 无法读取文件: {csv_file}")

        # 清洗数值列
        if "人民币" in df.columns:
            df["人民币"] = (
                df["人民币"]
                .astype(str)
                .str.replace(",", "", regex=False)
                .astype(float)
            )
        return df

    # ========== 分析方法（全部返回 DataFrame） ==========

    @staticmethod
    def total_export(df) -> float:
        """计算总出口额"""
        return df['人民币'].sum()

    @staticmethod
    def trade_by_country(df) -> pd.DataFrame:
        """按国家统计出口金额"""
        return df.groupby("贸易伙伴名称")["人民币"].sum().reset_index()

    @staticmethod
    def trade_by_province(df) -> pd.DataFrame:
        """按注册地省份统计出口金额"""
        return df.groupby("注册地名称")["人民币"].sum().reset_index()

    @staticmethod
    def trade_by_month(df) -> pd.DataFrame:
        """按年月统计出口金额"""
        return df.groupby("数据年月")["人民币"].sum().reset_index()

    @staticmethod
    def trade_by_mode(df) -> pd.DataFrame:
        """按贸易方式统计出口金额"""
        return df.groupby("贸易方式名称")["人民币"].sum().reset_index()

    def trade_by_product(self) -> pd.DataFrame:
        """按商品统计出口金额"""
        return self.df.groupby("商品名称")["人民币"].sum().reset_index()

    def split_by_product(self) -> dict:
        """
        按商品名称拆分 DataFrame
        :return: dict，key=商品名称，value=对应的 DataFrame
        """
        if "商品名称" not in self.df.columns:
            raise ValueError("DataFrame 必须包含 '商品名称' 列")
        product_groups = {}
        for product_name, group in self.df.groupby("商品名称"):
            product_groups[product_name] = group.reset_index(drop=True)
        return product_groups

    @staticmethod
    def trade_by_month_country(df) -> pd.DataFrame:
        """
        按年月统计出口金额，并按国家区分，输出整理好的 DataFrame
        :return: DataFrame, 第一列为时间，第二列开始为不同国家对应的出口额
        """
        df = df.pivot_table(
            index='数据年月',
            columns='贸易伙伴名称',
            values='人民币',
            aggfunc='sum',
            fill_value=0
        ).reset_index()  # 重置索引，让时间成为第一列
        return df

    # ================== 数据分析 ==================

    def plot_country(self, df, img_name):
        # 按国家
        df_country = self.trade_by_country(df)
        # 假设对 "人民币" 这一列按从大到小排序
        df_country_sorted = df_country.sort_values(by="人民币", ascending=False)
        # 取前 20 行
        df_top_country = df_country_sorted.head(20)
        top_countries = df_top_country['贸易伙伴名称'].tolist()
        self.plt_manager.plot_bars(
            df_top_country,
            y_columns=1,
            title='Top 20 出口目的地',
            x_label='国家/地区',
            y_label='出口额（CNY）',
            save_path=self.paths.join_image_path(f'{img_name}_country.png'),
            rotate_xticks=15,
            figure_size=[16, 7]
        )
        return top_countries

    def plot_province(self, df, img_name):
        # 按省份
        df_province = self.trade_by_province(df)
        # 假设对 "人民币" 这一列按从大到小排序
        df_province_sorted = df_province.sort_values(by="人民币", ascending=False)
        self.plt_manager.plot_bars(
            df_province_sorted,
            y_columns=1,
            title='主要出口省份',
            x_label='省份',
            y_label='出口额（CNY）',
            save_path=self.paths.join_image_path(f'{img_name}_province.png'),
            rotate_xticks=20,
            annotate=True,
            number_format='sci',
            precision=1,
            figure_size=[16, 7]
        )

    def plot_mode(self, df, img_name):
        # 按贸易方式
        df_mode = self.trade_by_mode(df)
        # 假设对 "人民币" 这一列按从大到小排序
        df_mode_sorted = df_mode.sort_values(by="人民币", ascending=False)
        self.plt_manager.plot_bars(
            df_mode_sorted,
            y_columns=1,
            title='出口方式占比',
            x_label='贸易方式',
            y_label='出口额（CNY）',
            save_path=self.paths.join_image_path(f'{img_name}_mode.png'),
            rotate_xticks=0,
            figure_size=[16, 9]
        )

    def plot_product(self, img_name):
        """
        根据商品类别柱状图
        :param img_name: 图片名
        :return:
        """
        # 按商品类别
        df_product = self.trade_by_product()
        # 假设对 "人民币" 这一列按从大到小排序
        df_product_sorted = df_product.sort_values(by="人民币", ascending=False)
        self.plt_manager.plot_bars(
            df_product_sorted,
            y_columns=1,
            title='商品类别占比',
            x_label='商品',
            y_label='出口额（CNY）',
            save_path=self.paths.join_image_path(f'{img_name}_product.png'),
            rotate_xticks=20,
            figure_size=[16, 9]
        )

    def plot_month(self, df, img_name):
        # 按时间
        df_month = self.trade_by_month(df)
        # 第一列转换为str
        df_month["数据年月"] = pd.to_datetime(df_month["数据年月"], format="%Y%m")
        self.plt_manager.plot_lines(
            df_month,
            y_columns=1,
            title='月度出口趋势',
            x_label='时间',
            y_label='出口额（CNY）',
            show_markers=True,
            save_path=self.paths.join_image_path(f'{img_name}_month.png')
        )

    def plot_month_country(self, df, img_name, top_countries):
        # 按时间和国家
        df_month_country = self.trade_by_month_country(df)
        # 第一列转换为str
        df_month_country["数据年月"] = pd.to_datetime(df_month_country["数据年月"], format="%Y%m")
        self.plt_manager.plot_lines(
            df_month_country,
            y_columns=top_countries,
            title='月度出口趋势',
            x_label='时间',
            y_label='出口额（CNY）',
            show_markers=True,
            save_path=self.paths.join_image_path(
                f'{img_name}_month_country.png'
            )
        )

    def plot_heatmap(self, df, html_name):
        """
        绘制商品出口额的全球热力图
        :param html_name: 文件名
        :return:
        """
        df_country = self.trade_by_country(df)
        # 全球热力图
        self.plt_manager.plot_world_heatmap(
            df_country,
            country_column='贸易伙伴名称',
            value_column='人民币',
            save_path=self.paths.join_image_path(f'heatmap_{html_name}.html'),
            color_scale='Oranges',
            color_title='出口额（CNY）'
        )

    # ================== 分析入口 ==================

    def run_analysis(self):
        """运行常用分析并绘制图表"""
        print(f"总出口额：{self.total_export(self.df):,.2f} 元")

        self.plot_product(self.file_name)
        df_products = self.split_by_product()
        product_names = list(df_products.keys())
        for product_name in product_names:
            print(f"[INFO] 正在进行数据分析，商品为{product_name}")
            print(f"总出口额：{self.total_export(df_products[product_name]):,.2f} 元")
            top_countries = self.plot_country(df_products[product_name], product_name)
            self.plot_province(df_products[product_name], product_name)
            self.plot_mode(df_products[product_name], product_name)
            self.plot_month(df_products[product_name], product_name)
            self.plot_month_country(df_products[product_name], product_name, top_countries)
            self.plot_heatmap(df_products[product_name], product_name)

if __name__ == "__main__":
    # 示例
    analyzer = CustomsDataAnalyzer("customs_data_自动猫砂盆_2023-2025")
    analyzer.run_analysis()