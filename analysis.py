print("🔥 這是最新版本")
print("OK")

import os
print(os.getcwd())

import os
path = r"D:\project\OnlineRetail.csv"

import pandas as pd

import os

# 讀取資料
df = pd.read_csv(path, encoding="ISO-8859-1")

print("成功讀取")
print(df.shape)
print(df.head())

# 顯示前5筆，head()預設5筆資料

#專案正式開始
df = df[~df['InvoiceNo'].str.startswith('C')]
df = df[df['Quantity'] > 0]
df = df[df['UnitPrice'] > 0]

df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
#將商品合併訂單
order_df = df.groupby('InvoiceNo').agg({
    'TotalPrice': 'sum',
    'Quantity': 'sum'
}).reset_index()

print(order_df.head())

print(df['Quantity'].min())    #確認數字>=0
print(df['TotalPrice'].min())  #確認數字>=0
print(df['UnitPrice'].min())   #確認數字>=0



#模擬「配送距離」
import numpy as np
np.random.seed(42)
# 每筆訂單隨機距離（1~100 km），用於模擬物流情境
order_df['Distance_km'] = np.random.uniform(1, 100, len(order_df))

print(order_df.head())

#設定物流成本模型 (成本 = 基本費 + 距離 × 每公里油費) 英國當地
base_cost = 3            # 每單基本成本（例如人力、包裝）約 £2 ~ £5（倉儲、包裝、人力）
fuel_cost_per_km = 0.5     # 每公里油費 增加顯著 油價：約 £1.5 / litre  每公升跑：約 12–15 km

order_df['LogisticsCost'] = base_cost + (order_df['Distance_km'] * fuel_cost_per_km)

margin = 0.1  # 毛利率30% 降低到10%顯著

order_df['Revenue'] = order_df['TotalPrice']
order_df['Profit'] = (order_df['Revenue'] * margin) - order_df['LogisticsCost']

print(order_df.head())
print(order_df.describe())

order_df[['TotalPrice','Distance_km','LogisticsCost','Profit']].head()


#油價上升模擬
#油價情境
#scenarios = {
    #'Base': 1.0,
    #'Up_10%': 1.1,
    #'Up_30%': 1.3,
    #'Up_50%': 1.5
    #}
#調整參數用以顯著判別資料
scenarios = [
    {'name': 'Base', 'fuel_mult': 1.0, 'fuel_cost': 0.1, 'margin': 0.3},
    {'name': 'HighFuel', 'fuel_mult': 1.5, 'fuel_cost': 0.5, 'margin': 0.3},
    {'name': 'LowMargin', 'fuel_mult': 1.0, 'fuel_cost': 0.1, 'margin': 0.15},
    {'name': 'WorstCase', 'fuel_mult': 1.5, 'fuel_cost': 0.5, 'margin': 0.15}
]

#建立不同情境的成本 & 利潤  #只改「油費」，其他不變
#results = []

# for name, multiplier in scenarios.items():
    
#     temp_df = order_df.copy()
    
#     # 調整油費
#     temp_df['FuelCost'] = temp_df['Distance_km'] * fuel_cost_per_km * multiplier
    
#     # 總物流成本
#     temp_df['TotalLogisticsCost'] = base_cost + temp_df['FuelCost']
    
#     # 利潤
#     temp_df['Profit'] = (temp_df['Revenue'] * margin) - temp_df['TotalLogisticsCost']
    
#     temp_df['Scenario'] = name
    
#     results.append(temp_df)

#final_df = pd.concat(results)
#顯著 迴圈
#從原始訂單order_df裡面，模擬另一種情境儲存在temp_df裡面
results = []

for s in scenarios:
    
    temp_df = order_df.copy()
    
    # 油費
    temp_df['FuelCost'] = temp_df['Distance_km'] * s['fuel_cost'] * s['fuel_mult']
    
    # 總物流成本
    temp_df['TotalLogisticsCost'] = base_cost + temp_df['FuelCost']
    
    # 利潤
    temp_df['Profit'] = (temp_df['Revenue'] * s['margin']) - temp_df['TotalLogisticsCost']
    
    temp_df['Scenario'] = s['name']
    
    results.append(temp_df)

final_df = pd.concat(results)

#每種情境「平均利潤」
#summary = final_df.groupby('Scenario')['Profit'].mean()
#顯著分析
summary = final_df.groupby('Scenario')['Profit'].mean()

