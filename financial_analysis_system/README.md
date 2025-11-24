# 📘 README - 跨境电商金融分析系统

## 📌 项目简介

本系统旨在帮助跨境电商卖家进行 **财务与利润分析**，覆盖从 **产品成本核算 → 物流费用 → 平台手续费 → 广告投放 → 税务 → 最终利润** 的完整闭环。
通过模块化设计，用户可以快速评估不同产品和市场的盈利能力，并做出数据驱动的决策。

---

## 🏗 功能模块

### 1. 成本核算（`cost_analysis/`）

* **产品成本**：包含生产成本、包装成本、人工成本等。
* **采购批次**：支持按批次输入不同采购价格。
* **币种换算**：自动获取实时汇率，统一换算为目标币种（如 USD）。

### 2. 物流费用（`logistics/`）

* **多渠道支持**：空运、海运、快递、小包。
* **费用估算**：根据重量、体积、目的地自动计算。
* **分摊逻辑**：支持按 SKU 分摊运输费用。

### 3. 平台费用（`platform_fees/`）

* **Shopify/独立站**：支付通道手续费、服务器费用。
* **Amazon/eBay**：佣金、仓储费、上架费。
* **独立自营**：支持 PayPal、Stripe 费率。

### 4. 广告与推广（`ads/`）

* **Google Ads、Meta Ads** 投放成本录入。
* **ROI 分析**：广告费用与销售额对应关系。
* **客户获取成本 (CAC)** 计算。

### 5. 税务处理（`tax/`）

* **关税**：按目的国税率计算。
* **VAT/增值税**：支持欧盟、英国等市场。
* **税费分摊**：自动加入到成本模型。

### 6. 利润计算与报表（`reports/`）

* **单品利润**：单个 SKU 的毛利、净利。
* **订单利润**：单个订单的成本 & 利润分析。
* **整体利润**：指定时间范围的总收益。
* **可视化**：利润趋势图、盈亏平衡图。

---

## 📂 项目结构

```
financial_analysis_system/
│── README.md                # 使用说明
│── requirements.txt         # 依赖库
│── main.py                  # 主入口          
│── cost_calculator.py       # 成本模块
│── logistics_calculator.py  # 物流模块
│── fees_calculator.py       # 平台费用模块
│── ads_analyzer.py          # 广告模块
│── tax_calculator.py        # 税务模块
│── report_generator.py      # 报表与可视化
│── data/                    # 输入/输出数据
    ├── products.csv
    ├── logistics.csv
    └── reports/
```

---

## ⚙️ 使用方法

### 1. 环境准备

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 输入数据

在 `data/` 文件夹中，填写：

* **products.csv** → 产品成本、SKU、采购价
* **logistics.csv** → 运输渠道、费用

### 3. 运行分析

```bash
# 运行主程序
python main.py
```

### 4. 输出报表

系统将在 `data/reports/` 文件夹生成：

* **profit\_summary.csv**：利润汇总
* **profit\_trend.png**：趋势图

---

## 📊 示例输出

```bash
产品: Vape Case
成本: $2.50
物流: $1.20
平台费: $0.50
广告费: $1.00
税费: $0.30
-----------------------
销售价格: $7.00
净利润: $1.50 (Margin: 21.4%)
```

报表图示例（利润随时间变化）：
📈 （matplotlib 生成）

---

## 🔮 未来扩展

* 📦 **自动爬取物流报价**（API 连接 DHL/UPS）
* 💳 **多币种结算**（实时汇率）
* 📊 **Web 可视化仪表盘**（Flask/Django 前端展示）
* 🤖 **智能推荐定价**（基于历史销售 & 成本预测）

---

👉 这样你就能用这个系统 **管理跨境电商财务数据**，快速看清哪个产品赚钱，哪个产品亏钱。

要不要我帮你先写一个 **main.py 的骨架代码**（串联所有模块），这样你能马上跑一个 Demo？
