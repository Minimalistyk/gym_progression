from pathlib import Path

import pandas as pd

#na potrzebny testów
BASE_DIRECTORY = Path(".")
WORKOUTS_PATH = BASE_DIRECTORY / "spreadsheets" / "workoutsTEST.csv"
# 1. Test zakresu dat (mode: "dates") — maksymalny ciężar roboczy ("weight")
# Test A: Progres % ciężaru (powinno pokazać: 0%, +4.17%, +8.33%, +16.67%)
config_weight_pct = {
    "exercises": ["Lawka plaska", "Wznosy bokiem"],
    "period": {"mode": "dates", "start_date": "2026-10-01", "end_date": "2026-10-20"},
    "diet": "unknow",
    "type": "weight progress in %"
}

# Test B: Zwykła objętość (volume) z ostatnich 3 sesji
config_volume_raw = {
    "exercises": ["Lawka plaska"],
    "period": {"mode": "count", "value": 3},
    "diet": "unknow",
    "type": "volume"
}

# Test C: Progres % objętości (volume progress in %)
config_volume_pct = {
    "exercises": ["Lawka plaska"],
    "period": {"mode": "count", "value": 4},
    "diet": "unknow",
    "type": "volume progress in %"
}

# Test D: Stosunek ciężaru do masy ciała (weight/bodyweight)
config_ratio = {
    "exercises": ["Przysiad ze sztanga"],
    "period": {"mode": "dates", "start_date": "2026-10-01", "end_date": "2026-10-20"},
    "diet": "unknow",
    "type": "weight/bodyweight"
}

def create_plt(config = None, workouts_path = None):
    df = get_raw_dataframe(workouts_path)
    df = get_prepared_dataframe(df)
    df = filter_by_exercise(df,config["exercises"])
    df = filter_by_period(df,config["period"])
    df = filter_by_diet(df, config["diet"])
    base_metric = config["type"].split(" ")[0]
    df = add_metric_column(df, base_metric)
    df = aggregate_metrics(df, base_metric)
    is_progres_metric = config["type"].endswith("%")
    df = calculate_progress(df, is_progres_metric)
    print(df)
    #print(df[["date", "diet", "exercise", "metric_value"]])

def get_prepared_dataframe(df=None):
    df = df.sort_values("date", ascending=True, ignore_index = True)#mozna wprowadzac daty w roznej kolejnosci, weic je sortujemy
    df["bodyweight"] = df["bodyweight"].ffill().bfill()#uzupelniamy puste miejsca z waga
    return df

def filter_by_exercise(df=None, exericses=None):
    return df[df["exercise"].isin(exericses)]

def filter_by_period(df=None, period=None):
    if period["mode"] == "dates":
        start = pd.to_datetime(period["start_date"])
        end = pd.to_datetime(period["end_date"])
        return df[(df["date"]>=start)&(df["date"]<=end)]
    else:
        n = period["value"]
        target_dates = df["date"].drop_duplicates().sort_values().tail(n)
        return df[df["date"].isin(target_dates)]
    
def filter_by_diet(df=None, diet=None):
    if diet == "unknow":
        return df
    return df[df["diet"] == diet]

def add_metric_column(df=None, type=None):
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

def aggregate_metrics(df=None, type=None):
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

def calculate_progress(df, flag):
    if not flag: #jesli nie konczy sie "%" to znaczy ze nie chcemy edytowac metryki na procenty
        return df
    #tworymy kolumne z metryka z dnia zerowego dla kazdego cwiczenia
    day0 = df.groupby("exercise")["metric_value"].transform("first")
    #zamianiemy bazowa metryke na metryke procentowa
    df["metric_value"] = (df["metric_value"] - day0)/day0*100
    return df



def get_raw_dataframe(workouts_path = None):
    df = pd.read_csv(workouts_path, parse_dates=['date'])#ustawiam aby daty byly type(date) a nie string
    return df

if __name__ == "__main__":
    print("--- TEST 1: ---")
    create_plt(config=config_weight_pct, workouts_path=WORKOUTS_PATH)

    print("\n--- TEST 2:---")
    create_plt(config=config_volume_raw, workouts_path=WORKOUTS_PATH)

    print("\n--- TEST 3:---")
    create_plt(config=config_volume_pct, workouts_path=WORKOUTS_PATH)

    print("\n--- TEST 4:---")
    create_plt(config=config_ratio, workouts_path=WORKOUTS_PATH)