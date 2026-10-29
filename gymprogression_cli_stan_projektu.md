# GymProgression CLI — Stan Projektu, Architektura i Kontekst Dydaktyczny

> **Instrukcja dla asystenta AI / mentora w nowym oknie czatu:**
>
> Działasz jako wyrozumiały, ale technicznie konkretny Senior Data Engineer i osobisty mentor programowania. 
> Użytkownik studiuje informatykę (profil programistyczny) i uczy się Pythona, Pandasa oraz Matplotliba poprzez budowę własnego narzędzia CLI do analizy treningu siłowego.
>
> **ZASADY BEZWZGLĘDNE DLA ASYSTENTA:**
> 1. **ZAKAZ VIBE CODINGU I GENEROWANIA GOTOWCÓW:** Pod żadnym pozorem nie generuj gotowych bloków kodu z rozwiązaniami całych funkcji wizualizacji, dopóki użytkownik sam nie dojdzie do rozwiązania.
> 2. **NAUKA PRZED POSTĘPEM (ETAP 4 — WIZUALIZACJA):** Użytkownik dawno nie korzystał z `matplotlib`. **NIE przechodź od razu do pisania docelowej funkcji `generate_plot`**. Zacznij od zwięzłego przypomnienia podejścia obiektowego (`fig`, `ax`) oraz daj użytkownikowi 1–2 małe, izolowane mini-zadania/drille do przetestowania w pliku testowym na syntetycznym zbiorze.
> 3. **MIKRO-KROKI I SOKRATEJSKIE PYTANIA:** Rozbijaj budowę wykresu na elementarne części: inicjalizacja płótna `Figure`/`Axes`, rysowanie pojedynczej serii `ax.plot()`, iteracja po grupach ćwiczeń, formatowanie dat na osi X, nakładanie tła diety (`axvspan`). Pytaj o zrozumienie i zmuszaj do wnioskowania.
> 4. **TESTOWANIE W LOCIE:** Wszelkie próby z biblioteką Matplotlib użytkownik wykonuje w izolowanym bloku testowym na syntetycznym pliku `workoutsTEST.csv`.
> 5. **CODE REVIEW:** Weryfikuj poprawność stylów Matplotliba i spójność kontraktów danych między modułami.

---

## 1. Koncepcja i Cele Projektu

### Cel Użytkownika (Prywatny)
* **Eliminacja zgadywania na treningu:** Wyznaczanie obciążeń na sesję na podstawie algorytmu podwójnej progresji (*double progression*).
* **Nienaruszalna historia (Append-Only Log):** Rejestr surowych faktów w CSV bez modyfikacji starych sesji.
* **Korelacja siły z dietą i wagą:** Analiza wpływu bilansu kalorycznego (`surplus`, `maintenance`, `deficit`) i masy ciała na dynamikę siły.

### Cel Inżynierski (Data Engineering & Software Craftsmanship)
* **Higiena środowiska:** Izolowane `.venv`, `requirements.txt` (w tym `pandas`, `numpy`, `matplotlib`).
* **Standard Tidy Data (1NF):** Model danych: dokładnie 1 wiersz = 1 seria robocza.
* **Zasada SSOT:** Rozdzielenie faktów od wyliczanych w locie metryk pochodnych.
* **Czysty potok analityczny:** Modułowość (CLI Router -> Ingestion -> Pipeline ETL Pandas -> Wizualizacja Matplotlib -> Silnik Progresji).

---

## 2. Model Danych (SSOT — `spreadsheets/workouts.csv`)

Układ tabelaryczny: **1 wiersz = 1 seria robocza**.

| Kolumna | Typ w CSV | Typ docelowy w Pandas | Przykładowe wartości | Rola w systemie |
| :--- | :--- | :--- | :--- | :--- |
| `date` | `string (ISO)` | `datetime64[ns]` | `2026-10-28` | Chronologia sesji |
| `diet` | `string` | `string / category` | `surplus`, `maintenance`, `deficit`, `unknow` | Bilans kaloryczny |
| `bodyweight` | `float / puste` | `float64` (z `ffill().bfill()`) | `78.5`, `NaN` | Waga ciała |
| `exercise` | `string` | `string` | `Lawka plaska`, `Martwy ciag` | Klucz ćwiczenia |
| `set_number` | `int` | `int64` | `1`, `2`, `3` | Numer serii w ćwiczeniu |
| `reps` | `int` | `int64` | `10`, `12` | Wykonane powtórzenia |
| `weight` | `float` | `float64` | `60.0`, `102.5` | Ciężar roboczy w kg |

---

## 3. Stan Aktualny Implementacji (Changelog i Kod)

### Moduł A: Wprowadzanie Danych (`ingest.py`) — STATUS: DZIAŁA
* Dynamiczne ścieżki oparte o `pathlib.Path`.
* Pętla wprowadzania daty (`%d-%m-%Y`), diety (`s/m/d/u`), wagi ciała.
* Wybór ćwiczeń z 3-kolumnowej siatki (`enumerate`).
* Zbieranie serii po spacji (`10 10 9`) i atomowy zapis Tidy Data do CSV w kodowaniu `utf-8`.

### Moduł B: Router CLI (`main.py`) — STATUS: DZIAŁA
* Menu główne oparte o Dispatch Table (`menu_actions`).
* Zbieranie konfiguracji wykresu w `create_plot_config()`.
* Zsynchronizowana lista `PLOT_TYPE` z nazwami metryk bazowych i modyfikatorów procentowych (`weight/bodyweight`).

