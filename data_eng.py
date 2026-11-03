import datetime as dt
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DIET_COLORS = {
    "surplus": "green",
    "maintenance": "blue",
    "deficit": "red",
    "unknown": "gray"
}

#na potrzebny testów
BASE_DIRECTORY = Path(".")
WORKOUTS_PATH = BASE_DIRECTORY / "spreadsheets" / "workoutsTEST.csv"
REPORTS_PATH = BASE_DIRECTORY / "reports"
# 1. Test zakresu dat (mode: "dates") — maksymalny ciężar roboczy ("weight")
# Test A: Progres % ciężaru (powinno pokazać: 0%, +4.17%, +8.33%, +16.67%)
config_weight_pct = {
    "exercises": ["Lawka plaska", "Wznosy bokiem", "Przysiad ze sztanga"],
    "period": {"mode": "dates", "start_date": "2026-08-01", "end_date": "2026-10-30"},
    "diet": "deficit",
    "type": "weight progress in %"
}

# Test B: Zwykła objętość (volume) z ostatnich 3 sesji
config_volume_raw = {
    "exercises": ["Lawka plaska"],
    "period": {"mode": "count", "value": 10},
    "diet": "all",
    "type": "volume"
}

# Test C: Progres % objętości (volume progress in %)
config_volume_pct = {
    "exercises": ["Lawka plaska", "Przysiad ze sztanga"],
    "period": {"mode": "count", "value": 16},
    "diet": "all",
    "type": "volume progress in %"
}

# Test D: Stosunek ciężaru do masy ciała (weight/bodyweight)
config_ratio = {
    "exercises": ["Przysiad ze sztanga"],
    "period": {"mode": "dates", "start_date": "2026-08-01", "end_date": "2026-10-30"},
    "diet": "all",
    "type": "weight/bodyweight"
}

def create_plt(config: dict, workouts_path: Path):
    df = get_raw_dataframe(workouts_path)
    df = transform_data(df, config)

    if df.empty:
        print("[WARNING] for those parameters dataframe is empty! Plot creating is aborted!")
        return

    fig, ax = plt.subplots(figsize=(10,6))
    for exercise, df_grouped in df.groupby("exercise"):
        ax.plot(df_grouped["date"], df_grouped["metric_value"], marker="o", label = exercise)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlabel("Date")
    ax.set_ylabel(config["type"])
    #dodaj potem slownik z type aby to jakos lepiej wygladalo np nie weight a weight [KG]

    timeline = df[["date", "diet"]].drop_duplicates().sort_values("date")
    timeline["next_date"] = timeline["date"].shift(-1)
    timeline = timeline.dropna()


    diet_added_to_label = []
    for diet_from, diet_to, diet in zip(timeline["date"], timeline["next_date"], timeline["diet"]):
        diet_color = DIET_COLORS[diet]
        if diet in diet_added_to_label:#dzieki temu na legendzie dodajemy maks raz kazdy typ diety
            diet = None
        else:
            diet_added_to_label.append(diet)
        ax.axvspan(diet_from, diet_to, color=diet_color, alpha=0.15, label=diet, lw=0)



    ax.legend()
    fig.autofmt_xdate()
    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    metric_name = config["type"].split(" ")[0].replace("/", "_")
    file_name = f"{timestamp}_{metric_name}.svg"
    REPORTS_PATH.mkdir(parents=True, exist_ok=True)
    path = REPORTS_PATH / file_name
    fig.savefig(path)
    plt.close(fig)
    print(f"Plot {path} created successfully")

def transform_data(df: pd.DataFrame, config: dict):
    df = get_prepared_dataframe(df)
    df = filter_by_exercise(df,config["exercises"])
    df = filter_by_period(df,config["period"])
    df = filter_by_diet(df, config["diet"])
    base_metric = config["type"].split(" ")[0]
    df = add_metric_column(df, base_metric)
    df = aggregate_metrics(df, base_metric)
    is_progres_metric = config["type"].endswith("%")
    df = calculate_progress(df, is_progres_metric)
    return df

def get_prepared_dataframe(df: pd.DataFrame):
    df = df.sort_values("date", ascending=True, ignore_index = True)#mozna wprowadzac daty w roznej kolejnosci, weic je sortujemy
    df["bodyweight"] = df["bodyweight"].ffill().bfill()#uzupelniamy puste miejsca z waga
    return df

def filter_by_exercise(df: pd.DataFrame, exercises: list):
    return df[df["exercise"].isin(exercises)]

def filter_by_period(df: pd.DataFrame, period: dict):
    if period["mode"] == "dates":
        start = pd.to_datetime(period["start_date"])
        end = pd.to_datetime(period["end_date"])
        return df[(df["date"]>=start)&(df["date"]<=end)]
    else:
        n = period["value"]
        target_dates = df["date"].drop_duplicates().sort_values().tail(n)
        return df[df["date"].isin(target_dates)]
    
def filter_by_diet(df: pd.DataFrame, diet: str):
    if diet == "all":
        return df
    return df[df["diet"] == diet]

def add_metric_column(df: pd.DataFrame, type: str):
    METRIC_STRAT = {
        "weight": lambda d: d["weight"],
        "weight/bodyweight": lambda d: d["weight"]/d["bodyweight"],
        "volume": lambda d: d["weight"]*d["reps"]
    }
    strat = METRIC_STRAT.get(type)
    if strat is None:
        raise ValueError(f"niezaimplemetnowny typ metryki: {type}")
    df["metric_value"] = strat(df)
    return df

def aggregate_metrics(df: pd.DataFrame, type: str):
    METRIC_STRAT = {
            "weight": lambda d: d.groupby(["date", "exercise", "diet"])["metric_value"].max().reset_index(),
            "weight/bodyweight": lambda d: d.groupby(["date", "exercise", "diet"])["metric_value"].max().reset_index(),
            "volume": lambda d: d.groupby(["date", "exercise", "diet"])["metric_value"].sum().reset_index(),
        }
    strat = METRIC_STRAT.get(type)
    if strat is None:
        raise ValueError(f"niezaimplemetnowny typ metryki: {type}")
    df = strat(df)
    return df

def calculate_progress(df: pd.DataFrame, flag: bool):
    if not flag: #jesli nie konczy sie "%" to znaczy ze nie chcemy edytowac metryki na procenty
        return df
    #tworymy kolumne z metryka z dnia zerowego dla kazdego cwiczenia
    day0 = df.groupby("exercise")["metric_value"].transform("first")
    #zamianiemy bazowa metryke na metryke procentowa
    df["metric_value"] = (df["metric_value"] - day0)/day0*100
    return df

def get_raw_dataframe(workouts_path: Path):
    df = pd.read_csv(workouts_path, parse_dates=['date'])#ustawiam aby daty byly type(date) a nie string
    return df

if __name__ == "__main__":
    print("--- TEST 1: ---")
    create_plt(config=config_weight_pct, workouts_path=WORKOUTS_PATH)
    input("Oczekiwanie: ")
    print("\n--- TEST 2:---")
    create_plt(config=config_volume_raw, workouts_path=WORKOUTS_PATH)
    input("Oczekiwanie: ")
    print("\n--- TEST 3:---")
    create_plt(config=config_volume_pct, workouts_path=WORKOUTS_PATH)
    input("Oczekiwanie: ")
    print("\n--- TEST 4:---")
    create_plt(config=config_ratio, workouts_path=WORKOUTS_PATH)
    input("Oczekiwanie: ")