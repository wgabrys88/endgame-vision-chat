# endgame-vision-chat

Warstwa **oczu** dla [endgame-ai](https://github.com/wgabrys88/endgame-ai) i linii Franz.

Nie zastępuje `gui.py` (UI Automation). Dokłada to, czego UIA nie widzi:
obraz, kursor namalowany na zrzucie, wycinek konkretnego okna, współrzędne
normalized 0..1000, oraz **stateless user prompt** — model dostaje „gdzie
jestem teraz”, nie historię czatu.

Źródło `winapi.py`: `windows-ai-agent-toolset-v2.5-modular` (Franz),
przywołane tutaj. Zmiana: kursor rysuje się **zawsze** (jeśli systemowy
jest ukryty — strzałka `IDC_ARROW` w `GetCursorPos`).

## Po co

1. Agent mówi „zakończono”, a praca trwa. Stopka commita / odpowiedzi
   jest jedynym sygnałem.
2. Kontrola czatu z modelem wizyjnym = analiza pełnego obrazu, potem
   kawałka (okno / miejsce) w normalized coordinates.
3. User jest stateless: „pracuję w aplikacji X, zrobiłem costs, szukam
   przycisku scroll”. System prompt stoi w miejscu (cache). User prompt
   się zmienia.

## Pliki

| plik | rola |
|---|---|
| `winapi.py` | GDI zrzut + `DrawIconEx` + mysz/klawiatura. Tylko Windows. |
| `coords.py` | 0..1 ↔ 0..1000 ↔ piksel. Działa wszędzie. |
| `stateless_prompt.py` | Budowa user promptu „gdzie jestem”. |
| `vision_frame.py` | Jedna klatka: full PNG + crop PNG + prompt. |
| `agent_status.py` | Stopka `praca nadal trwa, pozostałe items todo list:`. |
| `test_protocol.py` | Testy bez Win32. |

## Protokół stopki (czytaj od dołu)

```
PRACA_NADAL_TRWA
praca nadal trwa, pozostałe items todo list:
- [ ] podpiąć grab() do Wheel._refresh_environment
- [ ] live run na Windows z costs / scroll
```

Albo naprawdę koniec:

```
ZAKONCZONO
praca nadal trwa, pozostałe items todo list:
(brak)
```

Słowo „koniec” w środku odpowiedzi **nie liczy się**. Liczy się stopka.

## Użycie na Windows

```python
from vision_frame import grab
from agent_status import status_from_items

frame = grab(
    goal="znajdź kontrolkę dalej na liście",
    looking_for="przycisk scroll albo koniec listy costs",
    last_effect="otwarto costs",
    last_cost_tokens=2100,
    crop_title="Chrome",   # albo crop_box=(0.1, 0.05, 0.9, 0.95)
    turn=7,
)
# frame.full_png, frame.crop_png, frame.user_prompt
# model dostaje 2 obrazy + frame.user_prompt
```

Współrzędne kliknięcia: `CLICK 412 780` w skali 0..1000 względem
obrazu, o którym mowa (full albo crop).

## Test bez Windows

```
python test_protocol.py
```
