# Employee Manager — Wymagania aplikacji

## 1. Cel aplikacji

Aplikacja „Employee Manager” służy do zarządzania pracownikami poprzez:
- dodawanie pracowników,
- edycję danych pracownika,
- usuwanie pracowników,
- wyświetlanie listy pracowników,
- oznaczanie pracownika jako przebywającego na urlopie.

Aplikacja działa w modelu klient-serwer:
- backend: FastAPI,
- frontend: HTML + CSS + Vanilla JavaScript.

# 2. Funkcjonalności aplikacji

## 2.1 Zarządzanie pracownikami

Użytkownik powinien mieć możliwość:
- dodania nowego pracownika,
- edycji istniejącego pracownika,
- usunięcia pracownika,
- przeglądania listy pracowników.

# 3. Model pracownika

Pracownik powinien zawierać następujące pola:

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| id | integer | Tak | Unikalny identyfikator |
| name | string | Tak | Imię i nazwisko pracownika |
| salary | integer | Tak | Wynagrodzenie |
| age | integer | Tak | Wiek pracownika |
| position | enum/string | Tak | Stanowisko pracownika |
| on_leave | boolean | Tak | Status urlopu |

# 4. Walidacja danych

## 4.1 Pole Name

Pole `name`:
- musi być wymagane,
- minimalna długość: `1`,
- maksymalna długość: `50`,
- powinno akceptować:
  - litery,
  - cyfry,
  - pojedyncze spacje,
- nie powinno akceptować znaków specjalnych.

### Regex walidacyjny

```bash
^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż0-9]+(?: [A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż0-9]+)*$
```

## 4.2 Pole Salary

Pole `salary`:

* musi być typu integer,
* minimalna wartość: 1,
* maksymalna wartość: 200000.

## 4.3 Pole Age

Pole `age`:

* musi być typu integer,
* minimalna wartość: 18,
* maksymalna wartość: 65.

## 4.4 Pole Position

Pole `position`:

* musi być wymagane,
* powinno być wybierane wyłącznie z listy rozwijanej (dropdown),
* powinno obsługiwać wyłącznie następujące wartości:
    - Junior QA
    - Mid QA
    - Senior QA
    - QA Lead

## 4.5 Pole On Leave

Pole `on_leave`:

* powinno być typu boolean,
* powinno być prezentowane jako checkbox,
* domyślna wartość: false.

# 5. UI aplikacji
## 5.1 Navbar

Navbar powinien zawierać:

* logo aplikacji,
* przycisk zmiany motywu.

## 5.2 Motyw aplikacji

Aplikacja powinna obsługiwać:
* dark mode,
* light mode.

Wybrany motyw powinien:
* być zapisywany w localStorage,
* być przywracany po odświeżeniu strony.

# 6. Formularz pracownika
## 6.1 Formularz dodawania

Formularz powinien zawierać:

* pole `Name`,
* pole `Salary`,
* pole `Age`,
* dropdown `Position`,
* checkbox `On vacation`,
* przycisk `Add`.

## 6.2 Formularz edycji

Po kliknięciu przycisku `Edit`:

* formularz powinien zostać uzupełniony danymi pracownika,
* przycisk Add powinien zmienić się na Update,
* formularz powinien przejść w tryb edycji.

# 7. Dropdown stanowiska

Dropdown stanowiska:

* powinien posiadać placeholder: Select position,
* powinien uniemożliwiać wpisywanie własnych wartości,
* powinien pozwalać wyłącznie na wybór dostępnych opcji.

# 8. Checkbox urlopu

Checkbox:
* powinien umożliwiać oznaczenie pracownika jako będącego na urlopie,
* powinien być odznaczony domyślnie.

# 9. Tabela pracowników
## 9.1 Kolumny tabeli

Tabela powinna zawierać następujące kolumny:

| Kolumna | Opis |
|---|---|
| ID | Unikalny identyfikator pracownika |
| Name | Imię i nazwisko pracownika |
| Salary | Wynagrodzenie pracownika |
| Age | Wiek pracownika |
| Position | Stanowisko pracownika |
| Vacation | Status urlopu pracownika |
| Actions | Dostępne akcje |

