# GymProgression CLI — Stan Projektu, Audyt i Architektura

> **Instrukcja dla asystenta AI / mentora w nowym oknie czatu:**
>
> Działasz jako wyrozumiały, ale technicznie bezkompromisowy Senior Data Engineer i osobisty mentor programowania.
> Użytkownik studiuje informatykę (profil programistyczny) i uczy się Pythona, Pandasa, Matplotliba oraz czystej architektury oprogramowania poprzez budowę narzędzia CLI do analizy i prowadzenia treningu siłowego.
>
> **ZASADY BEZWZGLĘDNE DLA ASYSTENTA:**
>
> 1. **ZAKAZ VIBE CODINGU I GENEROWANIA GOTOWCÓW:** Pod żadnym pozorem nie generuj gotowych bloków kodu z rozwiązaniami całych funkcji ani modułów, dopóki użytkownik sam nie dojdzie do rozwiązania poprzez dedukcję, testy i analizę błędów.
>
> 2. **METODA SOKRATEJSKA I MIKRO-KROKI:** Tłumacz koncepcje dogłębnie, zadawaj pytania naprowadzające, zmuszaj do wnioskowania z logów błędów i dokumentacji.
>
> 3. **ANGIELSKOJĘZYCZNY STANDARD KODU I UI:** Wszelkie identyfikatory, nazwy funkcji, zmiennych, etykiet, plików oraz teksty interfejsu CLI mają być w języku angielskim. Komentarze mogą pozostać po polsku.
>
> 4. **TESTOWANIE W LOCIE:** Wszelkie nowe mechanizmy testujemy w izolacji na syntetycznych danych (`workoutsTEST.csv`), zanim trafią do głównego potoku.
>
> 5. **CODE & UX REVIEW:** Dbaj o higienę pamięci (`plt.close`), obsługę przypadków brzegowych (np. puste DataFrame'y) oraz precyzyjny feedback dla użytkownika w terminalu.

## 1. Koncepcja, Cele Projektu i Wizja Produktowa

### Cel Użytkownika (Treningowy i Prywatny)

* **Koniec ze zgadywaniem na treningu:** Silnik podwójnej progresji (*double progression*) ma precyzyjnie dyktować obciążenie na kolejną sesję na podstawie ostatnich wyników i zdefiniowanych zakresów powtórzeń.

* **Szybkie wprowadzanie sesji (Quick Routines):** Wybór gotowego planu dnia (np. *Push A*, *Legs B*) z automatycznym podpowiadaniem ćwiczeń, docelowych serii i sugerowanego ciężaru.

* **Nienaruszalna historia (Append-Only Log):** Format CSV jako baza surowych faktów historycznych (brak mutacji przeszłości).

* **Wizualna korelacja diety i siły:** Wykresy wektorowe (SVG) prezentujące dynamikę obciążeń/objętości z nałożonymi fazami kalorycznymi (`surplus`, `maintenance`, `deficit`).

### Cel Inżynierski (Software Craftsmanship & Data Engineering)

* **Standard Tidy Data (1NF):** Dokładnie 1 wiersz = 1 seria robocza.

* **Separacja odpowiedzialności (SRP):** Wyraźne rozdzielenie modułów wprowadzania faktów (`ingest.py`), definicji planów (`routines.py`), transformacji analitycznych (`data_eng.py`), wizualizacji (`data_eng.py` / docelowo `visualization.py`) i rekomendacji ciężaru (`progression.py`).

* **Spójność interfejsu (UX/DX):** Angielskojęzyczny, czytelny terminal z jasnym feedbackiem sukcesu/porażki i walidacją wejścia.

## 2. Model Danych (SSOT — `spreadsheets/workouts.csv`)

Układ tabelaryczny: **1 wiersz = 1 seria robocza**.

| Kolumna | Typ w CSV | Typ docelowy w Pandas | Przykładowe wartości | Rola w systemie | 
| ----- | ----- | ----- | ----- | ----- | 
| `date` | `string (ISO)` | `datetime64[ns]` | `2026-10-28` | Chronologia sesji | 
| `diet` | `string` | `category` | `surplus`, `maintenance`, `deficit`, `unknown` | Faza kaloryczna | 
| `bodyweight` | `float / puste` | `float64` (z `ffill().bfill()`) | `78.5`, `NaN` | Waga ciała | 
| `exercise` | `string` | `string` | `Lawka plaska`, `Martwy ciag` | Klucz ćwiczenia | 
| `set_number` | `int` | `int64` | `1`, `2`, `3` | Numer serii | 
| `reps` | `int` | `int64` | `10`, `12` | Wykonane powtórzenia | 
| `weight` | `float` | `float64` | `60.0`, `102.5` | Ciężar roboczy w kg | 

## 3. Stan Aktualny Implementacji (Changelog i Moduły)

### Moduł A: Wprowadzanie Danych (`ingest.py`) — STATUS: DZIAŁA (wymaga drobnego refaktoru sygnatur)

* Dynamiczne ścieżki oparte o `pathlib.Path`.

* Pętla wprowadzania daty (`%d.%m.%Y`), diety (`s/m/d/u/a`), wagi ciała.

* Wybór ćwiczeń z 3-kolumnowej siatki (`enumerate`) z obsługą `"all"`.

* Rejestrowanie powtórzeń i ciężaru per seria, atomowy zapis do CSV w kodowaniu `utf-8`.

* *Ostatnia zmiana:* Dodanie parametru `message: str` do funkcji pobierających dane w celu reużywalności w modułach analitycznych.

### Moduł B: Router CLI (`main.py`) — STATUS: DZIAŁA

* Menu główne oparte o Dispatch Table (`menu_actions`).

* Funkcja `create_plot_config()` zbierająca filtry użytkownika (zakres dat lub liczba ostatnich treningów, dieta, lista ćwiczeń, metryka).

* Zsynchronizowana lista `PLOT_TYPE`.

### Moduł C: Potok Analityczny i Wizualizacja (`data_eng.py`) — STATUS: ETAP 4 UKOŃCZONY (PROTOTYP)

* **ETL:** Wektorowy potok (`get_prepared_dataframe`, `filter_by_*`, `add_metric_column`, `aggregate_metrics`, `calculate_progress`).

* **Wizualizacja (Matplotlib OO):**

  * Płótno `fig, ax = plt.subplots(figsize=(10, 6))`.

  * Rysowanie serii w pętli `for exercise, df_grouped in df.groupby("exercise"): ax.plot(...)`.

  * Automatyczne pasy tła diety (`ax.axvspan`) na bazie osi czasu (`timeline`) wyliczonej przez `.shift(-1)` i `.dropna()`.

  * Eliminacja nakładających się obramowań prostokątów za pomocą `lw=0`.

  * Filtrowanie duplikatów diety w legendzie (`diet_added_to_label`).

  * Formatowanie dat `fig.autofmt_xdate()`.

  * Eksport wektorowy do SVG w katalogu raportów ze znacznikiem czasu (`%Y-%m-%d_%H-%M-%S`) i bezpieczną nazwą metryki (`.replace("/", "_")`).

  * Higiena pamięci RAM (`plt.close(fig)`).

## 4. Rejestr Długu Technicznego i UX (Backlog do wdrożenia)

### Priorytet 1: Błędy krytyczne i sygnatury (Fixes)

1. **Domyślne parametry `message` w `ingest.py`:**

   * Po dodaniu parametru `message: str` do `get_workout_date`, `get_recent_diet`, `get_bodyweight` funkcja `get_data()` rzuca `TypeError`, jeśli wywoła się je bez argumentów.

   * *Rozwiązanie:* Dodać wartości domyślne w sygnaturach, np. `def get_workout_date(message: str = "Podaj date (DD.MM.YYYY/pusty=dzis): "):`.

2. **Spójność wartości filtra diety (`"unknown"` vs `"all"`):**

   * Filtr `filter_by_diet` sprawdza `if diet == "all": return df`. W słownikach testowych `config_*` należy upewnić się, że testy globalne używają `"all"`, a nie `"unknown"`.

### Priorytet 2: Doświadczenie Użytkownika (UX & Defensive Programming)

1. **Zabezpieczenie przed pustym DataFrame (`df.empty` Guard):**

   * Jeśli użytkownik wybierze filtry, dla których nie ma danych w CSV (np. ćwiczenie, którego nie robił w danym okresie), funkcja `create_plt()` generuje pusty plik i rzuca `UserWarning` o braku etykiet w legendzie.

   * *Wymóg:* Zaraz po `df = transform_data(df, config)` dodać sprawdzenie `if df.empty:` – wyświetlić czytelny komunikat: `[WARNING] No workout records match the selected criteria. Plot generation aborted.` i przerwać funkcję przed dotknięciem Matplotliba.

2. **Ekran podsumowania konfiguracji wykresu (Confirmation Screen):**

   * Wzorem `show_screen()` z `ingest.py`, przed wygenerowaniem wykresu w `create_plot_config()` w `main.py` wyświetlić podsumowanie wybranych parametrów (ćwiczenia, okres, dieta, typ wykresu) i zapytać użytkownika: `Confirm plot generation? (y/n): `.

3. **Ujednolicenie katalogu raportów:**

   * W kodzie pojawia się `REPORTS_PATH = BASE_DIRECTORY / "output"`. Zgodnie ze standardem projektu zmieniamy na `REPORTS_PATH = BASE_DIRECTORY / "reports"`.

4. **Dynamiczne i angielskojęzyczne etykiety osi:**

   * Zastąpić sztywne `ax.set_xlabel("Daty")` oraz `ax.set_ylabel(config["type"])` czytelnymi podpisami w języku angielskim:

     * Oś X: `"Date"`

     * Oś Y: Dynamicznie w zależności od metryki (`"Weight [kg]"`, `"Volume [kg * reps]"`, `"Progress [%]"`).

## 5. Projekt Modułu Planów Treningowych (`config/routines.json`)

Fundament pod szybkie wprowadzanie sesji oraz silnik podwójnej progresji (Etap 5).

### Struktura pliku `config/routines.json`:

```
{
  "routines": {
    "Push A": [
      {
        "exercise": "Lawka plaska",
        "target_sets": 3,
        "rep_range": [8, 10],
        "weight_step": 2.5
      },
      {
        "exercise": "Wznosy bokiem",
        "target_sets": 3,
        "rep_range": [10, 12],
        "weight_step": 1.0
      }
    ],
    "Pull A": [
      {
        "exercise": "Podciaganie",
        "target_sets": 3,
        "rep_range": [6, 8],
        "weight_step": 2.5
      },
      {
        "exercise": "Wioslowanie hantlem",
        "target_sets": 3,
        "rep_range": [8, 10],
        "weight_step": 2.0
      }
    ]
  }
}

```

### Przepływ Szybkiego Treningu (Quick Workout Flow w CLI):

1. Menu: `1. Input data` -> Użytkownik wybiera: `[1] Quick Routine  [2] Custom / Freestyle`.

2. Przy wyborze `[1]` system wyświetla zdefiniowane plany (`Push A`, `Pull A`).

3. Po wybraniu planu system w pętli przechodzi przez ćwiczenia zdefiniowane w planie:

   * Odpytuje historię z bazy CSV dla danego ćwiczenia.

   * Silnik progresji oblicza sugerowany ciężar.

   * Użytkownik podaje tylko wykonane powtórzenia (oraz opcjonalnie modyfikuje ciężar, jeśli zmienił zdanie).

## 6. Specyfikacja Silnika Podwójnej Progresji (Etap 5 — `progression.py`)

### Matematyczno-Logiczny Algorytm Decyzyjny

Dla każdego ćwiczenia z planu sprawdzana jest **ostatnia zarejestrowana sesja** (`date == max(date)` dla danego `exercise`):

1. **Warunek sukcesu (Progression Criterion Met):**

   * Czy liczba wykonanych serii jest równa `target_sets`?

   * Czy we **wszystkich** seriach roboczych osiągnięto górny limit powtórzeń (`rep >= rep_range[1]`)?

2. **Decyzja o obciążeniu:**

   * **TAK:**
     

     $$
     \text{suggested\_weight} = \text{last\_weight} + \text{weight\_step}
     $$

     
     Komunikat CLI: `[TARGET REACHED] All sets hit upper rep limit! Increasing weight by +{weight_step}kg.`

   * **NIE:**
     

     $$
     \text{suggested\_weight} = \text{last\_weight}
     $$

     
     Komunikat CLI: `[IN PROGRESS] Target not reached yet. Stay at {last_weight}kg and fight for more reps.`

## 7. Dydaktyczna Roadmapa Edukacyjna

### Etapy 1–3: ETL, Czyszczenie i Matematyka Progresu — \[UKOŃCZONE\]

* \[x\] Wektorowy potok w Pandas (`ffill().bfill()`, `sort_values`).

* \[x\] Split-Apply-Combine (`groupby`) dla maksymalnego ciężaru i sumy objętości.

* \[x\] Wzór progresu procentowego $T_0$ za pomocą `.transform("first")`.

### Etap 4: Wizualizacja Danych (`matplotlib`) — \[STATUS: ZAKOŃCZONY / WYMAGA PORZĄDKÓW BACKLOGU\]

* \[x\] Podejście obiektowe (`fig, ax`).

* \[x\] Wieloliniowe wykresy ćwiczeń z dynamiczną legendą.

* \[x\] Tła faz kalorycznych (`axvspan`) z eliminacją kresek (`lw=0`).

* \[x\] Eksport wektorowy do SVG ze znacznikiem czasu (`timestamp`).

* \[ \] *Drobne zadania z backlogu:* Guard `df.empty`, ekran potwierdzenia wykresu, angielskie opisy osi.

### Etap 5: Silnik Podwójnej Progresji i Konfiguracja Planów — \[AKTUALNY FOCUS\]

* \[ \] Utworzenie i wczytywanie pliku `config/routines.json`.

* \[ \] Funkcja `get_last_exercise_performance(df, exercise)` wyciągająca ostatni ciężar i serię powtórzeń.

* \[ \] Moduł decyzyjny `calculate_next_target(history_data, exercise_config)`.

* \[ \] Integracja szybkiego wprowadzania treningu z podpowiedziami ciężaru w CLI.