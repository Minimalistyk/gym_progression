# GymProgression CLI — Stan Projektu, Architektura i Kontekst

> **Instrukcja dla asystenta AI / mentora w nowym oknie czatu:**
>
> Działasz jako Senior Data Engineer i mentor programowania. Użytkownik uczy się Pythona pod kątem inżynierii danych poprzez budowę realnego narzędzia, a nie bierne oglądanie kursów.
>
> **ZASADA KRYTYCZNA:** Pod żadnym pozorem **nie podawaj gotowego kodu** bez wyraźnej, bezpośredniej prośby użytkownika. Twoim zadaniem jest robić Code Review, wskazywać błędy architektoniczne, pytać o decyzje inżynierskie i naprowadzać na właściwe biblioteki wbudowane oraz idiomy Pythona.

## 1. Koncepcja i Cele Projektu

### Cel Użytkownika (Wartość w życiu prywatnym)

* **Eliminacja zgadywania na treningu:** Program podaje dokładny cel na dziś (ciężar i powtórzenia) na podstawie reguły podwójnej progresji (*double progression*).

* **Zatrzymanie niszczenia historii:** Przejście z notatnika (gdzie stare wyniki były nadpisywane) na model *Append-Only Log* (dane historyczne są nienaruszalne).

* **Zrozumienie wpływu diety i masy ciała na siłę:** Analiza korelacji między stanem kalorycznym (deficyt, masa, utrzymanie), wahaniami wagi a tempem progresji.

* **Analiza trendów i wykrywanie plateau:** Docelowe generowanie wykresów objętości treningowej, grup mięśniowych i szacowanego 1RM w czasie.

### Cel Inżynierski (Wartość w karierze / Data Engineering)

* **Higiena środowiska:** Praca w odizolowanym `.venv`, zarządzanie zależnościami przez `requirements.txt`, linter i formatowanie przez `ruff`.

* **Projektowanie odpornych potoków wejściowych (Data Ingestion):** Walidacja typów (`try...except`), menu z indeksowaniem (`enumerate`), obsługa ścieżek i folderów.

* **Format Tidy Data (First Normal Form):** Model zapisu 1 wiersz = 1 seria, umożliwiający wektorowe kalkulacje w pandasie bez parsowania tekstu.

* **Zasada SSOT (Single Source of Truth):** Rozdzielenie surowych faktów od metryk pochodnych (wyliczanych w locie).

* **Architektura modularna CLI:** Przejście z monolitycznego skryptu do modułów o pojedynczej odpowiedzialności (`ingest`, `progression`, `cli`).

## 2. Model Danych (SSOT — Tidy Data)

Plik docelowy: `spreadsheets/workouts.csv`

Układ tabelaryczny: **Jeden wiersz reprezentuje dokładnie jedną wykonaną serię roboczą.**

| Kolumna | Typ techniczny | Format / Wartości | Rola w systemie | 
| ----- | ----- | ----- | ----- | 
| `date` | `string (ISO)` | `YYYY-MM-DD` | Identyfikator chronologiczny sesji | 
| `diet` | `string` | `surplus`, `maintenance`, `deficit`, `unknow` | Stan bilansu kalorycznego w ostatnich dniach | 
| `bodyweight` | `float` | Liczba dziesiętna (kropka) / `nan` | Waga ciała zawodnika w dniu treningu | 
| `exercise` | `string` | np. `Lawka plaska`, `Martwy ciag` | Klucz ćwiczenia (ujednolicone nazwy bez znaków PL) | 
| `set_number` | `int` | `1`, `2`, `3` ... | Kolejny numer serii w ramach danego ćwiczenia | 
| `reps` | `int` | Liczba całkowita | Zrealizowana liczba powtórzeń w tej serii | 
| `weight` | `float` | Liczba dziesiętna (kropka) | Ciężar roboczy na sztandze / hantlu (kg) | 

