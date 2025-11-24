'''
@Desc:   海关统计数据分析
            1.数据来源
            (1) UN Comtrade Database
             网址：https://comtradeplus.un.org/
             API：https://comtradedeveloper.un.org/
             github：https://github.com/uncomtrade/comtradeapicall
@Author: Dysin
@Date:   2025/11/2
'''

import os
import time
import pandas as pd
import comtradeapicall
from source.utils.paths import PathManager
from source.utils.plot_config import PlotManager
from source.utils.unsd_m49_infos import UNSDM49

class UNComtrade:
    def __init__(self):
        self.key = '5903214bebfa40099f1d58380fe24389'
        # self.key = '6205c6d207a24890b0094d6743d77d6e'
        self.unsd = UNSDM49()
        self.paths = PathManager()

    def expand_month_range(
            self,
            month_range: str
    ):
        """
        将输入的月份范围（如 '202501-202503'）展开成一个月份列表
        例如：'202501-202503' → [202501, 202502, 202503]
        支持跨年：'202512-202602' → [202512, 202601, 202602]
        :params month_range: 月份范围
        """
        # 拆分输入字符串，得到起始和结束的年月（如 202501 和 202503）
        start, end = map(int, month_range.split('-'))
        # 存放结果的列表
        result = []
        # 将起始年月和结束年月拆分为年份和月份
        year, month = divmod(start, 100)  # 202501 → (2025, 1)
        end_year, end_month = divmod(end, 100)  # 202503 → (2025, 3)
        # 从起始年月循环到结束年月
        while (year < end_year) or (
                year == end_year and
                month <= end_month
        ):
            # 将当前年月合并为整数（如 2025 * 100 + 1 = 202501）
            result.append(year * 100 + month)
            # 月份递增
            month += 1
            # 若超过 12 月，则年份加 1，月份重置为 1
            if month > 12:
                month = 1
                year += 1
        # 返回完整的月份列表
        return result

    def get_tariffline_data(
            self,
            periods,
            cmd_code, # HS 编码章节
            countrys
    ):
        periods_list = self.expand_month_range(periods)

        df_list = []
        if countrys == 'all':
            for period in periods_list:
                result = comtradeapicall.getTarifflineData(
                    self.key,
                    typeCode='C',
                    freqCode='M',
                    clCode='HS',
                    period=period,
                    reporterCode=None,
                    cmdCode=cmd_code,
                    flowCode='X',
                    partnerCode=None,
                    partner2Code=None,
                    customsCode=None,
                    motCode=None,
                    maxRecords=None,
                    format_output='JSON',
                    countOnly=None,
                    includeDesc=True
                )
                # 转为 pandas DataFrame
                df = pd.DataFrame(result)
                print(df)
                if not df.empty:
                    df_list.append(df)
                time.sleep(0.5)
        else:
            for country in countrys:
                report_code = self.unsd.get_m49_code(country)
                print(f'[INFO] Country: {country}')
                for period in periods_list:
                    result = comtradeapicall.getTarifflineData(
                        self.key,
                        typeCode='C',
                        freqCode='M',
                        clCode='HS',
                        period=period,
                        reporterCode=report_code,
                        cmdCode=cmd_code,
                        flowCode='X',
                        partnerCode=None,
                        partner2Code=None,
                        customsCode=None,
                        motCode=None,
                        maxRecords=None,
                        format_output='JSON',
                        countOnly=None,
                        includeDesc=True
                    )
                    # 转为 pandas DataFrame
                    df = pd.DataFrame(result)
                    print(df)
                    if not df.empty:
                        df_list.append(df)
                    time.sleep(0.5)
        df_list = [df.dropna(axis=1, how='all') for df in df_list]
        df_list = pd.concat(df_list, ignore_index=True)

        df_list.to_csv(
            os.path.join(
                self.paths.data_dir,
                'customs_data_un',
                f"export_{cmd_code}_{periods}.csv"
            ),
            index=False,
            encoding='utf-8-sig'
        )
        print(f"✅ 已保存为 china_fan_export_{periods}.csv")
        return df_list

