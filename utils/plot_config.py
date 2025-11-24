import os
from typing import List, Union, Optional
import math
import seaborn as sns
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
import plotly.express as px
from source.utils.country_mapping import *

class PlotManager:
    """
    数据可视化工具类
    支持统一风格配置、折线图、柱状图绘制
    """

    def __init__(self, font_path: str = None):
        """
        初始化绘图管理器

        参数:
        - font_path: str，自定义字体路径 (.ttf)，默认为当前目录下 simhei.ttf
        """
        if font_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(current_dir, "simhei.ttf")
        self.font_path = font_path
        self.set_style()

    def set_style(self):
        """
        应用统一的 Matplotlib 绘图风格配置
        如果找到自定义字体，则使用；否则使用系统默认字体
        """
        mpl.rcParams.update({
            "figure.figsize": (16, 9),     # 默认图像大小
            "figure.dpi": 100,             # 分辨率
            "axes.titlesize": 16,          # 图标题大小
            "axes.labelsize": 14,          # 坐标轴标签大小
            "xtick.labelsize": 12,         # X 轴刻度
            "ytick.labelsize": 12,         # Y 轴刻度
            "legend.fontsize": 12,         # 图例大小
            "lines.linewidth": 2,          # 曲线宽度
            "grid.alpha": 0.3,             # 网格透明度
            "axes.grid": True,             # 默认显示网格
            "savefig.bbox": "tight",       # 保存时裁剪空白
            "savefig.format": "png",       # 默认保存格式
        })

        if self.font_path and os.path.exists(self.font_path):
            custom_font = font_manager.FontProperties(fname=self.font_path)
            mpl.rcParams["font.family"] = custom_font.get_name()
            print(f"[INFO] 使用自定义字体: {custom_font.get_name()} ({self.font_path})")
        else:
            fallback_fonts = ["SimHei", "Microsoft YaHei", "SimSun", "Arial", "DejaVu Sans"]
            mpl.rcParams["font.sans-serif"] = fallback_fonts
            print("[WARN] 未找到自定义字体，使用默认字体:", fallback_fonts)

        # 解决负号显示问题
        mpl.rcParams["axes.unicode_minus"] = False

    def line_style(
            self,
            ax: plt.Axes,
            show_markers: bool = False,
            marker_types: List[str] = None,
            marker_size: int = 6,
            n_colors: int = 50,
            palette: str = "tab10"
    ):
        """
        设置曲线风格：统一实线，可选显示点、点类型和大小，颜色条自动选用美观配色

        :param ax: plt.Axes，matplotlib 轴对象
        :param n_colors: int，颜色个数
        :param show_markers: bool，是否在曲线上显示点
        :param marker_types: List[str]，点的样式列表，可选，支持 'o' (圆), 's' (方), '^' (三角) 等
                             如果数量少于曲线数量，将循环使用
        :param marker_size: int，点的大小
        :param palette: str，Seaborn调色板名，如 'tab10', 'Set2', 'deep'
        """
        # 使用 Seaborn 调色板
        colors = sns.color_palette(palette, n_colors=n_colors)

        # 默认点样式
        default_markers = ['o', 's', '^', 'D', '*', 'v', '<', '>']
        if marker_types is None:
            marker_types = default_markers

        # 遍历曲线设置样式
        for i, line in enumerate(ax.lines):
            line.set_color(colors[i % len(colors)])  # 自动配色
            line.set_linestyle('-')  # 统一实线
            if show_markers:
                line.set_marker(marker_types[i % len(marker_types)])
                line.set_markersize(marker_size)
            else:
                line.set_marker('')

        print(
            f"[INFO] 已应用 line_style: palette={palette}, show_markers={show_markers}, markers={marker_types}, marker_size={marker_size}")

    def bar_style(
            self,
            alpha: float = 0.8,
            width: float = 0.7,
            n_colors: int = 50,
            palette: str = "tab10"
    ) -> dict:
        """
        生成柱状图风格字典

        :param alpha: float, 柱体透明度
        :param width: float, 单根柱子宽度（单位为 x 轴刻度间距的比例）
        :param palette: str，Seaborn调色板名，如 'tab10', 'Set2', 'deep'
        :param n_colors: int，颜色个数
        :return: dict 风格设置
        """
        # 使用 Seaborn 调色板
        colors = sns.color_palette(palette, n_colors=n_colors)
        style = {
            "alpha": alpha,
            "width": width,
            "color": colors
        }
        return style

    def _format_number(
            self,
            val: float,
            number_format: str = "float",
            precision: int = 2
    ) -> str:
        """
        格式化数值为字符串，用于柱顶注释

        :param val: 待格式化的数值
        :param number_format: 'float' 或 'sci'
            - 'float'：以十进制浮点展示，并使用千分位分隔符，保留小数位数由 precision 指定
            - 'sci'：以科学计数法（e）展示，precision 指定小数位数（e 格式的小数位数）
        :param precision: int，精度含义见上
        :return: 格式化后的字符串
        """
        if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
            return ""

        if number_format == "float":
            # 带千分位，保留固定小数位
            fmt = f"{{:,.{precision}f}}"
            return fmt.format(val)
        elif number_format == "sci":
            # 科学计数法，precision 表示小数位数（e 格式）
            fmt = f"{{:.{precision}e}}"
            return fmt.format(val)
        else:
            # 兜底，使用通用格式
            fmt = f"{{:.{precision}f}}"
            return fmt.format(val)

    def plot_lines(
        self,
        df: pd.DataFrame,
        y_columns: Union[str, List[str], int, List[int]],
        x_column: Union[str, int] = 0,
        x_label: str = "X",
        y_label: str = "Y",
        line_labels: Union[str, List[str]] = None,
        title: str = "Line Plot",
        show_markers: bool = False,
        save_path: str = "line_plot.png"
    ):
        """
        绘制折线图

        参数:
        - df: pd.DataFrame，数据源
        - y_columns: 纵坐标列，可以是列名或列索引
        - x_column: 横坐标列，默认第 0 列
        - x_label, y_label: 坐标轴标签
        - line_labels: 曲线标签，默认使用列名
        - title: 图标题
        - save_path: 保存路径
        """
        # 横坐标
        x = df.iloc[:, x_column] if isinstance(x_column, int) else df[x_column]

        # 纵坐标
        if isinstance(y_columns, int):
            y_columns = [df.columns[y_columns]]
        elif isinstance(y_columns, list) and all(isinstance(c, int) for c in y_columns):
            y_columns = [df.columns[c] for c in y_columns]

        # 曲线标签
        if line_labels is None:
            line_labels = y_columns
        elif isinstance(line_labels, str):
            line_labels = [line_labels]

        plt.figure(figsize=(16, 9))
        for col, label in zip(y_columns, line_labels):
            plt.plot(x, df[col], label=label)

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.legend()
        plt.tight_layout()

        # 调用 line_style，自动美观配色
        if type(y_columns) == str or type(y_columns) == int:
            num_colors = 1
        else:
            num_colors = len(y_columns)
        fig, ax = plt.gcf(), plt.gca()
        self.line_style(ax, show_markers=show_markers, n_colors=num_colors)

        plt.savefig(save_path, dpi=300)
        print(f"[INFO] 折线图已保存: {save_path}")

    def plot_bars(
        self,
        df: pd.DataFrame,
        y_columns: Union[str, List[str], int, List[int]],
        x_column: Union[str, int] = 0,
        x_label: str = "X",
        y_label: str = "Y",
        bar_labels: Union[str, List[str]] = None,
        title: str = "Bar Chart",
        save_path: str = "bar_plot.png",
        style: Optional[dict] = None,
        rotate_xticks: Optional[Union[int, float]] = None,
        annotate: bool = False,
        number_format: str = "float",
        precision: int = 2,
        figure_size: [int, int] = None
    ):
        """
        绘制柱状图（支持单列 & 多列分组柱状图），并可在柱顶显示数值，支持浮点或科学计数法。

        :param df: pd.DataFrame，数据源表
        :param y_columns: 要绘制的纵坐标列，可以是列名或列索引或索引列表（支持单列或多列）
        :param x_column: 横坐标列，列名或列索引（默认第 0 列作为类别轴）
        :param x_label: 横坐标标签
        :param y_label: 纵坐标标签
        :param bar_labels: 每组柱子的图例名称，默认使用 y_columns 的列名
        :param title: 图标题
        :param save_path: 图片保存路径
        :param style: 通过 bar_style() 生成的风格字典（包含 alpha, width, color）
        :param rotate_xticks: 可选，x 刻度旋转角度（度数），默认 None 将自动判断（当类别过多时自动 45°）
        :param annotate: bool，是否在每个柱子顶部显示数值
        :param number_format: 'float' 或 'sci'，数值显示方式
        :param precision: int，精度：
               - 当 number_format=='float' 时表示小数位数（例如 2 表示保留 2 位小数）
               - 当 number_format=='sci' 时表示 e 格式的小数位数（例如 2 -> 1.23e+04）
        """
        # 默认样式
        if style is None:
            style = self.bar_style()

        # ---------- 准备数据 ----------
        # 横坐标
        x_vals = df.iloc[:, x_column] if isinstance(x_column, int) else df[x_column]
        # 将 x 标签转成字符串（以便显示）
        x_labels = [str(v) for v in x_vals]

        # 纵坐标列名解析（支持索引和名称）
        if isinstance(y_columns, int):
            y_cols = [df.columns[y_columns]]
        elif isinstance(y_columns, str):
            y_cols = [y_columns]
        elif isinstance(y_columns, list) and all(isinstance(c, int) for c in y_columns):
            y_cols = [df.columns[c] for c in y_columns]
        else:
            y_cols = list(y_columns)

        # 图例标签
        if bar_labels is None:
            bar_labels = y_cols
        elif isinstance(bar_labels, str):
            bar_labels = [bar_labels]

        # 样式拆解
        bar_width = style.get("width", 0.7)
        colors = style.get("color", list(plt.cm.tab10.colors))
        alpha = style.get("alpha", 0.8)

        n_groups = len(x_labels)
        n_bars = len(y_cols)

        # x 的中轴位置（每个类别的中心索引）
        indices = np.arange(n_groups)

        if figure_size is not None:
            plt.figure(figsize=(figure_size[0], figure_size[1]))

        # 计算每组柱子的偏移量，使得分组柱以类别中心对齐
        # 偏移量采用 (i - (n_bars-1)/2) * bar_width
        containers = []  # 用于保存每次 plt.bar 返回的 BarContainer 以便注释
        for i, col in enumerate(y_cols):
            offset = (i - (n_bars - 1) / 2) * bar_width
            bar_positions = indices + offset
            values = df[col].values
            bars = plt.bar(
                bar_positions,
                values,
                width=bar_width * 0.9,  # 柱子之间留一点间隙
                alpha=alpha,
                color=colors[i % len(colors)],
                label=bar_labels[i]
            )
            containers.append(bars)

        # 设置刻度：刻度放在每个分组的中间（indices）
        # 若 rotate_xticks 为 None 则自动判断：类别数 > 10 时旋转 45 度
        if rotate_xticks is None:
            rotate = 45 if n_groups > 10 else 0
        else:
            rotate = rotate_xticks

        plt.xticks(indices, x_labels, rotation=rotate, ha='right' if rotate else 'center')

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)

        # ---------- 在柱顶显示数值（可选） ----------
        if annotate:
            # 计算 y 方向偏移（相对高度），便于文字不与柱子顶端重合
            # 使用数据最大值乘 0.01 作为偏移（当数据非常小或为0时使用固定微小偏移）
            all_values = np.concatenate([c.datavalues for c in containers]) if containers else np.array([0])
            max_val = float(np.nanmax(np.abs(all_values))) if all_values.size > 0 else 0.0
            offset = max_val * 0.01 if max_val != 0 else 0.01

            for bars in containers:
                for rect in bars:
                    height = rect.get_height()
                    # 格式化显示文本
                    label_text = self._format_number(height, number_format=number_format, precision=precision)
                    if label_text == "":
                        continue
                    ax = plt.gca()
                    # 在柱顶上方稍微偏移一点
                    ax.text(
                        rect.get_x() + rect.get_width() / 2,
                        height + offset,
                        label_text,
                        ha='center',
                        va='bottom',
                        fontsize=10
                    )

        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        print(f"[INFO] 柱状图已保存: {save_path}")

    def plot_world_heatmap(
            self,
            df: pd.DataFrame,
            country_column: str | int,
            value_column: str | int,
            title: str = "Global Heatmap",
            save_path: str = "world_heatmap",
            color_scale: str = "Viridis",
            color_title: str = None,
            bool_iso3: bool = False
    ):
        """
        绘制全球热力图（交互式）

        参数：
        :params df: pd.DataFrame，数据源
        :params country_column: str 或 int，国家/地区列名或列索引（中文会自动映射为英文）
        :params value_column: str 或 int，数值列名或列索引
        :params title: str，图表标题
        :params save_path: str，保存路径
        :params color_scale: str，颜色映射方案，
                连续型色带："Viridis"，"Cividis"，"Plasma"，"RdYlGn"，"Inferno"，"Magma"，"Turbo"
                单色渐变方案："Blues"，"Greens"，"Reds"，"Greys"，"Oranges"，"Purples"
        """
        df = df.copy()

        # 如果输入的是列索引，则获取列名
        if isinstance(country_column, int):
            country_column = df.columns[country_column]
        if isinstance(value_column, int):
            value_column = df.columns[value_column]

        if bool_iso3:
            df['country'] = df[country_column]
            locationmode = 'ISO-3'
        else:

            # 映射国家名
            df["country"] = df[country_column].map(lambda x: country_mapping_cn.get(x, x))
            locationmode = 'country names'
            # 检查哪些国家没匹配到
            unmatched = set(df["country"]) - set(country_mapping_cn.values())
            if unmatched:
                print(f"[WARN] 以下国家可能无法识别: {unmatched}")

        # 确保数值是 float
        df[value_column] = pd.to_numeric(df[value_column], errors="coerce").fillna(0)

        print(df[value_column].describe())

        # 绘制热力图
        fig = px.choropleth(
            df,
            locations="country",
            locationmode=locationmode,
            color=value_column,
            hover_name=country_column,
            color_continuous_scale=color_scale,
            title=title
        )

        fig.update_layout(
            geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
            margin=dict(l=0, r=0, t=40, b=0),
            coloraxis_colorbar=dict(
                title=color_title,
                tickprefix="",
                ticks="outside",
                len=0.75,
                thickness=30
            )
        )

        fig.write_html(save_path + '.html')
        fig.write_image(
            save_path + '.png',
            width = 4000,
            height = 2500,
            scale = 3
        )
        print(f"🌍 全球热力图已保存到 {save_path}")

        return fig