loss_rate = (final_df['Profit'] < 0).groupby(final_df['Scenario']).mean()

print(summary)
print(loss_rate)

print(df.shape)
print(order_df.shape)
print(final_df.shape)

#找出「虧損訂單」

loss_orders = final_df[final_df['Profit'] < 0]

print(loss_orders.shape)
#15968 / 79840 ≈ 0.20，約 20% 訂單是虧損
#比例
loss_rate = final_df.groupby('Scenario')['Profit'].apply(lambda x: (x < 0).mean())

risky_orders = final_df[
    (final_df['Scenario'] == 'WorstCase') & 
    (final_df['Profit'] < 0)
]

print(risky_orders[['TotalPrice', 'Distance_km']].describe())


#視覺化
import matplotlib.pyplot as plt

os.makedirs("images", exist_ok=True)

#油價 vs 平均利潤
plt.figure(figsize=(6,4)) #開新畫布(未被前資料影響)
summary.plot(kind='bar')
plt.title("Profit under Fuel Price Scenarios")
plt.ylabel("Average Profit")
plt.xlabel("Scenario")
plt.savefig("images/profit.png")  #先存 → 再 show，不然會空白
plt.grid()
plt.show(block=False)
input("按 Enter 關閉圖表...")
plt.close()

#虧損訂單比例
plt.figure(figsize=(6,4))  #開新畫布(未被前資料影響)
loss_rate.plot(kind='bar')
plt.title("Loss Rate under Fuel Price Scenarios")
plt.ylabel("Loss Rate")
plt.xlabel("Scenario")
plt.savefig("images/loss_rate.png")
plt.grid()
plt.show(block=False)
input("按 Enter 關閉圖表...")
plt.close()

#距離 vs 利潤
plt.figure(figsize=(6,4))  #開新畫布(未被前資料影響)
base_df = final_df[final_df['Scenario'] == 'Base']

plt.scatter(base_df['Distance_km'], base_df['Profit'])
plt.xlabel("Distance (km)")
plt.ylabel("Profit")
plt.title("Distance vs Profit")
plt.savefig("images/distance_profit.png")
plt.grid()
plt.show(block=False)
input("按 Enter 關閉圖表...")
plt.close()

plt.figure(figsize=(6,4)) #開新畫布(未被前資料影響)

plt.plot(summary_df["fuel_price"], summary_df["Profit"], marker='o')
plt.xlabel("Fuel Price")
plt.ylabel("Average Profit")
plt.title("Impact of Fuel Cost on Profitability")
plt.savefig("images/profit_vs_fuel.png")
plt.grid()

plt.show(block=False)
input("按 Enter 關閉圖表...")
plt.close()

print("\n=== CHECKPOINT ===")

try:
    print("Summary:")
    print(summary)
except:
    print("summary 還沒建立")

try:
    print("\nLoss Rate:")
    print(loss_rate)
except:
    print("loss_rate 還沒建立")

print("\nShape:")
print(final_df.shape)

print("\n==============================")
print("📊 DATA SHAPE")
print("==============================")
print("df:", df.shape)
print("order_df:", order_df.shape)
print("final_df:", final_df.shape)

print("\n==============================")
print("💰 平均利潤 (Average Profit)")
print("==============================")
print(summary)

print("\n==============================")
print("⚠️ 虧損比例 (Loss Rate)")
print("==============================")
print(loss_rate)

print("\n==============================")
print("🔥 高風險訂單分析")
print("==============================")
print(risky_orders[['TotalPrice', 'Distance_km']].describe())

import matplotlib.pyplot as plt

# 把 summary 轉成 DataFrame（方便畫圖）
summary_df = summary.reset_index()

plt.figure(figsize=(6,4))  #開新畫布(未被前資料影響)
plt.plot(summary_df['Scenario'], summary_df['Profit'], marker='o')

plt.title('Oil Price Impact on Profit')
plt.xlabel('Scenario')
plt.ylabel('Average Profit')

plt.grid()

plt.savefig("images/oil_impact.png")
plt.show(block=False)
input("按 Enter 關閉圖表...")
plt.close()

print(df.shape)
print(order_df.shape)
print(final_df.shape)
print("final_df:", final_df.shape)

# print(final_df.head())


# print("=== Summary ===")
# print(summary)

# print("\n=== Loss Rate ===")
# print(loss_rate)

# print("\n=== final_df shape ===")
# print(final_df.shape)


print("✅ 我真的有跑到最下面")
exit()
