# language: pl
# Zgodne z: FUNCTIONAL_REQUIREMENTS.md §2.1, §4, §6, §7, §8, §9
# Nie zautomatyzowane — czysta specyfikacja Gherkin, patrz README.md w tym katalogu.

Funkcja: Zarządzanie pracownikami
  Jako zalogowany użytkownik
  chcę dodawać, edytować, usuwać i przeglądać pracowników
  aby mieć aktualną i poprawną listę zespołu

  Scenariusz: Dodanie pracownika pojawia się na liście
    Zakładając że jestem zalogowany
    Gdy wypełnię formularz poprawnym imieniem, wynagrodzeniem, wiekiem i stanowiskiem
    Oraz kliknę "Add"
    Wtedy nowy wiersz z tym pracownikiem pojawia się w tabeli
    Oraz formularz czyści się i wraca do trybu "Add Employee"
    # Pokrycie automatyczne: SEL-EMP-01, FT-WF-02

  Scenariusz: Edycja pracownika aktualizuje jego dane w tabeli
    Zakładając że na liście jest już jakiś pracownik
    Gdy kliknę "Edit" przy jego wierszu
    Wtedy formularz wypełnia się jego danymi, a przycisk "Add" zmienia się na "Update"
    Gdy zmienię jego wynagrodzenie i kliknę "Update"
    Wtedy wiersz w tabeli pokazuje nowe wynagrodzenie
    # Pokrycie automatyczne: SEL-EMP-02, FT-WF-03

  Scenariusz: Usunięcie pracownika usuwa go z tabeli
    Zakładając że na liście jest już jakiś pracownik
    Gdy kliknę "Delete" przy jego wierszu
    Wtedy pracownik znika z tabeli
    # Pokrycie automatyczne: SEL-EMP-03, FT-WF-05

  Szablon scenariusza: Niepoprawne dane w formularzu są odrzucane z czytelnym komunikatem
    Zakładając że jestem zalogowany
    Gdy wypełnię formularz, podając w polu "<pole>" wartość "<niepoprawna_wartosc>"
    Oraz kliknę "Add"
    Wtedy widzę czerwony komunikat błędu
    Oraz żaden nowy wiersz nie pojawia się w tabeli

    Przykłady:
      | pole   | niepoprawna_wartosc |
      | Age    | 10                   |
      | Age    | 70                   |
      | Salary | 0                    |
      | Salary | 250000               |
      | Name   | !!Invalid!!          |
    # Pokrycie automatyczne: SEL-EMP-04, FT-VAL-03, FT-VAL-05, FT-VAL-07

  Scenariusz: Stanowisko można wybrać tylko z zamkniętej listy opcji
    Zakładając że jestem na formularzu dodawania pracownika
    Gdy otworzę rozwijaną listę "Position"
    Wtedy widzę wyłącznie opcje: Junior QA, Mid QA, Senior QA, QA Lead
    Oraz nie mam możliwości wpisania własnej, dowolnej wartości
    # Pokrycie automatyczne: FT-VAL-08, FT-VAL-09, FT-VAL-10

  Scenariusz: Anulowanie resetu danych zachowuje istniejących pracowników
    Zakładając że na liście jest przynajmniej jeden pracownik
    Gdy kliknę "Reset Data"
    Wtedy pojawia się modal z ostrzeżeniem, że operacja jest nieodwracalna
    Gdy w modalu kliknę "Cancel"
    Wtedy modal się zamyka, a pracownik nadal jest widoczny na liście
    # Pokrycie automatyczne: SEL-EMP-05

  Scenariusz: Potwierdzenie resetu czyści całą listę
    Zakładając że na liście jest przynajmniej jeden pracownik
    Gdy kliknę "Reset Data"
    Oraz w modalu kliknę "Delete All"
    Wtedy tabela pracowników jest pusta
    Oraz jeśli formularz był w trybie edycji, wraca do trybu "Add Employee"
    # Pokrycie automatyczne: SEL-EMP-06, FT-WF-07
