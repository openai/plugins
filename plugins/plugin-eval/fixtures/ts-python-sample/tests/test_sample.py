from src.sample import choose_path


def test_choose_path():
    assert choose_path(["fast:item", "archived:slow"], False, True) == ["FAST:ITEM"]
