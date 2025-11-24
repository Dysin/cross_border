'''
@Desc:   成本分析模块 (Cost Analysis Module)
         用于读取商品信息表与物流表，计算每个商品的总成本

         功能：
         1. 读取商品表和物流表
         2. 按商品ID合并物流成本
         3. 计算每个商品总成本
         4. 输出成本明细表

         表格要求：
         - 商品表 (products.csv)：
             商品ID, 商品名, 供应商名, 单价(CNY)
         - 物流表 (logistics.csv)：
             商品ID, 运输方式, 单件运费(CNY), 额外费用(CNY)
@Author: Dysin
@Time:   2025/9/16
'''

import os
import pandas as pd
from exchange_rate import ExchangeRateManager

# -----------------------------
# 文件路径设置
# -----------------------------
PRODUCT_FILE = '../../data/products.csv'   # 商品信息表
LOGISTICS_FILE = '../../data/logistics.csv'  # 物流信息表
# -----------------------------
# 读取商品表
# -----------------------------
def load_products(file_path):
    df = pd.read_csv(file_path)
    required_cols = ['SKU', '商品名', '供应商名', '单价(CNY)']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"商品表缺少列: {col}")
    return df

# -----------------------------
# 读取物流表
# -----------------------------
def load_logistics(file_path):
    df = pd.read_csv(file_path)
    required_cols = ['ID', '物流公司', '运输方式', '单件运费(CNY)', '按kg运费(CNY)']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"物流表缺少列: {col}")
    return df

# -----------------------------
# 计算成本
# -----------------------------
def calculate_cost(products_df, logistics_df, order_list, currency='CNY'):
    """
    按 SKU 合并商品表与物流表，计算总成本，并可转换币种
    :param products_df: 商品信息DataFrame
    :param logistics_df: 物流信息DataFrame
    :param order_list: 订单列表，每条订单包含: SKU, 数量, 物流SKU
    :param currency: 输出币种，如 'USD', 'EUR', 默认 'CNY'
    :return: DataFrame，包含总成本
    """
    exchange_manager = ExchangeRateManager()
    results = []

    for order in order_list:
        sku = order['SKU']
        quantity = order['数量']
        shipping_sku = order['物流SKU']

        # 商品信息
        product = products_df[products_df['SKU'] == sku].iloc[0]
        unit_price_cny = product['单价(CNY)']
        weight = product['重量(kg)']

        # 物流信息
        logistics = logistics_df[logistics_df['ID'] == shipping_sku].iloc[0]
        cost_per_piece_cny = logistics['单件运费(CNY)']
        cost_per_kg_cny = logistics['按kg运费(CNY)']

        # 运输成本
        shipping_cost_cny = max(cost_per_piece_cny * quantity, cost_per_kg_cny * weight)

        # 总成本
        total_cost_cny = unit_price_cny * quantity + shipping_cost_cny

        # 币种转换 & 保留两位小数
        unit_price = round(exchange_manager.convert_from_cny(unit_price_cny, currency), 2)
        shipping_cost = round(exchange_manager.convert_from_cny(shipping_cost_cny, currency), 2)
        total_cost = round(exchange_manager.convert_from_cny(total_cost_cny, currency), 2)
        cost_per_piece = round(exchange_manager.convert_from_cny(cost_per_piece_cny, currency), 2)
        cost_per_kg = round(exchange_manager.convert_from_cny(cost_per_kg_cny, currency), 2)

        results.append({
            'SKU': sku,
            '商品名': product['商品名'],
            '供应商名': product['供应商名'],
            '数量': quantity,
            '重量(kg)': weight,
            '物流SKU': shipping_sku,
            '物流公司': logistics['物流公司'],
            '运输方式': logistics['运输方式'],
            '单价({})'.format(currency): unit_price,
            '单件运费({})'.format(currency): cost_per_piece,
            '按kg运费({})'.format(currency): cost_per_kg,
            '运输成本({})'.format(currency): shipping_cost,
            '总成本({})'.format(currency): total_cost
        })

    path_data = '../../data'
    file_cost = os.path.join(path_data, f'cost_summary_{currency}.csv')
    df = pd.DataFrame(results)
    df.to_csv(file_cost, index=False)
    print(f'[INFO] 文件以保持至：{file_cost}')

# -----------------------------
# 主函数示例
# -----------------------------
def main():
    products_df = load_products(PRODUCT_FILE)
    logistics_df = load_logistics(LOGISTICS_FILE)

    # 示例订单列表
    order_list = [
        {'SKU': 'VC-S-BLK', '数量': 100, '物流SKU': 'LS001'},
        {'SKU': 'VCL-STD', '数量': 200, '物流SKU': 'LS002'},
    ]

    calculate_cost(products_df, logistics_df, order_list, 'CNY')

# -----------------------------
if __name__ == '__main__':
    main()