class UNComtradeAnalysis:
    def __init__(
            self,
            periods,
            cmd_code,
            cmd_desc
    ):
        self.paths = PathManager()
        self.path_image = os.path.join(self.paths.images_dir, 'customs_data_un')
        csv_name = f'export_{cmd_code}_{periods}.csv'
        csv_file = os.path.join(
            self.paths.data_dir,
            'customs_data_un',
            csv_name
        )
        df = pd.read_csv(csv_file, low_memory=False)
        self.df = df[df['partnerDesc'] != 'China']
        self.plt_manager = PlotManager()
        self.periods = periods
        self.cmd_code = cmd_code
        self.cmd_desc = cmd_desc

    def total_export(self) -> float:
        '''
        计算总贸易额（主要为出口）
        '''
        # primaryValue为主要统计值（美元），
        # 与 fobvalue 或 cifvalue 一致（取决于流向）
        result = self.df['primaryValue'].sum()
        print(f'[INFO] 总贸易额（主要为出口）：{result}美元')
        return result

    def trade_by_variable(self, var, bool_sorted=True) -> pd.DataFrame:
        df = self.df.groupby(var)['primaryValue'].sum().reset_index()
        if bool_sorted:
            df = df.sort_values(by='primaryValue', ascending=False)
        return df

    def trade_by_two_variable(self, var1, var2) -> pd.DataFrame:
        df = self.df.pivot_table(
            index=var1,
            columns=var2,
            values='primaryValue',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        return df

    def plot_country(self):
        df = self.trade_by_variable('partnerDesc')
        df_top_country = df.head(20)
        self.plt_manager.plot_bars(
            df_top_country,
            y_columns=1,
            title=f'{cmd_desc}出口目的地Top 20',
            x_label='国家/地区',
            y_label='出口额（USD）',
            save_path=os.path.join(
                self.path_image,
                f'customs_data_{self.cmd_code}_{self.periods}_country.png'
            ),
            rotate_xticks=15,
            figure_size=[16, 7]
        )
        top_countries = df_top_country['partnerDesc'].tolist()
        return top_countries

    def plot_month(self):
        df = self.trade_by_variable('period', False)
        df['period'] = pd.to_datetime(df['period'], format="%Y%m")
        self.plt_manager.plot_lines(
            df,
            y_columns=1,
            title=f'{self.cmd_desc}月度出口趋势',
            x_label='时间',
            y_label='出口额（USD）',
            show_markers=True,
            save_path=os.path.join(
                self.path_image,
                f'customs_data_{self.cmd_code}_{self.periods}_month.png'
            )
        )

    def plot_month_country(self, top_countries):
        df = self.trade_by_two_variable('period', 'partnerDesc')
        df['period'] = pd.to_datetime(df['period'], format="%Y%m")
        self.plt_manager.plot_lines(
            df,
            y_columns=top_countries,
            title=f'{self.cmd_desc}月度出口趋势',
            x_label='时间',
            y_label='出口额（USD）',
            show_markers=True,
            save_path=os.path.join(
                self.path_image,
                f'customs_data_{self.cmd_code}_{self.periods}_month_country.png'
            )
        )

    def plot_heatmap(self):
        """
        绘制商品出口额的全球热力图
        :return:
        """
        df = self.trade_by_variable('partnerCode')
        df['partnerCode'] = df['partnerCode'].apply(UNSDM49().m49_to_iso3)
        df = df.reset_index(drop=True)
        print(df)
        # 全球热力图
        self.plt_manager.plot_world_heatmap(
            df,
            country_column='partnerCode',
            value_column='primaryValue',
            title=f'{cmd_desc}',
            save_path=os.path.join(
                self.path_image,
                f'heatmap_{self.cmd_code}_{self.periods}'
            ),
            color_scale='Oranges',
            color_title='出口额（USD）',
            bool_iso3=True
        )

    def run(self):
        top_countries = self.plot_country()
        self.plot_month()
        self.plot_month_country(top_countries)
        self.plot_heatmap()

if __name__ == "__main__":
    # countrys = [
    #     'China',
    #     'United States',
    #     'Germany',
    #     'Japan',
    #     'Netherlands',
    #     'Hong Kong',
    #     'France',
    #     'Italy',
    #     'United Kingdom',
    #     'Canada'
    # ]

    countrys = 'all'

    periods = '201501-202508'

    cmd_dist = {
        # '842139': '空气净化器',
        '841451': '小风扇',
        '851830': '智能音箱',
        '847989': '庭院机器人',
        # '850811': '泳池清洁机器人/扫地机器人',
        # '850980': '电动牙刷',
        # '851631': '吹风机',
        # '900630': '摄影相机（水下作业、航测、医学等）',
        # '901380': '车载 HUD 抬头显示器',
        '880220': '固定翼无人机',
        # '880621': '无人飞行器',
        # '854370': '电子烟',
        # '852580': '网络摄像头、安防监控摄像机、智能摄像头',
        '900791': '手机三轴云台/稳定器'
    }

    uncomtrade = UNComtrade()
    for cmd_code, cmd_desc in cmd_dist.items():
        print(cmd_code)
        # df =uncomtrade.get_tariffline_data(
        #     periods=periods,
        #     cmd_code=cmd_code,
        #     countrys=countrys
        # )

        comtrade_analysis = UNComtradeAnalysis(periods, cmd_code, cmd_desc)
        # comtrade_analysis.run()

    df = pd.DataFrame(columns=['品类', '贸易额（USD）'])
    for cmd_code, cmd_desc in cmd_dist.items():
        comtrade_analysis = UNComtradeAnalysis(periods, cmd_code, cmd_desc)
        value = comtrade_analysis.total_export()
        df.loc[len(df)] = [cmd_desc, value]
    path_image = os.path.join(PathManager().images_dir, 'customs_data_un')
    df = df.sort_values(by='贸易额（USD）', ascending=False)
    PlotManager().plot_bars(
        df,
        y_columns=1,
        title='商品贸易额对比',
        x_label='品类',
        y_label='进口额（USD）',
        save_path=os.path.join(
            path_image,
            f'customs_data_products_{periods}.png'
        ),
        rotate_xticks=15,
        figure_size=[16, 7]
    )
