import matplotlib.pyplot as plt
import pandas as pd

df = pd.DataFrame({
    "date": pd.to_datetime([
        "2026-10-01", "2026-10-05", "2026-10-10", "2026-10-12", 
        "2026-10-01", "2026-10-05", "2026-10-10", "2026-10-12"
    ]),
    "exercise": [
        "Lawka plaska", "Lawka plaska", "Lawka plaska", "Lawka plaska",
        "Wznosy bokiem", "Wznosy bokiem", "Wznosy bokiem", "Wznosy bokiem"
    ],
    "diet": [
        "surplus", "surplus", "deficit", "surplus",
        "surplus", "surplus", "deficit", "surplus"
    ],
    "metric_value": [0.0, 5.0, 10.0, 0.0, 12.5, 20.0, 15, 22.5]
})


fig, ax = plt.subplots(figsize=(10, 6))


timeline = df[["date", "diet"]].drop_duplicates().sort_values("date")

timeline["next_date"] = timeline["date"].shift(-1)

timeline = timeline.dropna()

print(timeline)
DIET_COLORS = {
    "surplus": "green",
    "maintenance": "blue",
    "deficit": "red",
    "unknow": "gray"
}
for exercise, group_df in df.groupby("exercise"):

    ax.plot(group_df["date"], group_df["metric_value"], marker="o", label = exercise)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlabel("Daty")
    ax.set_ylabel("OS Y")
    
fig.autofmt_xdate()

for data_od, data_do, dieta in zip(timeline["date"], timeline["next_date"], timeline["diet"]):
    ax.axvspan(data_od, data_do, color=DIET_COLORS[dieta], alpha=0.15, label=dieta)
ax.legend()
plt.show()
