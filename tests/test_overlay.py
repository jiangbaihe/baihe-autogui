from baihe_autogui.core.overlay import _parse_color, _rgb


def test_parse_color_uses_soft_named_palette():
    assert _parse_color("red") == _rgb(248, 113, 113)
    assert _parse_color("green") == _rgb(74, 222, 128)


def test_parse_color_accepts_hex_values():
    assert _parse_color("#facc15") == _rgb(250, 204, 21)
