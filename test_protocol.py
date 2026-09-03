"""Testy które chodzą bez Windows: coords + status + prompt."""
from __future__ import annotations

from agent_status import AgentStatus, TodoItem, parse_footer, status_from_items
from coords import box_to_px, n_to_px, px_to_n
from stateless_prompt import WhereAmI, build_user_prompt, example_chrome_costs


def test_coords_dual_scale() -> None:
    assert n_to_px(0, 1920) == 0
    assert n_to_px(1000, 1920) == 1919
    assert n_to_px(1.0, 1920) == 1919
    assert n_to_px(0.5, 1920) == n_to_px(500, 1920)
    assert px_to_n(0, 1920) == 0
    assert px_to_n(1919, 1920) == 1000
    x0, y0, x1, y1 = box_to_px((0.1, 0.2, 0.8, 0.9), 1000, 1000)
    assert x0 < x1 and y0 < y1


def test_footer_working() -> None:
    st = status_from_items(
        [
            "kursor zawsze na zrzucie",
            "crop okna po tytule / normalized box",
            "stateless user prompt w endgame Wheel",
        ],
        finished=False,
    )
    msg = st.wrap_commit(
        "vision-chat: kursor + crop + stateless prompt",
        "Franz winapi przywołany. Model dostaje pełny obraz i wycinek.",
    )
    assert "PRACA_NADAL_TRWA" in msg
    assert "praca nadal trwa, pozostałe items todo list:" in msg
    done, items = parse_footer(msg)
    assert done is False
    assert len(items) == 3


def test_footer_done() -> None:
    st = AgentStatus(
        finished=True,
        items=[TodoItem("kursor", done=True), TodoItem("crop", done=True)],
    )
    foot = st.footer()
    assert foot.startswith("ZAKONCZONO")
    done, items = parse_footer(foot)
    assert done is True
    assert items == []


def test_prompt_has_where() -> None:
    text = example_chrome_costs()
    assert "stateless" in text.lower()
    assert "xn=512" in text
    assert "przycisk scroll" in text
    assert "costs" in text.lower()
    p = build_user_prompt(WhereAmI(app="X"), goal="zobacz costs")
    assert "aplikacja: X" in p


if __name__ == "__main__":
    test_coords_dual_scale()
    test_footer_working()
    test_footer_done()
    test_prompt_has_where()
    print("ok")
