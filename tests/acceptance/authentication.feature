# language: pl
# Zgodne z: FUNCTIONAL_REQUIREMENTS.md §10.4, §12.5
# Nie zautomatyzowane — czysta specyfikacja Gherkin, patrz README.md w tym katalogu.

Funkcja: Logowanie i wylogowanie
  Jako użytkownik Employee Managera
  chcę móc się zalogować i wylogować
  aby mieć dostęp do listy pracowników tylko podczas aktywnej, bezpiecznej sesji

  Scenariusz: Poprawne dane logowania dają dostęp do aplikacji
    Zakładając że jestem na stronie logowania
    Gdy wpiszę login "admin" i hasło "admin"
    Oraz kliknę "Sign in"
    Wtedy zostaję przekierowany na stronę główną
    Oraz widzę tabelę pracowników
    # Pokrycie automatyczne: SEL-LOGIN-01, FT-AUTH-01

  Scenariusz: Niepoprawne dane logowania pokazują czytelny błąd
    Zakładając że jestem na stronie logowania
    Gdy wpiszę login "admin" i błędne hasło
    Oraz kliknę "Sign in"
    Wtedy pozostaję na stronie logowania
    Oraz widzę czerwony komunikat błędu logowania
    # Pokrycie automatyczne: SEL-LOGIN-02, FT-AUTH-02

  Scenariusz: Brak aktywnej sesji przekierowuje na ekran logowania
    Zakładając że nie jestem zalogowany
    Gdy otworzę stronę główną bezpośrednio, wpisując jej adres
    Wtedy zostaję przekierowany na stronę logowania
    # Pokrycie automatyczne: SEL-LOGIN-03

  Scenariusz: Sesja wygasa automatycznie po 10 minutach
    Zakładając że jestem zalogowany
    Gdy od momentu zalogowania minie ponad 10 minut
    Oraz spróbuję wykonać dowolną akcję wymagającą zalogowania
    Wtedy zostaję automatycznie przekierowany na stronę logowania
    # Pokrycie automatyczne: test_expired_token_rejected (tests/integration/test_auth_flow.py)

  Scenariusz: Wylogowanie kończy sesję również po stronie serwera
    Zakładając że jestem zalogowany
    Gdy kliknę przycisk "Logout"
    Wtedy zostaję przekierowany na stronę logowania
    Oraz mój poprzedni token dostępu przestaje działać — nawet gdyby ktoś
      spróbował użyć go bezpośrednio przeciwko API z pominięciem UI
    # Pokrycie automatyczne: SEL-EMP-07, FT-AUTH-07, FT-AUTH-08,
    #   test_logout_removes_token_from_server_side_store
