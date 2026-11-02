# GymProgression CLI — Stan Projektu, Audyt i Architektura

> **Instrukcja dla asystenta AI / mentora w nowym oknie czatu:**
>
> Działasz jako wyrozumiały, ale technicznie bezkompromisowy Senior Data Engineer i osobisty mentor programowania. 
> Użytkownik studiuje informatykę (profil programistyczny) i uczy się Pythona, Pandasa, Matplotliba oraz czystej architektury oprogramowania poprzez budowę narzędzia CLI do analizy i prowadzenia treningu siłowego.
>
> **ZASADY BEZWZGLĘDNE DLA ASYSTENTA:**
> 1. **ZAKAZ VIBE CODINGU I GENEROWANIA GOTOWCÓW:** Pod żadnym pozorem nie generuj gotowych bloków kodu z rozwiązaniami całych funkcji ani modułów, dopóki użytkownik sam nie dojdzie do rozwiązania poprzez dedukcję i próby.
> 2. **METODA SOKRATEJSKA I MIKRO-KROKI:** Tłumacz koncepcje dogłębnie, zadawaj pytania naprowadzające, zmuszaj do wnioskowania z dokumentacji i logów błędów.
> 3. **ANGIELSKOJĘZYCZNY STANDARD KODU I UI:** Wszelkie identyfikatory, nazwy funkcji, zmiennych, etykiet, plików oraz teksty interfejsu CLI mają być w języku angielskim. Komentarze mogą pozostać po polsku.
> 4. **TESTOWANIE W LOCIE:** Wszelkie nowe mechanizmy testujemy w izolacji na syntetycznych danych (`workoutsTEST.csv`), zanim trafią do głównego potoku.
> 5. **CODE & UX REVIEW:** Dbaj o higienę pamięci, obsługę błędów, czystość typów oraz precyzyjny feedback dla użytkownika w terminalu.

---

## 1. Koncepcja, Cele Projektu i Wizja Produktowa

### Cel Użytkownika (Treningowy i Prywatny)
* **Koniec ze zgadywaniem na treningu:** Silnik podwójnej progresji (*double progression*) ma precyzyjnie dyktować obciążenie na kolejną sesję na podstawie ostatnich wyników i zdefiniowanych zakresów powtórzeń.
* **Szybkie wprowadzanie sesji (Quick Routines):** Wybór gotowego planu dnia (np. *Push A*, *Legs B*) z automatycznym podpowiadaniem ćwiczeń, docelowych serii i sugerowanego ciężaru.
* **Nienaruszalna historia (Append-Only Log):** Format CSV jako baza surowych faktów historycznych (brak mutacji przeszłości).
* **Wizualna korelacja diety i siły:** Wykresy wektorowe (SVG) prezentujące dynamikę obciążeń/objętości z nałożonymi fazami kalorycznymi (`surplus`, `maintenance`, `deficit`).

### Cel Inżynierski (Software Craftsmanship & Data Engineering)
* **Standard Tidy Data (1NF):** Dokładnie 1 wiersz = 1 seria robocza.
* **Separacja odpowiedzialności (SRP):** Wyraźne rozdzielenie modułów wprowadzania faktów (`ingest.py`), definicji planów (`routines.py`), transformacji analitycznych (`data_eng.py`), wizualizacji (`visualization.py`) i rekomendacji ciężaru (`progression.py`).
* **Spójność interfejsu (UX/DX):** Angielskojęzyczny, czytelny terminal z jasnym feedbackiem sukcesu/porażki i walidacją wejścia.

---

## 2. Raport Audytu Technicznego (Code Review & UX Audit)

### A. Błędy merytoryczne i literówki w kodzie (Bugs & Code Smells)
1. **Błąd w pisowni `unknow` zamiast `unknown`:**
   * Występuje w `DIET_COLORS`, słownikach `config_*`, domyślnych parametrach oraz w mapowaniu `diet_translation` w `ingest.py`. Należy zmigrować w całym projekcie i plikach CSV do poprawnego `unknown`.