## 9.2 Status urlopu

Kolumna `Vacation` powinna wyświetlać:

| Wartość | Znaczenie |
|---|---|
| ✅ | Pracownik przebywa na urlopie |
| ❌ | Pracownik nie przebywa na urlopie |


## 9.3 Akcje

Kolumna `Actions` powinna zawierać:

| Przycisk | Opis |
|---|---|
| Edit | Edycja danych pracownika |
| Delete | Usunięcie pracownika |

# 10. Obsługa błędów

## 10.1 Walidacja backendowa

Backend powinien zwracać błędy walidacyjne dla:
- niepoprawnego `name`,
- niepoprawnego `salary`,
- niepoprawnego `age`,
- niepoprawnego `position`.

## 10.2 Error Box

Frontend powinien:
- wyświetlać komunikaty błędów,
- prezentować je w czerwonym kontenerze,
- ukrywać sekcję błędów przy poprawnym żądaniu.


# 11. Dokumentacja API (swagger)

http://127.0.0.1:8000/docs

# 12. Wymagania techniczne

## 12.1 Frontend

Frontend powinien:
- korzystać z:
  - HTML,
  - CSS,
  - Vanilla JavaScript,
- używać Fetch API do komunikacji z backendem,
- dynamicznie aktualizować tabelę bez przeładowania strony,
- obsługiwać localStorage do zapisywania motywu aplikacji,
- renderować dane pracowników dynamicznie w tabeli HTML.

## 12.2 Backend

Backend powinien:
- być napisany w FastAPI,
- wykorzystywać Pydantic do walidacji danych,
- przechowywać dane w pamięci aplikacji (in-memory storage),
- obsługiwać REST API,
- zwracać odpowiedzi w formacie JSON,
- posiadać endpoint healthcheck.

## 12.3 Walidacja danych

Walidacja danych powinna być realizowana:
- po stronie backendu przy użyciu Pydantic,
- po stronie frontendu poprzez ograniczenia pól formularza.

## 12.4 Obsługiwane endpointy

| Metoda HTTP | Endpoint | Opis |
|---|---|---|
| GET | `/health` | Healthcheck API |
| GET | `/api/employees` | Pobranie listy pracowników |
| POST | `/api/employees` | Dodanie pracownika |
| PUT | `/api/employees/{id}` | Aktualizacja pracownika |
| DELETE | `/api/employees/{id}` | Usunięcie pracownika |

# 13. Wymagania UX/UI

## 13.1 Responsywność

Interfejs użytkownika powinien:
- poprawnie działać na desktopie,
- poprawnie skalować się na mniejszych ekranach,
- obsługiwać zawijanie elementów formularza (`flex-wrap`).

## 13.2 Wygląd aplikacji

UI powinno:
- posiadać nowoczesny wygląd,
- wykorzystywać rounded corners,
- posiadać shadows,
- posiadać hover effects,
- wykorzystywać spójny accent color,
- obsługiwać dark mode i light mode.

## 13.3 Formularz

Formularz powinien:
- wyraźnie wskazywać tryb:
  - Add Employee,
  - Edit Employee,
- podświetlać tryb edycji,
- czyścić pola po poprawnym zapisaniu danych.

## 13.4 Tabela

Tabela powinna:
- posiadać hover effect dla wierszy,
- być czytelna wizualnie,
- posiadać wyróżniony nagłówek,
- wyświetlać dane w sposób centralnie wyrównany.

## 14.5 Obsługa błędów

Komunikaty błędów powinny:
- być widoczne dla użytkownika,
- posiadać czerwone obramowanie,
- posiadać czerwone tło,
- znikać po poprawnym wykonaniu operacji.

# 14. Przykładowy obiekt pracownika

```json
{
  "id": 1,
  "name": "Patryk",
  "salary": 15000,
  "age": 29,
  "position": "Senior QA",
  "on_leave": true
}