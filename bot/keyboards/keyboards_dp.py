from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class KeyboardDispatcher:
    def __init__(self):
        self.keyboards = dict()  # map<name, keyboard>

    def __setitem__(self, keyboard_name: str, keyboard):
        self.keyboards[keyboard_name] = keyboard

    def __getitem__(self, keyboard_name: str) -> ReplyKeyboardMarkup:
        return self.keyboards[keyboard_name]


def register_common_keyboard() -> KeyboardDispatcher:
    keyboards_dp = KeyboardDispatcher()
    keyboards_dp["main"] = ReplyKeyboardMarkup(resize_keyboard=True).row(
            KeyboardButton("my files")
    ).row(
            KeyboardButton("upload file")
    )
    keyboards_dp["cancel"] = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
            KeyboardButton("cancel")
    )
    return keyboards_dp
