'''
@Desc:   图片工具类
@Author: Dysin
@Date:   2025/11/23
'''

import os.path
from PIL import Image
import requests
from io import BytesIO

class ImageUtils:
    def __init__(
            self,
            path_target=None,
            name_target=None
    ):
        self.path_target = path_target
        self.name_target = name_target

    def download(self, url, img_type='.png'):
        """
        下载图片并转换为 png 格式保存
        :param url: 图片 URL
        :param img_type: 保存图片格式，默认 '.png'
        """
        file_img = os.path.join(self.path_target, self.name_target + img_type)
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # 如果请求失败，会抛出异常
            # 将内容读取到内存
            img_data = BytesIO(response.content)
            # 使用 PIL 打开图片
            with Image.open(img_data) as im:
                # 转换为 RGB 模式（防止某些格式如 RGBA 导致保存失败）
                im = im.convert('RGB')
                im.save(file_img, format='PNG')
            print(f"图片已保存并转换为 PNG: {file_img}")
        except Exception as e:
            print(f"下载失败: {e}")

