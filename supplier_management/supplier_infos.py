'''
@Desc:   从Alibaba获取供应商数据
@Author: Dysin
@Date:   2025/11/9
'''
# alibaba_search_manual_driver_no_try.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from source.utils.paths import PathManager

def create_driver(chromedriver_path, headless=False):
    """
    创建 Chrome 浏览器实例（手动指定 driver 路径）
    """
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"未找到 ChromeDriver 路径：{chromedriver_path}")

    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")  # 无头模式（可选）
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

    service = ChromeService(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def open_and_search(keyword, chromedriver_path, headless=False):
    driver = create_driver(chromedriver_path, headless=headless)
    wait = WebDriverWait(driver, 15)

    try:
        url = "https://www.alibaba.com"
        print(f"[INFO] 打开：{url}")
        driver.get(url)

        # 等待首页加载
        time.sleep(2)

        # 关闭可能的弹窗
        try:
            close_btns = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Close'], button.close, .next-dialog-close")
            for btn in close_btns:
                try:
                    btn.click()
                    time.sleep(0.3)
                except:
                    pass
        except:
            pass

        # 定位搜索框
        search_box = None
        selectors = [
            "input#search-key",
            "input[name='SearchText']",
            "input.ui-searchbar-keyword",
            "input[placeholder*='Search']"
        ]
        for sel in selectors:
            try:
                search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                if search_box:
                    break
            except:
                continue

        if not search_box:
            try:
                search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='search' or @type='text']")))
            except:
                raise RuntimeError("未能定位到搜索框，请手动检查网页结构。")

        # 输入搜索词并回车
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)
        print(f"[INFO] 已发起搜索：{keyword}")

        # 等待结果加载
        try:
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".organic-gallery-offer, .search-result, .J-offer-wrapper, .item-content")
            ))
            print("[INFO] 搜索结果加载完成。")
        except:
            wait.until(EC.title_contains(keyword.split()[0]))
            print("[WARN] 页面加载，但未检测到标准结果容器。")

        print("页面标题：", driver.title)
        print("当前 URL：", driver.current_url)

        # 抓取前 5 条结果
        time.sleep(2)
        results = driver.find_elements(By.CSS_SELECTOR, ".organic-gallery-offer, .J-offer-wrapper, .item-content")
        print(f"[INFO] 找到 {len(results)} 条结果，打印前 5 条：")
        for i, r in enumerate(results[:5]):
            print(f"Result {i+1}: {r.text.splitlines()[0:3]}")

    except Exception as e:
        print("[ERROR]", e)
    finally:
        print("[INFO] 5 秒后关闭浏览器...")
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    # 👇 修改为你自己的 chromedriver.exe 路径
    chromedriver_path = PathManager().join_chrome_path("chromedriver.exe")
    keyword = "handheld fan"

    open_and_search(keyword, chromedriver_path, headless=False)
