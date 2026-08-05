# language: pl
# Zgodne z: FUNCTIONAL_REQUIREMENTS.md §5.2
# Nie zautomatyzowane — czysta specyfikacja Gherkin, patrz README.md w tym katalogu.

Funkcja: Motyw jasny/ciemny
  Jako użytkownik
  chcę przełączać motyw aplikacji i mieć go zapamiętanym
  aby korzystać z aplikacji w preferowanym trybie wizualnym

  Scenariusz: Przełączenie motywu zmienia wygląd natychmiast
    Zakładając że jestem na stronie logowania lub stronie głównej
    Gdy kliknę przycisk zmiany motywu
    Wtedy wygląd aplikacji zmienia się między trybem jasnym i ciemnym bez przeładowania strony

  Scenariusz: Wybrany motyw przetrwa odświeżenie strony
    Zakładając że przełączyłem motyw na ciemny
    Gdy odświeżę stronę
    Wtedy aplikacja nadal wyświetla się w trybie ciemnym
    # Pokrycie automatyczne: SEL-LOGIN-04
