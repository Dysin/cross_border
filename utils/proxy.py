'''
@Desc:   科学上网/代理管理工具
@Author: Dysin
@Time:   2025/9/17
'''

import socket

def clash_proxy(proxy_type="http", possible_ports=None):
    """
    自动检测 Clash 本地代理端口是否可用
    proxy_type: 'http' 或 'socks5'
    possible_ports: 端口列表，默认 http=[7890], socks5=[7891]
    """
    if possible_ports is None:
        possible_ports = [7890] if proxy_type == "http" else [7891]

    for port in possible_ports:
        s = socket.socket()
        s.settimeout(0.5)
        try:
            s.connect(('127.0.0.1', port))
            s.close()
            print(f"检测到 Clash 可用代理: {proxy_type}://127.0.0.1:{port}")
            return f"{proxy_type}://127.0.0.1:{port}"
        except:
            s.close()
            continue
    print(f"未检测到可用 Clash 代理: {proxy_type}")
    return None

