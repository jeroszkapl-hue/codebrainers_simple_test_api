# Testy akceptacyjne (UAT)

Ten katalog zawiera testy akceptacyjne — spisane z perspektywy użytkownika,
nie implementacji. Odpowiadają na pytanie "czy aplikacja robi to, czego
oczekuje użytkownik/biznes", a nie "czy ta funkcja zwraca poprawny kod
HTTP". Uzupełniają, a nie zastępują, `tests/unit`, `tests/integration`,
`tests/functional` i `tests/selenium`, które sprawdzają implementację.

**To nie jest zautomatyzowana warstwa testów.** Pliki `.feature` to
wyłącznie specyfikacja w składni Gherkin — nie ma tu step definitions ani
żadnego runnera (`behave`, `pytest-bdd` itp.), więc `pytest` ich nie
odpali i nic tu nie zostanie wykonane maszynowo. Są pomyślane jako:

1. czytelna, ustandaryzowana forma kryteriów akceptacji, którą może
   przeczytać i zweryfikować osoba nietechniczna (PO, QA robiący ręczny
   UAT przed wydaniem),
2. gotowy punkt wyjścia, gdyby kiedyś ktoś chciał je zautomatyzować
   (dodanie `pytest-bdd` + step defs mapujących kroki na istniejące
   fixture'y z `tests/selenium/conftest.py` byłoby stosunkowo małym
   krokiem — większość kroków UI już jest pokryta Selenium).

## Zawartość

| Plik | Obszar |
|---|---|
| `authentication.feature` | Logowanie, sesja, wylogowanie |
| `employee_management.feature` | Dodawanie/edycja/usuwanie pracowników, walidacja, reset danych |
| `theme.feature` | Motyw jasny/ciemny |
| `CHECKLIST.md` | Checklista do ręcznego odhaczenia podczas UAT, z miejscem na sign-off |

## Jak z tego korzystać

- **Ręcznie (UAT):** przejdź `CHECKLIST.md` scenariusz po scenariuszu na
  żywej instancji aplikacji, zaznacz wynik i podpisz się w kolumnach
  "Zweryfikował(a)" / "Data".
- **Jako źródło prawdy o kryteriach akceptacji:** każdy scenariusz w
  plikach `.feature` ma komentarz `# Pokrycie automatyczne: ...`
  wskazujący, które istniejące testy automatyczne (Selenium/functional/
  integration) już faktycznie sprawdzają dany przypadek technicznie.
  Scenariusze bez takiego komentarza nie mają dziś żadnego automatycznego
  pokrycia i są sprawdzane wyłącznie manualnie.

Kryteria są zgodne z `FUNCTIONAL_REQUIREMENTS.md` — w razie rozbieżności
to `FUNCTIONAL_REQUIREMENTS.md` jest źródłem prawdy co do wymagań, a te
pliki są ich odzwierciedleniem w formie scenariuszy.
