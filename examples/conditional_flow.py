from baihe_autogui import Auto, ElementNotFoundError, ElementTimeoutError


def main() -> None:
    auto = Auto()

    try:
        auto.locate("dialog.png").wait_until_exists(timeout=3).right_click()
    except ElementTimeoutError:
        print("Dialog did not appear in time.")

    try:
        auto.locate("confirm.png").assert_exists().click()
    except ElementNotFoundError:
        print("Confirm button is required but missing.")

    auto.locate("optional-close.png").if_exists().click()


if __name__ == "__main__":
    main()
