# Jak wpiąć to w endgame-ai

endgame-ai trzyma system prompt STABILNY (`Prompt.PREFIX` + docstrings).
Lotna część to user message, w tym `## environment`.

## Minimalny hak

W `Wheel._refresh_environment` (albo obok `gui.observe`):

```python
try:
    from vision_frame import grab
    frame = grab(
        goal=board.goal,
        looking_for=board.living_word[:200] if board.living_word else "",
        last_effect=(board.action_frame or "")[:300],
        crop_title="",  # albo tytuł top window z gui.enum_windows
    )
    environment_vision = frame.user_prompt
    # do transportu LLM: image full + opcjonalnie image crop
except OSError:
    environment_vision = ""  # nie-Windows
```

Nie dodawaj planera. Nie dodawaj checklisty jako prawdy postępu.
Obraz jest dodatkowym świadkiem świata, nie nowym biurem.

## Co model ma robić z wycinkiem

1. Pełny obraz → orientacja (jaka aplikacja, gdzie fold).
2. Wycinek okna / miejsca → „co jest grane” w tym prostokącie.
3. Jedna akcja w 0..1000.
4. Jeśli Submit / scroll jest poza kadrem — `SCROLL`, potem świeży grab.

To leczy znany edge z README endgame-ai: kontrolki pod foldem są
„absent” dla siatki UIA.

## User prompt ma się zmieniać

Nie doklejaj starych tur. Doklejaj tylko:

- cel
- gdzie jestem (app, okno, kursor xn/yn, szukam)
- ostatni SKUTEK w świecie
- koszt poprzedniej tury (tokeny), jeśli chcesz kalibrować zwięzłość
- zadanie tej tury

Historia czatu psuje mały model: zaczyna „kontynuować rozmowę”
zamiast patrzeć na piksele.
