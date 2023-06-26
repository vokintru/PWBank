from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# ~~~~~~~~~ КНОПКИ ~~~~~~~~~
if True:
    # Общие кнопки
    button1 = KeyboardButton('💰 Баланс')
    button2 = KeyboardButton('📦 Перевод')
    button3 = KeyboardButton('🔑 Использовать Промокод')
    button4 = KeyboardButton('💎 Донат')
    button6 = KeyboardButton('⚙ Настройки')
    button7 = KeyboardButton('📈 Топ Баланса')
    button_last = KeyboardButton('📝 Тех. Поддержка')

    # Все виды кнопок новых пользователей
    button_card2 = KeyboardButton('💳 Создать карту')

    # Все виды кнопок старых пользователей
    button_card1 = KeyboardButton('💳 Ваша Карта')

    # Все виды кнопок админов
    button_admin_panel = KeyboardButton('⚙ Админ-панель')

    # Все виды кнопок админ панели
    button_admin_add_balance = KeyboardButton('💰 Добавить баланс')
    button_admin_link = KeyboardButton('🔗 Привязать карту')
    button_admin_create_promo = KeyboardButton('🎫 Создать промокод')
    button_admin_ban = KeyboardButton('🔨 Выдать бан')
    button_admin_ping = KeyboardButton('🔔 Вызвать пользователя в хотлайн')
    button_admin_return = KeyboardButton('⬅ Вернутся')

    # Остальные кнопки
    button_last = KeyboardButton('🔄 Обновить кнопки')
    markup_update = ReplyKeyboardMarkup(resize_keyboard=True).add(button_last)

# ~~~~~~~~~ НАБОРЫ ~~~~~~~~~
if True:
    # Новый юзер
    if True:
        # Новый юзер | Лист
        markup_list_newuser = ReplyKeyboardMarkup().add(button1).add(button2).add(button3).add(button4) \
            .add(button_card2).add(button6).add(button7).add(button_last)

        # Новый юзер | Маленькие Кнопки
        markup_sb_newuser = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2, button3)
        markup_sb_newuser.row(button4, button_card2, button6)
        markup_sb_newuser.row(button7, button_last)

        # Новый юзер | Большие Кнопки
        markup_bb_olduser = ReplyKeyboardMarkup().row(button1, button2, button3)
        markup_bb_olduser.row(button4, button_card1, button6)
        markup_bb_olduser.row(button7, button_last)

    # Старый Юзер
    if True:
        # Старый юзер | Лист
        markup_list_olduser = ReplyKeyboardMarkup().add(button1).add(button2).add(button3).add(button4) \
            .add(button_card1).add(button6).add(button7).add(button_last)

        # Старый юзер | Маленькие Кнопки
        markup_sb_olduser = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2, button3)
        markup_sb_olduser.row(button4, button_card1, button6)
        markup_sb_olduser.row(button7, button_last)

        # Старый юзер | Большие Кнопки
        markup_sb_olduser = ReplyKeyboardMarkup().row(button1, button2, button3)
        markup_sb_olduser.row(button4, button_card1, button6)
        markup_sb_olduser.row(button7, button_last)

    # Админ
    if True:
        # Админ Обычные
        if True:
            # Админ | Лист
            markup_list_admin = ReplyKeyboardMarkup().add(button1).add(button2).add(button3).add(button4) \
                .add(button_card1).add(button6).add(button7).add(button_admin_panel).add(button_last)

            # Админ | Маленькие Кнопки
            markup_sb_admin = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2, button3)
            markup_sb_admin.row(button4, button_card1, button6)
            markup_sb_admin.row(button7, button_admin_panel, button_last)

            # Админ | Большие Кнопки
            markup_bb_admin = ReplyKeyboardMarkup().row(button1, button2, button3)
            markup_bb_admin.row(button4, button_card1, button6)
            markup_bb_admin.row(button7, button_admin_panel, button_last)

        # Админ Панель
        if True:
            # Админ | Лист
            markup_list_admin_panel = ReplyKeyboardMarkup().add(button_admin_add_balance).add(button_admin_link) \
                .add(button_admin_create_promo).add(button_admin_ban).add(button_admin_ping).add(button_admin_return)

            # Админ | Маленькие Кнопки
            markup_sb_admin_panel = ReplyKeyboardMarkup(resize_keyboard=True).row(button_admin_add_balance,
                                                                                  button_admin_link,
                                                                                  button_admin_create_promo)
            markup_sb_admin_panel.row(button_admin_ban, button_admin_ping, button_admin_return)

            # Админ | Большие Кнопки
            markup_bb_admin_panel = ReplyKeyboardMarkup().row(button_admin_add_balance, button_admin_link,
                                                              button_admin_create_promo)
            markup_bb_admin_panel.row(button_admin_ban, button_admin_ping, button_admin_return)

    # Остальное
    if True:
        # Кнопна назад
        button_back = KeyboardButton('⬅ Отмена')
        markup_back = ReplyKeyboardMarkup(resize_keyboard=True).add(button_back)

        # Да/Нет
        button_yes = KeyboardButton('✅ Да')
        button_no = KeyboardButton('❌ Нет')
        markup_confirm = ReplyKeyboardMarkup(resize_keyboard=True).add(button_yes).add(button_no)

        # Настройки
        settings_keyboard = KeyboardButton('⌨ Клавиатура')
        settings_public = KeyboardButton('🌐 Статус аккаунта')
        markup_settings = ReplyKeyboardMarkup(resize_keyboard=True).add(settings_keyboard) \
            .add(settings_public).add(button_back)

        # Настройки Подвиды
        if True:
            # Настройки --> Клава
            settings_keyboard_big_but = KeyboardButton('Большие кнопки')
            settings_keyboard_list = KeyboardButton('Список')
            settings_keyboard_small_but = KeyboardButton('Маленькие кнопки')
            markup_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(settings_keyboard_big_but) \
                .add(settings_keyboard_list).add(settings_keyboard_small_but).add(button_back)

            # Настройки --> Статус
            settings_public_yes = KeyboardButton('Публичный')
            settings_public_no = KeyboardButton('Приватный')
            markup_settings_public = ReplyKeyboardMarkup(resize_keyboard=True).add(settings_public_yes).add(
                settings_public_no) \
                .add(button_back)
