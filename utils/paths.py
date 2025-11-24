'''
@Desc:   项目路径管理
@Author: Dysin
@Time:   2025/9/17
'''

import os
from pathlib import Path

class PathManager:
    """
    项目路径管理类
    - 获取项目根目录
    - 构建各类文件保存路径（images, data, logs）
    """

    def __init__(self):
        # 项目根目录（默认为当前文件上两级目录）
        self.root_dir = Path(__file__).resolve().parent.parent.parent

        # 图片保存路径
        self.images_dir = self.root_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        # 数据保存路径
        self.data_dir = self.root_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 日志路径
        self.logs_dir = self.root_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # source路径
        self.source_dir = self.root_dir / "source"

        # 第三方库路径
        self.third_party_dir = self.source_dir / "third_party"

        # chromedriver路径
        self.chrome_dir = self.third_party_dir / "chrome"

    def get_root(self) -> str:
        """返回项目根目录字符串"""
        return str(self.root_dir)

    def get_images_dir(self) -> str:
        """返回图片保存目录"""
        return str(self.images_dir)

    def get_data_dir(self) -> str:
        """返回数据保存目录"""
        return str(self.data_dir)

    def get_logs_dir(self) -> str:
        """返回日志目录"""
        return str(self.logs_dir)

    def get_source(self) -> str:
        """返回source目录字符串"""
        return str(self.source_dir)

    def get_third_party(self) -> str:
        """返回第三方库目录字符串"""
        return str(self.third_party_dir)

    def get_chrome(self) -> str:
        """返回chromedirver目录字符串"""
        return str(self.chrome_dir)

    def join_image_path(self, filename: str) -> str:
        """返回完整图片保存路径"""
        return str(self.images_dir / filename)

    def join_data_path(self, filename: str) -> str:
        """返回完整数据保存路径"""
        return str(self.data_dir / filename)

    def join_log_path(self, filename: str) -> str:
        """返回完整日志文件路径"""
        return str(self.logs_dir / filename)

    def join_chrome_path(self, filename: str) -> str:
        """返回chrome文件路径"""
        return str(self.chrome_dir / filename)

