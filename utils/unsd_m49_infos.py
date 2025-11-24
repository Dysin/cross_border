'''
@Desc:   获取联合国M49数据
@Author: Dysin
@Date:   2025/11/1
'''
import os.path

import pandas as pd

class UNSDM49:
    def __init__(self):
        file_csv = os.path.join('../database', '2022-09-24__Excel_UNSD_M49.csv')
        self.df = pd.read_csv(file_csv)

    def get_m49_code(self, country_name):
        """
        根据国家名称获取对应的 M49 Code。
        参数:
        - csv_file: str, CSV 文件路径，包含 'Country or Area' 和 'M49 Code' 列
        - country_name: str, 要查询的国家名称
        返回:
        - int 或 None: 对应的 M49 Code，如果找不到则返回 None
        """
        # 构建 Country -> M49 Code 的映射
        country_to_m49 = dict(zip(self.df['Country or Area'], self.df['M49 Code']))
        # 查询并返回
        return country_to_m49.get(country_name)

    def m49_to_iso3(self, code):
        iso3 = dict(zip(self.df['M49 Code'], self.df['ISO-alpha3 Code']))
        res = iso3.get(code)
        return res

if __name__ == '__main__':
    unsd = UNSDM49()
    country_name = 'China'
    m49_code = unsd.get_m49_code(country_name)
    print(m49_code)