2. **Hybrydowe nazewnictwo i literówka `RAPORTS_PATH`:**
   * W `data_eng.py` zdefiniowano `RAPORTS_PATH` (zbitka polskiego „raport” i angielskiego „path”). Prawidłowa nazwa to `REPORTS_PATH = BASE_DIRECTORY / "reports"`.
3. **Zmienna `axies` zamiast `ax` / `axes`:**
   * Słowo `axies` nie istnieje w języku angielskim. Pojedynczy układ współrzędnych to `ax`, a w liczbie mnogiej `axes`.
4. **Literówka w sygnaturze funkcji:**
   * W `filter_by_exercise(df=None, exericses=None)` parametr to `exericses`.
5. **Polskie nazwy zmiennych w pętli wizualizacji:**
   * Zmienne `data_od`, `data_do`, `dieta` w pętli `axvspan` zaburzają anglojęzyczny standard kodu (`start_date`, `end_date`, `diet_phase`).
6. **Brak zamykania ostatniego przedziału diety na wykresie:**
   * Linijka `timeline["next_date"] = timeline["date"].shift(-1)` wraz z `.dropna()` powoduje usunięcie ostatniego treningu z osi czasu. Jeśli użytkownik ma 1 trening, tło w ogóle się nie rysuje; jeśli ma 10 treningów, ostatni dzień nie ma tła. Prawidłowe podejście: wypełnienie ostatniej daty (`bfill`/wartość bieżącej daty sesji).

### B. Doświadczenie Użytkownika (UX Friction & Missing Feedback)
1. **Cichy zapis wykresu (Zero Feedback):**
   * Po wygenerowaniu wykresu w `create_plt()` funkcja zapisuje plik i natychmiast kończy działanie. Użytkownik w CLI nie wie, czy operacja się powiodła, ani gdzie fizycznie znajduje się plik.
   * *Wymóg:* Wyświetlenie w terminalu: `[SUCCESS] Chart saved to: reports/2026-11-02_22-30-00_weight.svg`.
2. **Mylący recykling promptów wprowadzania danych w filtrach wykresów:**
   * W `main.py` funkcja `create_plot_config()` wywołuje bezpośrednio `get_recent_diet()` z `ingest.py`, która wyświetla prompt: *"Input your today's diet type"*. Przy konfiguracji wykresu użytkownik NIE podaje swojej dzisiejszej diety, lecz wybiera filtr przeszłości.
   * Podobnie `get_exercises_list()` pyta o wykonane ćwiczenia, zamiast zapytać: *"Select exercises to display (comma-separated or 'all')"*.
3. **Niespójność językowa (Language Jumble):**
   * Menu główne jest po angielsku (`"Choose action:"`), po czym prompt wyboru zakresu przełącza się na język polski (`"Wybierz zakres (data/treningi): "`), a etykiety osi wykresu na `"Daty"` i `"OS Y"`.
   * Całe CLI oraz nazewnictwo wykresów musi przejść na czysty angielski.

---

## 3. Nowa Architektura: Rozdzielenie Ingestion vs Filtering

Aby wyeliminować mylące prompty, rozdzielamy funkcje wprowadzające fakty od funkcji konfigurujących zapytania analityczne:

```text
               CLI Router (main.py)
              /                    \
             /                      \
   [DATA INGESTION]           [ANALYTICS & PLOTTING]
   ingest.py                  query_prompts.py (lub wewnątrz main.py)
   --------------------       --------------------------------------
   - Prompt: Dzisiejsza data  - Prompt: Zakres dat lub N treningów
   - Prompt: Dzisiejsza waga  - Prompt: Filtr diety ("all" lub konkretna)
   - Prompt: Dzisiejsza dieta - Prompt: Ćwiczenia ("all" lub wybrane)
   - Prompt: Serie i powt.    - Prompt: Typ metryki wykresu
```

---

## 4. Projekt Modułu Planów Treningowych (`routines.json`)

Aby zrealizować Twój cel szybkiego wyboru treningu i umożliwić działanie silnikowi podwójnej progresji (Etap 5), wprowadzamy plik konfiguracyjny `config/routines.json`.

### Struktura pliku `config/routines.json`:
```json
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
      }
    ]
  }
}
```

