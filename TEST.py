import pandas as pd

df = pd.DataFrame({
    "exercise": ["Lawka", "Lawka", "Wznosy", "Wznosy"],
    "metric_value": [60.0, 66.0, 10.0, 12.0]
})

# Wyciągamy pierwszy element (T0) dla każdego ćwiczenia i rozciągamy na całą ramkę
df["v0"] = df.groupby("exercise")["metric_value"].transform("first")
print(df)