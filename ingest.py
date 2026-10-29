import datetime as dt

TODAY_DATE = dt.date.today()

EXERCISES_LIST = [
    "Przysiad ze sztanga",
    "Lawka plaska",
    "Martwy ciag",
    "Podciaganie",
    "Face pull",
    "Wznosy bokiem",
    "Plank",
    "Pompki",
    "Przysiad bulgarski",
    "Sciaganie wyciagu do klatki",
    "Wioslowanie hantlem",
    "OHP",
    "Rozpietki",
    "Biceps hantle siedzac",
    "Wyciskanie hantli skos dodatni",
    "Martwy rumunski",
    "Podciaganie australijskie",
    "Wyprosty nog na maszynie",
    "Lydki na palcach stojac",
    "Lydki na palcach siedzac",
    "Uginanie nog",
    "Gniecenie arbuza",
    "Odgniatanie arbuza",
    "Suwnica na nogi",
]

def show_screen(date = TODAY_DATE, diet = "unknow", bodyweight = None, exercises_data = None):
    width = 30
    print("SUMMARY".center(width, "="))
    print(f"Date: {date} \nDiet type: {diet}\nBodyweight: {bodyweight}")
    for exercise, details in exercises_data.items():
        print(f"{exercise}:")
        for metric, value in details.items():
            formated_value = ", ".join(str(r) for r in value) if isinstance(value, list) else f"{value}kg"
            print(f"    {metric:<7}: {formated_value}")
    print("="*width)

def get_data():
    while True:
        date = get_workout_date()
        diet = get_recent_diet()
        bodyweight = get_bodyweight()
        exercises = get_exercises_list()
        exercises_data = get_exercises_data(exercises)
        show_screen(date, diet, bodyweight, exercises_data)
        while True:
            confirmation = input("Confirm? (y/n): ").lower()
            if confirmation and confirmation[0] in ["y","n"]:
                break
        if confirmation[0] == "y":
            break
    
    return {"date": date, "diet": diet,"bodyweight": bodyweight ,"exercises": exercises_data}

def get_workout_date():
    while True:
        try:
            date_input = input("Podaj date (DD-MM-YYYY/pusty=dzis): ")
            if not date_input:
                date_input = TODAY_DATE
                return date_input
            date_input = dt.datetime.strptime(date_input, "%d-%m-%Y").date()
            return date_input
        except ValueError:
            print("Invalid date!")

def get_recent_diet():
    diet_translation = {
                        "s": "surplus",
                        "m": "maintenance",
                        "d": "deficit",
                        "u": "unknow"
                        }
    while True:
        diet_input = input("Input your today's diet type. \nsurplus/maintenance/deficit/unknow: ")
        #sprawdzamy czy zostalo cokowiek podane i sprawdzamy ierwsza litere
        if not diet_input:
            return diet_translation["u"]
        if diet_input[0].lower() in ["s", "m", "d", "u"]:
            return diet_translation[diet_input[0].lower()]

def get_bodyweight():
    while True:
        try:
            input_bodyweight = input("Input bodyweight kg: ").replace(",",".")
            if input_bodyweight:
                bodyweight = abs(float(input_bodyweight))
            else: 
                bodyweight = ""
            break
        except ValueError:
            print("Number is expected")
    return bodyweight

def get_exercises_list():
    while True:
        today_exercises_list = [] #jakby error byl w locie to tworzymy pusta liste na poczatku
        for i, item in enumerate(EXERCISES_LIST):
            if i%3==0:
                print("\n")
            if i>=9:
                print(f"{i+1}. {item:<30}", end="   ")
            else:#z nieznanego mi powodu bez tego printuje sie to troche nie równo xD
                print(f"{i+1}. {item:<31}", end="   ")
        try:
            today_exercises_input = input("\n\nPodaj numer/y ćwiczeń: ").split() #lista stringów z numerami cwiczen
            for exercise in today_exercises_input:
                today_exercises_list.append(EXERCISES_LIST[int(exercise)-1])
            if today_exercises_list: #w razie pustej listy nas to ratuje
                return today_exercises_list
        except (ValueError, IndexError):
            print("Poza przedziałem!")

def get_exercises_data(exercises_list = None):
    exercises_data = {}
    for item in exercises_list:
        while True:
            try:
                print(f"Ćwiczenie: {item}")
                raw_reps = input("Podaj l. powtórzeń (serie odzielone spacją): ").split()
                if not raw_reps:#musi byc minimum 1 seria
                    continue
                reps = [abs(int(rep)) for rep in raw_reps]  # castujemy liste na inty i lapiemy jesli ktos podal nieliczby
                weight = abs(float(input("Podaj ciężar: ").replace(",",".")))
                temp_exercise_dict = {"reps" : reps, "weight": weight} 
                break
            except ValueError:
                print("Podawaj liczby!")
        exercises_data[item] = temp_exercise_dict
    return exercises_data

def save_data_to_csv(path = None, my_data = None):
    if not path:
        print("save_data_to_csv nie otrzymal sciezki")
        return
    with open(path, mode="a", encoding="utf-8") as f:
        for exercise_name, details in my_data["exercises"].items():
            for set_number, rep in enumerate(details["reps"]):
                line = f"{my_data["date"]},{my_data["diet"]},{my_data["bodyweight"]},{exercise_name},{int(set_number)+1},{int(rep)},{details["weight"]}\n"
                f.write(line)