### Moduł C: Potok Analityczny (`data_eng.py`) — STATUS: ETAPY 1–3 UKOŃCZONE
* Kompletny, wektorowy potok ETL:
  * `get_raw_dataframe()` — odczyt CSV z parsowaniem kolumny `date` na typ `datetime`.
  * `get_prepared_dataframe()` — chronologiczne sortowanie (`sort_values(ascending=True, ignore_index=True)`) oraz dwukierunkowa propagacja wagi (`ffill().bfill()`).
  * `filter_by_exercise()`, `filter_by_period()`, `filter_by_diet()` — wektorowa filtracja.
  * `add_metric_column()` — obliczanie metryk serii przez słownik strategii (`weight`, `weight/bodyweight`, `volume`).
  * `aggregate_metrics()` — redukcja serii do jednego punktu dziennego per ćwiczenie i dieta (`groupby(["date", "exercise", "diet"])`) z użyciem `.max()` dla ciężarów i `.sum()` dla objętości.
  * `calculate_progress()` — kalkulacja dynamiki procentowej względem sesji bazowej $T_0$ na bazie `.transform("first")` pogrupowanego po ćwiczeniu.
* Środowisko: doinstalowany pakiet `matplotlib==3.11.2`, zamrożony w `requirements.txt`.
* Środowisko testowe: utworzony syntetyczny zbiór `spreadsheets/workoutsTEST.csv` z wieloma sesjami, skokami ciężaru i brakami wagi do weryfikacji algorytmów.

### Backlog i dług technologiczny do zaadresowania:
1. **Rozbicie promptów CLI (UX Refactor):** W `main.py` funkcja `create_plot_config()` wywołuje bezpośrednio `get_recent_diet()` z `ingest.py`, która wyświetla prompt: *"Input your today's diet type"*. Należy rozdzielić wprowadzanie faktów treningowych od filtrowania analitycznego (dedykowana funkcja np. `select_diet_filter()` z komunikatem o filtrze historii).
2. **Szybkie wybory (Quick Presets):** Dodanie w CLI gotowych skrótów dla częstych analiz (np. "Ostatnie 5 treningów", "Wszystkie ćwiczenia z dziś").
3. **Konfiguracja celów treningowych (`user_config.json`):** Przygotowanie bazy pod Etap 5 — konfiguracja docelowych serii i zakresów powtórzeń (np. Ławka: 3 serie po 8–10 powtórzeń) w pliku konfiguracyjnym, z którego skorzysta silnik podwójnej progresji.

---

## 4. Dydaktyczna Roadmapa Edukacyjna

### Etap 1: Solidne Podstawy Pandasa i Czyszczenie Danych — [UKOŃCZONE]
* [x] Zrozumienie różnicy między `Series` a `DataFrame` oraz wektoryzacji.
* [x] Obsługa braków wagi: implementacja i zrozumienie mechanizmów `.ffill()` i `.bfill()` w czasie.
* [x] Wyeliminowanie `SettingWithCopyWarning` i unifikacja nazw kolumn.

### Etap 2: Agregacja Danych (Zrozumienie `groupby`) — [UKOŃCZONE]
* [x] Redukcja wielu serii z jednego dnia do pojedynczego punktu na wykres liniowy.
* [x] Zrozumienie paradygmatu Split-Apply-Combine.
* [x] Implementacja strategii agregacji: `.max()` dla obciążenia roboczego vs `.sum()` dla łącznej objętości sesji.

### Etap 3: Indeksowanie i Matematyka Progresu Procentowego — [UKOŃCZONE]
* [x] Normalizacja skali różnych ćwiczeń na wspólnym wykresie.
* [x] Implementacja wzoru $\frac{V_t - V_0}{V_0} \times 100\%$ dla punktu bazowego $T_0$.
* [x] Zrozumienie i wdrożenie metody `.transform("first")` z grupowaniem po ćwiczeniu.

### Etap 4: Wizualizacja Danych (`matplotlib.pyplot`) — [AKTUALNY FOCUS]
* [ ] **Mini-drille startowe:** Szybkie przypomnienie podejścia obiektowego (`fig, ax = plt.subplots()`), anatomii wykresu i metod konfiguracji osi (`ax.set_*`).
* [ ] **Rysowanie serii wieloliniowych:** Pętla `for exercise, group_df in df.groupby("exercise"):` nanosząca linie na wspólny `ax`.
* [ ] **Formatowanie:** Etykiety dat na osi X, dynamiczny tytuł i podpis osi Y (`kg` vs `%`), siatka pomocnicza (`grid`), czytelna legenda.
* [ ] **Strefy diety w tle:** Zrozumienie i implementacja kolorowych pasów tła (`ax.axvspan`) odpowiadających fazom kalorycznym (`surplus`, `maintenance`, `deficit`).
* [ ] **Eksport raportu:** Zapis wygenerowanego wykresu do pliku `reports/{timestamp}_{metric}.png` obok podglądu interaktywnego.

### Etap 5: Silnik Progresji (`progression.py`) — [OCZEKUJE]
* [ ] Wczytanie konfiguracji celów z `user_config.json`.
* [ ] Odpytanie ostatniej sesji danego ćwiczenia (`df['date'].max()`).
* [ ] Walidacja kryteriów podwójnej progresji (wszystkie serie w górnym limicie powtórzeń).
* [ ] Formułowanie rekomendacji obciążenia na kolejną sesję.