> **Zasada inżynierska:** Kolumny takie jak **Objętość serii** ($\text{weight} \times \text{reps}$) oraz **Objętość sesji / 1RM** **NIE SĄ ZAPISYWANE** w pliku. Wylicza je silnik analityczny w locie przy odczycie.

## 3. Schemat Działania: Input (Zrealizowany)

Przepływ modułu wprowadzania danych (`ingest`):

1. **Pobranie kontekstu sesji (raz na start):**

   * Data treningu (Enter = dzisiaj `date.today()`, opcjonalnie data historyczna `YYYY-MM-DD`).

   * Dieta z ostatnich 3 dni (`s` / `m` / `d` / `u` $\rightarrow$ mapowana na pełne słowa).

   * Waga ciała (float z zamianą przecinka na kropkę, opcjonalnie pusta $\rightarrow$ brak wagi).

2. **Pętla wyboru ćwiczeń:**

   * Wyświetlenie bazy ćwiczeń w 3 czytelnych kolumnach z numeracją (`enumerate`).

   * Użytkownik podaje ciąg numerów po spacji (np. `2 4 10`).

3. **Pobieranie wyników siłowych:**

   * Dla każdego wybranego ćwiczenia użytkownik podaje powtórzenia w seriach po spacji (np. `10 10 9`).

   * Użytkownik podaje ciężar roboczy (np. `62.5`).

4. **Ekran weryfikacji wpisu (Confirmation Step):**

   * Konsolowa karta `SUMMARY` z wyśrodkowanym nagłówkiem i sformatowanymi seriami.

   * Pytanie `Confirm? (y/n)`.

   * Po potwierdzeniu: atomowy zapis do pliku CSV (zagnieżdżona pętla rozwijająca serie do pojedynczych wierszy).

## 4. Schemat Działania: Output (Analityka i Decyzje — Do Zrobienia)

### Moduł A: Silnik Progresji (`progression.py`)

* **Pytanie biznesowe:** *„Robię dzisiaj Ławkę płaską. Ile kg założyć i ile powtórzeń wykonać?”*

* **Wejście:** Wybór ćwiczenia z listy.

* **Logika potoku (Pandas):**

  1. Wczytanie `workouts.csv` do DataFrame.

  2. Odfiltrowanie wierszy dla wybranego ćwiczenia.

  3. Wyciągnięcie rekordów z **ostatniej zarejestrowanej daty**.

  4. Analiza powtórzeń w seriach roboczych (algorytm podwójnej progresji, np. widełki 10–12 powt.):

     * Jeśli we wszystkich seriach osiągnięto górny limit (np. $\ge 12$ powtórzeń) $\rightarrow$ rekomendacja: **ciężar** $+2.5\text{ kg}$, cel: **10 powtórzeń**.

     * Jeśli nie dobito do limitu (np. serie `12, 11, 9`) $\rightarrow$ rekomendacja: **ten sam ciężar**, cel: **dobicie do 12 powtórzeń**.

     * Przypadek brzegowy: brak historii $\rightarrow$ prośba o podanie ciężaru bazowego.

* **Wyjście w konsoli:**

  ```
  [OSTATNI TRENING: 2026-10-20]
  Serie: 10, 10, 9 powtorzen | Ciezar: 60.0 kg | Dieta: deficit
  ------------------------------------------------------------
  CEL NA DZIS: 60.0 kg -> probuj osiagnac 3x12 powtorzen!
  
  ```

### Moduł B: Moduł Analityczny i Raporty (`analytics.py`)

* **Pytanie biznesowe:** *„Jak wygląda mój postęp siłowy i objętościowy w czasie w relacji do diety?”*

* **Metryki liczone w locie:**

  * $\text{Objętość serii} = \text{weight} \times \text{reps}$

  * $\text{Objętość treningu} = \sum(\text{Objętość serii per data})$

  * Szacowane $1\text{RM} = \text{weight} \times (1 + \frac{\text{reps}}{30})$ (wzór Epleya)

