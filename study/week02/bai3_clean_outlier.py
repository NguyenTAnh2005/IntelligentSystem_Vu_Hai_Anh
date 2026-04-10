import pandas as pd

# Bước 1: Chèn outlier
df = pd.read_csv("hvac_simulated_week2.csv")
df.loc[5, "T_in"] = 99
df.loc[10, "T_in"] = -5
df.loc[20, "humidity"] = 0
df.loc[25, "humidity"] = 150
df.to_csv("hvac_with_outlier.csv", index=False)
print("Đã tạo hvac_with_outlier.csv với outlier.")

# Bước 2: Phát hiện & xử lý outlier
df_outlier = pd.read_csv("hvac_with_outlier.csv")

def is_T_in_bad(x):
    return x < 15 or x > 45

def is_humidity_bad(x):
    return x < 10 or x > 100

bad_T = df_outlier["T_in"].apply(is_T_in_bad)
bad_H = df_outlier["humidity"].apply(is_humidity_bad)

print("Số dòng T_in bất thường:", bad_T.sum())
print("Số dòng humidity bất thường:", bad_H.sum())

# Xử lý: thay bằng trung bình của 2 hàng lân cận
for idx in df_outlier[bad_T].index:
    if 1 <= idx < len(df_outlier) - 1:
        df_outlier.loc[idx, "T_in"] = (df_outlier.loc[idx - 1, "T_in"] + df_outlier.loc[idx + 1, "T_in"]) / 2
    else:
        df_outlier.loc[idx, "T_in"] = df_outlier["T_in"].median()

for idx in df_outlier[bad_H].index:
    if 1 <= idx < len(df_outlier) - 1:
        df_outlier.loc[idx, "humidity"] = (df_outlier.loc[idx - 1, "humidity"] + df_outlier.loc[idx + 1, "humidity"]) / 2
    else:
        df_outlier.loc[idx, "humidity"] = df_outlier["humidity"].median()

df_outlier.to_csv("hvac_cleaned.csv", index=False)
print("Đã lưu file hvac_cleaned.csv sau khi làm sạch.")