### Przepływ Szybkiego Treningu (Quick Workout Flow):
1. Użytkownik wybiera z menu: `1. Log Workout`.
2. System pyta: `Choose input mode: [1] Quick Routine  [2] Custom / Freestyle`.
3. Wybór `1` wyświetla listę: `1. Push A`, `2. Pull A`.
4. Po wyborze `Push A` system automatycznie odpytuje historię z CSV dla każdego ćwiczenia z planu i wyświetla:
   ```text
   --- Exercise 1/2: Lawka plaska (Target: 3 sets of 8-10 reps) ---
   Last session: 60.0kg x [10, 10, 10] (Criteria met!)
   Suggested weight today: 62.5 kg
   Enter reps for 3 sets (separated by space): 
   ```

---

## 5. Dydaktyczna Roadmapa Edukacyjna

### Etapy 1–3: ETL, Czyszczenie i Matematyka Progresu — [UKOŃCZONE]
* [x] Wektorowy potok w Pandas (`ffill().bfill()`, `sort_values`).
* [x] Split-Apply-Combine (`groupby`) dla maksymalnego ciężaru i sumy objętości.
* [x] Wzór progresu procentowego $T_0$ za pomocą `.transform("first")`.

### Etap 4: Wizualizacja Danych (`matplotlib`) — [STATUS: DO PRZESTRONNEGO REFACTORU]
* [x] Podejście obiektowe (`fig, ax`).
* [x] Wieloliniowe wykresy ćwiczeń z dynamiczną legendą.
* [x] Tła faz kalorycznych (`axvspan`) z eliminacją kresek (`lw=0`).
* [x] Eksport wektorowy do SVG ze znacznikiem czasu (`timestamp`).
* [ ] **Zadania refaktoryzacyjne Etapu 4 do wykonania:**
  * Przeniesienie czystej funkcji rysującej do dedykowanego modułu lub ujednolicenie `data_eng.py`.
  * Korekta literówek (`unknown`, `REPORTS_PATH`, `ax`, angielskie nazwy zmiennych).
  * Dodanie jasnego komunikatu w konsoli z potwierdzeniem ścieżki zapisu pliku SVG.
  * Zastąpienie sztywnych etykiet osi X i Y dynamicznymi opisami w języku angielskim (`Date`, `Weight [kg]`, `Progress [%]`).

### Etap 5: Silnik Podwójnej Progresji i Konfiguracja Planów — [NASTĘPNY FOCUS]
* [ ] Implementacja odczytu `config/routines.json`.
* [ ] Funkcja analizy ostatniej sesji: wyciągnięcie ostatnich powtórzeń i ciężaru dla danego ćwiczenia.
* [ ] Algorytm decyzyjny podwójnej progresji:
  * Warunek awansu: Czy we wszystkich seriach roboczych osiągnięto górny limit powtórzeń (`rep_range[1]`)?
  * Jeśli TAK: `rekomendowany_ciężar = poprzedni_ciężar + weight_step`.
  * Jeśli NIE: `rekomendowany_ciężar = poprzedni_ciężar` (walka o brakujące powtórzenia).
* [ ] Interfejs szybkiego wprowadzania sesji zintegrowany z silnikiem rekomendacji.

---

## 6. Model Danych (SSOT — `spreadsheets/workouts.csv`)

| Kolumna | Typ w CSV | Typ docelowy w Pandas | Przykładowe wartości | Rola w systemie |
| :--- | :--- | :--- | :--- | :--- |
| `date` | `string (ISO)` | `datetime64[ns]` | `2026-10-28` | Chronologia sesji |
| `diet` | `string` | `category` | `surplus`, `maintenance`, `deficit`, `unknown` | Faza kaloryczna |
| `bodyweight` | `float / puste` | `float64` (z `ffill().bfill()`) | `78.5`, `NaN` | Waga ciała |
| `exercise` | `string` | `string` | `Lawka plaska`, `Martwy ciag` | Klucz ćwiczenia |
| `set_number` | `int` | `int64` | `1`, `2`, `3` | Numer serii |
| `reps` | `int` | `int64` | `10`, `12` | Wykonane powtórzenia |
| `weight` | `float` | `float64` | `60.0`, `102.5` | Ciężar roboczy w kg |