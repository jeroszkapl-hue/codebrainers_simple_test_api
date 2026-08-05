# Checklista akceptacyjna (UAT)

Do ręcznego przejścia na żywej instancji aplikacji (`python run.py`) przed
wydaniem. Każdy wiersz odpowiada scenariuszowi w plikach `.feature` w tym
katalogu — kolumna "Scenariusz" wskazuje który.

Wynik: zaznacz **Pass** / **Fail** / **Blocked** (zablokowany przez inny
błąd) po ręcznym przejściu kroków.

## Logowanie i wylogowanie (`authentication.feature`)

| # | Scenariusz | Wynik | Zweryfikował(a) | Data | Uwagi |
|---|---|---|---|---|---|
| 1 | Poprawne dane logowania dają dostęp do aplikacji | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 2 | Niepoprawne dane logowania pokazują czytelny błąd | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 3 | Brak aktywnej sesji przekierowuje na ekran logowania | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 4 | Sesja wygasa automatycznie po 10 minutach | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 5 | Wylogowanie kończy sesję również po stronie serwera | ☐ Pass ☐ Fail ☐ Blocked | | | |

## Zarządzanie pracownikami (`employee_management.feature`)

| # | Scenariusz | Wynik | Zweryfikował(a) | Data | Uwagi |
|---|---|---|---|---|---|
| 6 | Dodanie pracownika pojawia się na liście | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 7 | Edycja pracownika aktualizuje jego dane w tabeli | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 8 | Usunięcie pracownika usuwa go z tabeli | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 9 | Niepoprawny wiek (10) jest odrzucany z komunikatem błędu | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 10 | Niepoprawny wiek (70) jest odrzucany z komunikatem błędu | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 11 | Niepoprawne wynagrodzenie (0) jest odrzucane z komunikatem błędu | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 12 | Niepoprawne wynagrodzenie (250000) jest odrzucane z komunikatem błędu | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 13 | Niepoprawne imię/nazwisko (znaki specjalne) jest odrzucane z komunikatem błędu | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 14 | Stanowisko można wybrać tylko z zamkniętej listy opcji | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 15 | Anulowanie resetu danych zachowuje istniejących pracowników | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 16 | Potwierdzenie resetu czyści całą listę | ☐ Pass ☐ Fail ☐ Blocked | | | |

## Motyw jasny/ciemny (`theme.feature`)

| # | Scenariusz | Wynik | Zweryfikował(a) | Data | Uwagi |
|---|---|---|---|---|---|
| 17 | Przełączenie motywu zmienia wygląd natychmiast | ☐ Pass ☐ Fail ☐ Blocked | | | |
| 18 | Wybrany motyw przetrwa odświeżenie strony | ☐ Pass ☐ Fail ☐ Blocked | | | |

## Sign-off

| Wersja aplikacji | Środowisko | Zweryfikował(a) | Data | Decyzja (Go / No-Go) |
|---|---|---|---|---|
| | | | | |
