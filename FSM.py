from aiogram.dispatcher.filters.state import StatesGroup, State


class Donate(StatesGroup):
    donate_summ = State()


class Send(StatesGroup):
    send_summ = State()
    send_user = State()
    send_msg = State()


class Promo(StatesGroup):
    promo_key = State()


class CreatePromo(StatesGroup):
    promo_key = State()
    promo_count = State()
    promo_msg = State()
    promo_confirm = State()


class Link(StatesGroup):
    link_token = State()
    link_user = State()
    link_confirm = State()


class Settings(StatesGroup):
    settings_choice = State()

    class Keyboard(StatesGroup):
        keyboard = State()

    class Public(StatesGroup):
        choice = State()


class Ban(StatesGroup):
    ban_user = State()
    ban_rezone = State()
    ban_confirm = State()


class Ping(StatesGroup):
    ping_user = State()
    ping_confirm = State()
