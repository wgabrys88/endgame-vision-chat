"""Protokół komunikacji agent ↔ człowiek.

Agent często kłamie słowem „koniec / zakończono”. Jedyny wiarygodny
sygnał to stopka na KOŃCU commita, push message albo odpowiedzi tury:

    praca nadal trwa, pozostałe items todo list:
    - [ ] ...
    - [ ] ...

Gdy lista jest pusta I flaga done=True:

    ZAKONCZONO
    praca nadal trwa, pozostałe items todo list:
    (brak)

Człowiek czyta TYLKO stopkę. Reszta tekstu może twierdzić cokolwiek.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


FOOTER_MARKER = "praca nadal trwa, pozostałe items todo list:"
DONE_MARKER = "ZAKONCZONO"
STILL_WORKING_MARKER = "PRACA_NADAL_TRWA"


@dataclass
class TodoItem:
    text: str
    done: bool = False

    def line(self) -> str:
        mark = "x" if self.done else " "
        return f"- [{mark}] {self.text.strip()}"


@dataclass
class AgentStatus:
    """Stan tury / commita. Źródło prawdy dla człowieka."""

    finished: bool = False
    items: list[TodoItem] = field(default_factory=list)
    note: str = ""

    def remaining(self) -> list[TodoItem]:
        return [i for i in self.items if not i.done]

    def footer(self) -> str:
        remaining = self.remaining()
        really_done = self.finished and not remaining
        lines = []
        if really_done:
            lines.append(DONE_MARKER)
        else:
            lines.append(STILL_WORKING_MARKER)
        if self.note:
            lines.append(self.note.rstrip())
        lines.append(FOOTER_MARKER)
        if really_done:
            lines.append("(brak)")
        elif not remaining:
            lines.append("- [ ] (lista pusta, ale finished=False — praca nadal trwa)")
        else:
            lines.extend(i.line() for i in remaining)
        return "\n".join(lines)

    def wrap_message(self, body: str) -> str:
        body = (body or "").rstrip()
        return f"{body}\n\n{self.footer()}\n" if body else f"{self.footer()}\n"

    def wrap_commit(self, subject: str, body: str = "") -> str:
        """Commit / extended push message z obowiązkową stopką."""
        subject = subject.strip()
        parts = [subject]
        if body.strip():
            parts.append("")
            parts.append(body.strip())
        parts.append("")
        parts.append(self.footer())
        return "\n".join(parts) + "\n"


def parse_footer(text: str) -> tuple[bool, list[str]]:
    """Zwraca (zakończono, pozostałe_otwarte_itemy)."""
    if not text:
        return False, []
    lines = text.replace("\r\n", "\n").split("\n")
    finished = False
    items: list[str] = []
    seen_marker = False
    for raw in lines:
        line = raw.strip()
        if line == DONE_MARKER:
            finished = True
        if line == FOOTER_MARKER:
            seen_marker = True
            continue
        if not seen_marker:
            continue
        if line.startswith("- ["):
            checked = line.startswith("- [x]") or line.startswith("- [X]")
            label = line[5:].strip() if line.startswith("- [") and "]" in line[:5] else line[2:].strip()
            if label and label != "(brak)" and not checked:
                items.append(label)
    if finished and not items:
        return True, []
    return False, items


def status_from_items(texts: Iterable[str], finished: bool = False, note: str = "") -> AgentStatus:
    return AgentStatus(
        finished=finished,
        items=[TodoItem(t) for t in texts if str(t).strip()],
        note=note,
    )
