import datetime as dt
from pathlib import Path

#daty i czas
TODAY_DATE = dt.date.today()

#sciezki
BASE_DIRECTORY = Path(".")
WORKOUTS_PATH = BASE_DIRECTORY / "spreadsheets" / "workoutsTEST.csv"
REPORTS_DIR_PATH = BASE_DIRECTORY / "reports"

#listy
PLOT_TYPE = [
    "weight", 
    "weight/bodyweight", 
    "volume", 
    "weight progress in %", 
    "weight/bodyweight progress in %", 
    "volume progress in %"
]

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

#slowniki
DIET_COLORS = {
    "surplus": "green",
    "maintenance": "blue",
    "deficit": "red",
    "unknown": "gray"
}
