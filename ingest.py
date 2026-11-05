import datetime as dt
from pathlib import Path

from constants import EXERCISES_LIST, TODAY_DATE


def show_screen(config: dict):
    width = 30
    print("SUMMARY".center(width, "="))
    if config["conf_type"] == "input":
        print(f"Date: {config["start_date"]} \nDiet type: {config["diet"]}\nBodyweight: {config["bodyweight"]}")
        
        for exercise, details in config["exercises_data"].items():
            print(f"{exercise}:")
            for metric, value in details.items():
                formated_value = ", ".join(str(r) for r in value) if isinstance(value, list) else f"{value}kg"
                print(f"    {metric:<7}: {formated_value}")
    
    elif config["conf_type"] == "plot":
        exercises = "\n"+ "   \n".join(config["exercises"])
        if config["period"]["mode"] == "count":
            print(f"Workouts: {config["period"]["value"]}\nDiet type: {config["diet"]}\nMetric: {config["type"]}\nExercises: {exercises}")
        elif config["period"]["mode"] == "dates":
            print(f"Dates: {config["period"]["start_date"]} - {config["period"]["end_date"]}\nDiet type: {config["diet"]}\nMetric: {config["type"]}\nExercises: {exercises}")
    print("="*width)

def get_data():
    while True:
        date = get_workout_date("Input workout date (empyt=today, DD.MM.YYYY): ")
        diet = get_recent_diet("What is your recent diet type: ")
        bodyweight = get_bodyweight("What is your today's bodyweight (empty = skip): ")
        exercises = get_exercises_list("What exercises do you want to entry (all or numbers with spaces): ")
        exercises_data = get_exercises_data(exercises)

        show_screen({"conf_type": "input", "start_date": date, "diet": diet, "bodyweight": bodyweight, "exercises_data": exercises_data})
        while True:
            confirmation = input("Confirm? (y/n): ").lower()
            if confirmation and confirmation[0] in ["y","n"]:
                break
        if confirmation[0] == "y":
            break
    
    return {"conf_type": "input", "start_date": date, "diet": diet, "bodyweight": bodyweight, "exercises": exercises_data}

def get_workout_date(message: str):
    while True:
        try:
            date_input = input(message)
            if not date_input:
                date_input = TODAY_DATE
                return date_input
            date_input = dt.datetime.strptime(date_input, "%d.%m.%Y").date()
            return date_input
        except ValueError:
            print("Invalid date!")

def get_recent_diet(message: str):
    diet_translation = {
                        "s": "surplus",
                        "m": "maintenance",
                        "d": "deficit",
                        "u": "unknown",
                        "a": "all"
                        }
    while True:
        diet_input = input(f"{message} \nsurplus/maintenance/deficit/unknown: ")
        #sprawdzamy czy zostalo cokowiek podane i sprawdzamy ierwsza litere
        if not diet_input:
            return diet_translation["a"]
        if diet_input[0].lower() in ["s", "m", "d", "u", "a"]:
            return diet_translation[diet_input[0].lower()]

def get_bodyweight(message: str):
    while True:
        try:
            input_bodyweight = input(message).replace(",",".")
            if input_bodyweight:
                bodyweight = abs(float(input_bodyweight))
            else: 
                bodyweight = ""
            break
        except ValueError:
            print("Number is expected")
    return bodyweight

def get_exercises_list(message: str):
    while True:
        today_exercises_list = [] #jakby error byl w locie to tworzymy pusta liste na poczatku
        for i, item in enumerate(EXERCISES_LIST):
            if i%3==0:
                print()
            if i>=9:
                print(f"{i+1}. {item:<30}", end="   ")
            else:#z nieznanego mi powodu bez tego printuje sie to troche nie równo xD
                print(f"{i+1}. {item:<31}", end="   ")
        try:
            today_exercises_input = input(f"\n\n{message}") #lista stringów z numerami cwiczen
            if today_exercises_input == "all" or not today_exercises_input:
                return EXERCISES_LIST
            today_exercises = today_exercises_input.split()
            for exercise in today_exercises:
                today_exercises_list.append(EXERCISES_LIST[int(exercise)-1])
            if today_exercises_list: #w razie pustej listy nas to ratuje
                return today_exercises_list
        except (ValueError, IndexError):
            print("Poza przedziałem!")

def get_exercises_data(exercises_list: list):
    exercises_data = {}
    for item in exercises_list:
        while True:
            try:
                print(f"Exercise: {item}")
                raw_reps = input("Input all reps separated by space: ").split()
                if not raw_reps:#musi byc minimum 1 seria
                    continue
                reps = [abs(int(rep)) for rep in raw_reps]  # castujemy liste na inty i lapiemy jesli ktos podal nieliczby
                weight = abs(float(input("Input weight: ").replace(",",".")))
                temp_exercise_dict = {"reps" : reps, "weight": weight} 
                break
            except ValueError:
                print("Invalid format!\nExample:\n  resp: 10 10 9\n weight:65,5")
        exercises_data[item] = temp_exercise_dict
    return exercises_data

def save_data_to_csv(path: Path, my_data: dict):
    if not path:
        print("save_data_to_csv nie otrzymal sciezki")
        return
    with open(path, mode="a", encoding="utf-8") as f:
        for exercise_name, details in my_data["exercises"].items():
            for set_number, rep in enumerate(details["reps"]):
                line = f"{my_data["start_date"]},{my_data["diet"]},{my_data["bodyweight"]},{exercise_name},{int(set_number)+1},{int(rep)},{details["weight"]}\n"
                f.write(line)
