import datetime as dt
import sys
from pathlib import Path

#moje pozostałe pliki
from data_eng import create_plt
from ingest import get_data, get_exercises_list, get_recent_diet, save_data_to_csv

#constanty
BASE_DIRECTORY = Path(".")
WORKOUTS_PATH = BASE_DIRECTORY / "spreadsheets" / "workouts.csv"
PLOT_TYPE = ["weight", "weight/bodyweight", "volume", "weight progress in %", "weight/bodyweight progress in %", "volume progress in %"
]
    
def main_menu():
    #menu_actions zawiera krotki z funkcja oraz tekstem w menu
    menu_actions = {1:(input_data, "Input data"), 2:(create_plot_config, "Create plot"), 3:(create_workout, "Create workout"), 4:(end_program, "Exit")}
    width = 30
    while True:
        print("MENU".center(width, "="))

        for key, value in menu_actions.items():
            line = f"{key}. {value[1]}"
            print(f"{line}".center(width, " "))

        print("=" * width)

        while True:
            try:
                action = menu_actions[int(input("Choose action: "))][0]
                break
            except (KeyError, ValueError):
                pass
        #poza walidacja aby bledy w innych czesciach kodu nie wracaly az tutaj
        action()

def input_data():
    workout_data = get_data()
    save_data_to_csv(path = WORKOUTS_PATH, my_data = workout_data)

def create_plot_config():
    #tutaj pytamy uzytkownika o parametry wykresu i nastepnie wysylamy je do 
    #zakres dat/liczba ostanich treningów
    #lista ćwiczeń
    #typ: ciężar w rep/ ciezar do masy ciala w rep/ progres % ciezaru wzgledem poprzedniej serii/ objetosc cwiczenia/ progress % objetosci cwiczenia

    exercises = get_exercises_list()
    diet = get_recent_diet()

    while True:
        choice = input("Wybierz zakres (data/treningi): ")

        if not choice:
            continue
        try:
            if choice[0].lower() == "d":
                date_input = input("Podaj date poczatkowa (DD-MM-YYYY): ")
                start_date = dt.datetime.strptime(date_input, "%d-%m-%Y").date()
                date_input = input("Podaj date koncowa (DD-MM-YYYY): ")
                end_date = dt.datetime.strptime(date_input, "%d-%m-%Y").date()
                period = {"mode": "dates", "start_date": start_date, "end_date":end_date}
            elif choice[0].lower() == "t":
                workout_count = int(input("Input how many workouts back from now you would like to see on a plot: "))
                period = {"mode": "count", "value": workout_count}
            else:
                continue
            break
        except ValueError:
            print("Invalid input")

    while True:
        try:
            for i, item in enumerate(PLOT_TYPE):
                print(f"{i+1}. {item}")
            plot_type = PLOT_TYPE[int(input("Podaj typ wykresu: "))-1]
            break
        except (ValueError, IndexError):
            pass
    config = {"period":period, "diet": diet, "exercises": exercises, "type":plot_type}
    create_plt(config, WORKOUTS_PATH)

def create_workout():
    pass

def end_program():
    sys.exit()

def main():
    WORKOUTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not WORKOUTS_PATH.exists():
        #jezeli sciezka nie istnieje tworzymy nowy csv i dajemy nazwy kolumn
        with open(WORKOUTS_PATH, mode="w", encoding="utf-8") as workouts:
            workouts.write("date,diet,bodyweight,exercise,set_number,reps,weight\n")

    main_menu()

if __name__ == "__main__":
    main()


