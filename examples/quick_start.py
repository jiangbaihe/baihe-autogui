from baihe_autogui import Auto


def main() -> None:
    auto = Auto()

    auto.locate("button.png").wait_until_exists(timeout=5).click()
    auto.locate((200, 300)).move_to().click().write("hello world")
    auto.locate("button.png").double_click().press("enter")
    auto.locate("button.png").hotkey("ctrl", "a").write("replacement")


if __name__ == "__main__":
    main()