* **Wizualizacja:** Zapisywanie wykresów PNG do folderu `reports/` przy użyciu `matplotlib` / `seaborn`.


### Moduł C: Poprawki i drobne zmiany

**Wyświetlanie listy ćwiczeń**

1. Lista pokazuje sie w posortowanej postaci od najczęściej wybieranego ćwiczenia.

2. Lista wypisuje ćwiczenia w takich samych odstępach i rónych kolumnach po 3 ćwiczenia na wiersz

## 5. Stan Aktualny Implementacji (Changelog)

* [x] Utworzone repozytorium, środowisko `.venv` i `requirements.txt`.
* [x] Skonfigurowany linter `ruff`.
* [x] Pełny silnik wprowadzania danych (Faza 1):
  * Dynamiczne tworzenie folderu `spreadsheets/` i pliku `workouts.csv` oparte o `pathlib.Path`.
  * Obsługa daty (domyślnie dzisiaj lub z ręki).
  * Zbieranie diety i masy ciała z obsługą wartości pustych.
  * Wybór ćwiczeń po numerach (`enumerate`) w siatce 3-kolumnowej.
  * Zbieranie serii po spacji (`10 10 9`).
  * Formatowanie podsumowania (`show_screen`) i krok potwierdzenia (`Confirm? (y/n)`).
  * Płaski zapis atomowy w standardzie Tidy Data (1 wiersz = 1 seria).
* [x] Architektura modularna i Router CLI (Dawna Faza 3 — wykonana wcześniej):
  * Wydzielenie potoku wprowadzania danych do niezależnego modułu `ingest.py`.
  * Przebudowa `main.py` w czysty punkt startowy (Router).
  * Implementacja menu w oparciu o wzorzec Dispatch Table ze szczelną pętlą walidacji i izolacją wywołań akcji.

## 6. Roadmapa Projektu (Kolejne Kroki)

### Faza 2: Silnik Podwójnej Progresji (Pandas Engine) — NASTĘPNY ETAP

* [ ] Utworzenie modułu `progression.py` operującego na pandasie:
  * [ ] Wczytanie pliku `spreadsheets/workouts.csv` do `pd.DataFrame`.
  * [ ] Zabezpieczenie przed brakiem pliku lub pustą bazą (np. gdy użytkownik uruchomi cel przed pierwszym treningiem).
  * [ ] Filtrowanie po wybranym ćwiczeniu i wyznaczenie ostatniej daty (`df['date'].max()`).
  * [ ] Obliczenie aktualnego potencjału siłowego sesji (szacowane 1RM ze wzoru Epleya na najcięższej serii).
  * [ ] Implementacja reguły decyzyjnej podwójnej progresji (weryfikacja czy poprzedni cel powtórzeń został domknięty).
  * [ ] Opcjonalne przeliczenie obciążenia pod nową docelową liczbę powtórzeń (gdy użytkownik zmienia zakres).
  * [ ] Formatowanie i zwrot czytelnej rekomendacji przed treningiem.
* [ ] Podpięcie akcji z `progression.py` pod opcję menu `Create workout` w `main.py`.

### Faza 3: Metryki Pochodne i Wizualizacja (`analytics.py`)

* [ ] Wyliczanie objętości sesji, szacowanego 1RM oraz stosunku ciężaru do masy ciała w pandasie w locie (in-memory).
* [ ] Wykresy progresji w czasie (`matplotlib` / `seaborn`):
  * Podział na ćwiczenia / partie mięśniowe (mapowanie kategorii ze słownika metadanych).
  * Wizualizacja tła wykresu oznaczająca stan kaloryczny (surplus, maintenance, deficit).
* [ ] Zapisywanie raportów graficznych do dedykowanego katalogu `reports/`.

### Faza 4: Interfejs Prezentacyjny (Showcase na koło naukowe)

* [ ] Zbudowanie interaktywnego dashboardu webowego w `streamlit` zasilanego plikiem `workouts.csv`.