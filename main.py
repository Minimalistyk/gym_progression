import sys
from pathlib import Path

#moje pozostałe pliki
from ingest import get_data, save_data_to_csv

#constanty
BASE_DIRECTORY = Path(".")
WORKOUTS_PATH = BASE_DIRECTORY / "spreadsheets" / "workoutsTEST.csv"

def main_menu():
    #menu_actions zawiera krotki z funkcja oraz tekstem w menu
    menu_actions = {1:(input_data, "Input data"), 2:(create_plot, "Create plot"), 3:(create_workout, "Create workout"), 4:(end_program, "Exit")}
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
            except KeyError:
                pass
            except ValueError:
                pass
        #poza walidacja aby bledy w innych czesciach kodu nie wracaly az tutaj
        action()

def input_data():
    workout_data = get_data()
    save_data_to_csv(path = WORKOUTS_PATH, my_data = workout_data)

def create_plot():
    pass

def create_workout():
    pass

def end_program():
    sys.exit()

def main():
    WORKOUTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not WORKOUTS_PATH.exists():
        #jezeli sciezka nie istnieje tworzymy nowy csv i dajemy nazwy kolumn
        with open(WORKOUTS_PATH, mode="w") as workouts:
            workouts.write("date,diet,bodyweight,exercise,set_number,reps,weight\n")

    main_menu()

if __name__ == "__main__":
    main()


