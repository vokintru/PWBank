# Импорты
import logging
import pickledb
import datetime
from datetime import timedelta
import config
import keyboards
import random
import string
from operator import itemgetter
from FSM import Donate, Send, Promo, Link, Settings, Ban, CreatePromo, Ping
from database import BotDB
from qiwi_payments import QiwiPay
from colorama import Fore
from colorama import Style
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ParseMode

# Базы данных
logsid = pickledb.load('logsid.json', True)
promos = pickledb.load('promos.json', True)
bills = pickledb.load('bills.json', True)
revenue = pickledb.load('revenue.json', True)
invite_codes = pickledb.load('invite_codes.json', True)
BotDB = BotDB('data.db')

# Переменные
PWBaad = 1998072563
admins = {1585401975, 1998072563, 5967901708}
qiwi_token = config.tokens['qiwi']

# Обект бота
bot = Bot(token=config.bot_tokens[config.bot], parse_mode=ParseMode.HTML)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
QiwiPay = QiwiPay(qiwi_token)


# Функции
async def on_startup(_):
    if config.startup_on:
        for i in range(len(BotDB.get_all_user_id())):
            await bot.send_message(BotDB.get_all_user_id()[i], f'Бот перезагрузился!',
                                   reply_markup=keyboards.markup_update)


def get_keyboard(user_id, text=False):
    data = BotDB.get_keyboard(user_id=user_id)
    neworold = BotDB.status(user_id)
    if neworold == 1:
        neworold = True
    else:
        neworold = False

    admin = admins
    if user_id in admin:
        admin = 1
    else:
        admin = 0

    if text:
        if data == 0:
            return 'Большие кнопки'
        elif data == 1:
            return 'Список'
        elif data == 2:
            return 'Маленькие кнопки'
    else:
        if admin == 0:
            if neworold:
                if data == 0:
                    return keyboards.markup_bb_admin
                elif data == 1:
                    return keyboards.markup_list_admin
                elif data == 2:
                    return keyboards.markup_sb_admin
            else:
                if data == 0:
                    return keyboards.markup_bb_admin
                elif data == 1:
                    return keyboards.markup_list_admin
                elif data == 2:
                    return keyboards.markup_sb_admin
        elif admin == 1:
            # обычные кнопки
            if data == 0:
                return keyboards.markup_bb_admin
            elif data == 1:
                return keyboards.markup_list_admin
            elif data == 2:
                return keyboards.markup_sb_admin
            # админ-панель
            elif data == 10:
                return keyboards.markup_bb_admin_panel
            elif data == 11:
                return keyboards.markup_list_admin_panel
            elif data == 12:
                return keyboards.markup_sb_admin_panel


def get_public_status(user_id, text=False):
    data = BotDB.get_public_status(user_id=user_id)
    if text:
        if data == 0:
            return 'Приватный'
        elif data == 1:
            return 'Публичный'
    else:
        if data == 0:
            return 0
        elif data == 1:
            return 1


def check_invite_code(code, use=True, add=False):
    codes = invite_codes.get('codes').split()
    if add:
        codes.append(code)
        codes = ' '.join(codes)
        invite_codes.set('codes', codes)
    elif code in codes:
        if use:
            codes.remove(code)
            codes = ' '.join(codes)
            invite_codes.set('codes', codes)
        return True


def log():
    logid = logsid.get('last')
    logging.basicConfig(level=logging.INFO,
                        handlers=[logging.StreamHandler(), logging.FileHandler(f"logs/{logid}.log")])
    logging.info(Fore.GREEN + Style.BRIGHT + 'Set Color Message')
    last = int(float(logsid.get('last')) + 1)
    logsid.set('last', str(forlog(last)))


def lastpromodef(idx, promocode):
    x = BotDB.promos(idx)
    if promocode in x:
        return False
    else:
        return True


def timestamp():
    timestamp = str(datetime.datetime.now()).split()
    timestamp = f'{"".join(list(timestamp[1])[:5])} {timestamp[0]}'
    return timestamp


def forlog(x):
    if len(str(x)) == 1:
        x = f'0000{x}'
    elif len(str(x)) == 2:
        x = f'000{x}'
    elif len(str(x)) == 3:
        x = f'00{x}'
    elif len(str(x)) == 4:
        x = f'0{x}'
    return x


def addmoney(x, y):
    money = float(x) + float(y)
    return money


async def link(user_id):
    card = BotDB.get_card(user_id)
    await bot.send_message(user_id, 'Ура! Ваша карта создана и добавлена в стикерпак! Кстати вот она:')
    await bot.send_sticker(user_id, sticker=card)


def create_payment(value, user_id, description):
    pay_url, bill_id = QiwiPay.create_bill(value, user_id, description)
    return pay_url, bill_id


def check_payment(bill_id):
    status = QiwiPay.check_bill(bill_id)
    if status == 'PAID':  # Оплата прошла
        return 0
    elif status == 'WAITING':  # Ожидание
        return 1
    elif status == 'REJECTED':  # Отклонено
        return 2
    elif status == 'EXPIRED':  # Просрочено
        return 3


async def anti_flood(*args, **kwargs):
    m = args[0]
    # Логи
    logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                 f'@{m.from_user.username} - Спам ({m.from_user.id} id)')

    # Чат
    await bot.send_video(m.from_user.id, 'https://i.ibb.co/1JMKV68/fsrgasdfgzsfdag.gif')


# Система логов
log()


#####################################################-+-START-+-########################################################

@dp.message_handler(commands=["start"])
@dp.throttled(anti_flood, rate=1)
async def cmd_start(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /start (Первый раз) ({message.from_user.id} id)')

        # Добавление в базу
        BotDB.add_user(message.from_user.id, message.from_user.username)

        # Ответ
        await message.answer('У бота есть канал с информацией о тех. работах, важной информацией и новостями об '
                             'обновлениях!\n'
                             'Ссылка: https://t.me/PWBankInfo')
        await bot.send_sticker(chat_id=message.chat.id,
                               sticker=r'CAACAgIAAxkBAAEGuDtjkHiqDPvnBOCMDK0aGQ35q_yHPAACyyIAAoBdiEhY-6nL0KVotSsE')
        await message.answer(f'Добро пожаловать в PWBank, {message.from_user.first_name}!\n'
                             f'Если вы хотите изменить меню управления, нажмите сюда --> '
                             f'/settings и выбирете пункт "Клавиатура"',
                             reply_markup=get_keyboard(message.from_user.id))

    ########################################################################################################################

    elif not BotDB.check_ban(message.from_user.id):
        BotDB.update_username(message.from_user.id, message.from_user.username)
        await message.answer('Вы забанены! Если вы не согласны с этим, напишите @PWBaad')

    ########################################################################################################################

    # Админ
    elif message.from_user.id in admins:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /start (Админ) ({message.from_user.id} id)')

        # Ответ
        await message.answer(f'Добро пожаловать в PWBank, Админ!\n'
                             'Что бы посмотреть баланс: /balance\n'
                             'Что бы пополнить баланс: /addcoins\n'
                             'Что бы перевести: /sendcoins\n'
                             'Что бы посмотреть свою карту: /mycard\n'
                             'Что бы привязать карту: /link\n'
                             'Что бы создать промокод: /createpromo\n'
                             'Что бы забанить человека: /ban\n'
                             'Что бы попросить пользователя обратится в хотлайн: /pinguser'
                             '\n\n'
                             'PWBank Inc.',
                             reply_markup=get_keyboard(message.from_user.id))

    ########################################################################################################################

    # Есть карта
    elif BotDB.status(int(message.from_user.id)) == 1:
        BotDB.update_username(message.from_user.id, message.from_user.username)
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /start (Есть карта) ({message.from_user.id} id)')

        # Ответ
        await bot.send_sticker(chat_id=message.chat.id,
                               sticker=r'CAACAgIAAxkBAAEGuDtjkHiqDPvnBOCMDK0aGQ35q_yHPAACyyIAAoBdiEhY-6nL0KVotSsE')
        await message.answer(f'Добро пожаловать в PWBank, {message.from_user.first_name}!',
                             reply_markup=get_keyboard(message.from_user.id))

    ########################################################################################################################

    # Остальные
    else:
        BotDB.update_username(message.from_user.id, message.from_user.username)
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /start (Нет карты) ({message.from_user.id} id)')

        # Ответ
        await bot.send_sticker(chat_id=message.chat.id,
                               sticker=r'CAACAgIAAxkBAAEGuDtjkHiqDPvnBOCMDK0aGQ35q_yHPAACyyIAAoBdiEhY-6nL0KVotSsE')
        await message.answer(f'Добро пожаловать в PWBank, {message.from_user.first_name}!',
                             reply_markup=get_keyboard(message.from_user.id))


########################################################################################################################
##################################################-+-CREATEPROMO-+-#####################################################

@dp.message_handler(commands=["createpromo"])
async def cmd_createpromo(message: types.Message):
    # Проверка на админа
    if message.from_user.id in admins:
        await message.answer('Ввидите имя промокода:', reply_markup=keyboards.markup_back)
        await CreatePromo.promo_key.set()

    else:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /createpromo (Не Админ) ({message.from_user.id} id)')


@dp.message_handler(state=CreatePromo.promo_key)
async def promo_key(message: types.Message, state: FSMContext):
    # Проверка на админа
    if message.from_user.id in admins:
        await state.update_data(promo_key=message.text)
        data = await state.get_data()
        data = data['promo_key']
        if data == '⬅ Отмена':
            await state.finish()
            await fsm_cancel(call=message)
        else:
            await message.answer('Ввидите награду:', reply_markup=keyboards.markup_back)
            await CreatePromo.promo_count.set()

    else:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /createpromo (Не Админ) ({message.from_user.id} id)')


@dp.message_handler(state=CreatePromo.promo_count)
async def promo_count(message: types.Message, state: FSMContext):
    # Проверка на админа
    if message.from_user.id in admins:
        await state.update_data(promo_count=message.text)
        data = await state.get_data()
        data = data['promo_count']
        if data == '⬅ Отмена':
            await state.finish()
            await fsm_cancel(call=message)
        else:
            await message.answer('Ввидите описание:', reply_markup=keyboards.markup_back)
            await CreatePromo.promo_msg.set()

    else:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /createpromo (Не Админ) ({message.from_user.id} id)')


@dp.message_handler(state=CreatePromo.promo_msg)
async def promo_msg(message: types.Message, state: FSMContext):
    # Проверка на админа
    if message.from_user.id in admins:
        await state.update_data(promo_msg=message.text)
        data = await state.get_data()
        data = data['promo_msg']
        if data == '⬅ Отмена':
            await state.finish()
            await fsm_cancel(call=message)
        else:
            await message.answer('Вы уверены?', reply_markup=keyboards.markup_confirm)
            await CreatePromo.promo_confirm.set()

    else:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /createpromo (Не Админ) ({message.from_user.id} id)')


@dp.message_handler(state=CreatePromo.promo_confirm)
async def promo_confirm(message: types.Message, state: FSMContext):
    # Проверка на админа
    if message.from_user.id in admins:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /createpromo (Админ) ({message.from_user.id} id)')

        await state.update_data(promo_confirm=message.text)
        data = await state.get_data()
        data = data['promo_confirm']
        if data == '❌ Нет':
            await state.finish()
            await fsm_cancel(call=message)
        elif data == '✅ Да':
            # Мэйн код
            x = await state.get_data()
            j = f'{x["promo_msg"]} {x["promo_count"]}'
            promos.set(x['promo_key'], j)
            y = str(promos.get(x['promo_key']))
            y = y.split()
            infopromo = ' '.join(y[:-1])
            count = y[-1]
            await state.finish()
            await message.answer(f'Промокод {x["promo_key"]} создан!\nОписание промокода:\n{infopromo}\n'
                                 f'Бонус: {count}\n', reply_markup=get_keyboard(message.from_user.id, False))

    else:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /createpromo (Не Админ) ({message.from_user.id} id)')


########################################################################################################################
####################################################-+-NEWCARD-+-#######################################################

@dp.message_handler(commands=["newcard"])
@dp.throttled(anti_flood, rate=1)
async def cmd_newcard(message: types.Message):
    BotDB.update_username(message.from_user.id, message.from_user.username)
    if BotDB.check_ban(message.from_user.id):
        if message.from_user.username:
            # Проверка на наличие карты
            if BotDB.status(int(message.from_user.id)) == 1:
                # Логи
                logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                             f'@{message.from_user.username} - /newcard (Уже есть карта) ({message.from_user.id} id)')

                # Сообщение
                await message.answer('У вас уже есть карта PWBank!')
            # Проверка на нахождение в очереди
            elif BotDB.status(int(message.from_user.id)) == 2:
                # Сообщение
                logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                             f'@{message.from_user.username} - /newcard (В ожидании карты) ({message.from_user.id} id)')

                # Сообщение
                await message.answer('Ваша карта PWBank сейчас на стадии обработки. '
                                     'Напишите в @PWBaad, чтобы мы могли с вами связатся.')
            # Мэйн код
            else:
                # Логи
                logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                             f'@{message.from_user.username} - /newcard (Идёт заказ) ({message.from_user.id} id)')

                # Кнопки
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text='Да', callback_data="card_yes"))
                keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data="card_no"))

                # Сообщение
                await message.answer(f'Вы хотите оставить заявку?', reply_markup=keyboard)
        else:
            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /newcard (Нет ника) ({message.from_user.id} id)')
            # Чат
            await message.answer(f'Перед заказом карты создайте ник и напишите @PWBaad!')
    else:
        await message.answer('Вы забанены! Если вы не согласны с этим, напишите @PWBaad')


########################################################################################################################

@dp.callback_query_handler(text="card_yes")
async def dezain_fish(call: types.CallbackQuery):
    # Логи
    logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                 f'@{call.from_user.username} - /newcard (Заказано) ({call.from_user.id} id)')

    # Запись
    BotDB.set_status(call.from_user.id, 2)

    # Чат
    await bot.send_message(PWBaad, f'Поступил новый заказ от @{call.from_user.username}')
    await call.message.delete()
    await call.message.answer('Успешно, напишите в @PWBaad, чтобы мы могли с вами связатся.')
    await call.answer()


########################################################################################################################

@dp.callback_query_handler(text="card_no")
async def dezain_fish_no(call: types.CallbackQuery):
    # Логи
    logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                 f'@{call.from_user.username} - /newcard (Отмена) ({call.from_user.id} id)')

    # Чат
    await call.message.delete()
    await call.message.answer('Отменено')
    await call.answer()


########################################################################################################################
####################################################-+-HOTLINE-+-#######################################################

@dp.message_handler(commands=["hotline"])
@dp.throttled(anti_flood, rate=1)
async def cmd_hotline(message: types.Message):
    BotDB.update_username(message.from_user.id, message.from_user.username)
    # Логи
    logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                 f'@{message.from_user.username} - /hotline ({message.from_user.id} id)')

    # Сообщение
    await message.answer('Аккаунт поддержки: @PWBaad')


########################################################################################################################
######################################################-+-TOP-+-#########################################################

@dp.message_handler(commands=["top"])
@dp.throttled(anti_flood, rate=1)
async def cmd_top(message: types.Message):
    BotDB.update_username(message.from_user.id, message.from_user.username)
    if BotDB.check_ban(message.from_user.id):
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /top ({message.from_user.id} id)')

        tops = BotDB.get_all_public_user_id()
        bal_set = []
        for i in range(len(tops)):
            bal_set.append([BotDB.get_balance(tops[i]), tops[i]])
        bal_set = sorted(bal_set)
        tops_set = {}
        for i in range(len(bal_set)):
            tops_set[bal_set[i][1]] = bal_set[i][0]

        # Сообщение
        tops_msg = 'Топ:\n'
        if len(tops_set) == 0:
            await message.answer('На данный момент нет ни одного пользователя с публичным аккаунтом!')
        elif len(tops_set) > 5:
            for i in range(5):
                da = tops_set.popitem()
                da1 = str(BotDB.get_user_name(da[0]))
                da2 = str(BotDB.get_balance(da[0]))
                tops_msg = tops_msg + f'@{da1} - {da2} Пубедкоинов\n'
            await message.answer(tops_msg)
        else:
            for i in range(len(tops_set)):
                da = tops_set.popitem()
                da1 = str(BotDB.get_user_name(da[0]))
                da2 = str(BotDB.get_balance(da[0]))
                tops_msg = tops_msg + f'@{da1} - {da2} Пубедкоинов\n'
            await message.answer(tops_msg)

    else:
        await message.answer('Вы забанены! Если вы не согласны с этим, напишите @PWBaad')


########################################################################################################################
#####################################################-+-DONATE-+-#######################################################

@dp.message_handler(commands=["donate"])
@dp.throttled(anti_flood, rate=1)
async def cmd_donate(message: types.Message):
    BotDB.update_username(message.from_user.id, message.from_user.username)
    if not config.donate_on:
        await message.answer('Донат отключён администрацией!')
    else:
        if BotDB.check_ban(message.from_user.id):
            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /donate ({message.from_user.id} id)')

            await message.answer(f'Курс: 1₽ = 100 Пубедокоинов')
            await message.answer(f'Введите сумму пополнения в рублях:', reply_markup=keyboards.markup_back)
            await Donate.donate_summ.set()
        else:
            await message.answer('Вы забанены! Если вы не согласны с этим, напишите @PWBaad')


########################################################################################################################


@dp.message_handler(state=Donate.donate_summ)
async def donate_summ(message: types.Message, state: FSMContext):
    await state.update_data(donate_summ=message.text)
    data = await state.get_data()
    bills.set(str(message.from_user.id), data['donate_summ'])
    if ',' in data['donate_summ']:
        await message.answer('Замените запятую на точку')
        await state.finish()
        await fsm_cancel(call=message)
    elif data['donate_summ'] == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    elif float(data['donate_summ']) < 1:
        await message.answer('Минимальная сумма пополнения - 1₽')
        await fsm_cancel(call=message)
        await state.finish()
    elif float(data['donate_summ']) > 100000:
        await message.answer('Максимальная сумма пополнения - 100.000₽')
        await fsm_cancel(call=message)
        await state.finish()
    else:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /donate (Qiwi) (Идёт оплата) ({message.from_user.id} id)')

        pay_url, bill_id = create_payment(data['donate_summ'], message.from_user.id,
                                          f'Пополнение баланса в телеграм боте PWBank\n(UserID: {message.from_user.id})')
        await state.finish()
        temp = [pay_url, bill_id, bills.get(str(message.from_user.id))]
        bills.set(str(message.from_user.id), temp)

        # Кнопки
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Продолжить',
                                                callback_data='pay_qiwi_check'))

        # Сообщение
        await bot.send_message(message.from_user.id, 'Для отмены оплаты нажмите "Продолжить"',
                               reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(message.from_user.id, f'Ссылка на оптату: {pay_url}. У вас 30 минут чтобы оплатить. '
                                                     f'После оплаты нажмите на кнопку',
                               reply_markup=keyboard)


########################################################################################################################

@dp.callback_query_handler(text="pay_qiwi_check")
async def pay_qiwi_check(call: types.CallbackQuery):
    status = check_payment(bills.get(str(call.from_user.id))[1])
    if status == 0:
        # Сообщение
        await bot.send_message(call.from_user.id, 'Оплата прошла успешно.')

        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{call.from_user.username} - /donate (Qiwi) ({bills.get(str(call.from_user.id))[2]} Рублей) '
                     f'({call.from_user.id} id)')
        BotDB.add_money(call.from_user.id, float(bills.get(str(call.from_user.id))[2]) * 100)
        revenue.set('revenue', str(int(float(revenue.get('revenue')) + float(bills.get(str(call.from_user.id))[2]))))
        await bot.send_message(call.from_user.id, f'Ваш баланс составляет {BotDB.get_balance(call.from_user.id)}',
                               reply_markup=get_keyboard(call.from_user.id))
    elif status == 1:
        await bot.send_message(call.from_user.id, 'Вы не оплатили! Платёж отменён!')
        QiwiPay.close_bill(bills.get(str(call.from_user.id))[1])

        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{call.from_user.username} - /donate (Qiwi) (Платёж отклонён (Не оплачено)) '
                     f'({call.from_user.id} id)')
        await fsm_cancel(call=call)
    elif status == 2:
        # Сообщение
        await bot.send_message(call.from_user.id, 'Платёж отклонён.')

        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{call.from_user.username} - /donate (Qiwi) (Платёж отклонён) ({call.from_user.id} id)')
        await fsm_cancel(call=call)
    elif status == 3:
        # Сообщение
        await bot.send_message(call.from_user.id, 'Время платежа просрочено.')

        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{call.from_user.username} - /donate (Qiwi) (Время платежа просрочено) ({call.from_user.id} id)')
        await fsm_cancel(call=call)
    await call.answer()


########################################################################################################################
###################################################-+-PINGUSER-+-#######################################################

@dp.message_handler(commands=["pinguser"])
async def cmd_pinguser(message: types.Message):
    # Проверка на админа
    if message.from_user.id in admins:
        await message.answer('Введите ник (Пример @example):', reply_markup=keyboards.markup_back)
        await Ping.ping_user.set()


@dp.message_handler(state=Ping.ping_user)
async def pinguser_username(message: types.Message, state: FSMContext):
    await state.update_data(ping_user=message.text)
    data = await state.get_data()
    if data['ping_user'] == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        await message.answer('Вы уверены?', reply_markup=keyboards.markup_confirm)
        await Ping.ping_confirm.set()


@dp.message_handler(state=Ping.ping_confirm)
async def pinguser_username(message: types.Message, state: FSMContext):
    await state.update_data(ping_confirm=message.text)
    data = await state.get_data()
    confirm = data['ping_confirm']
    if confirm == '✅ Да':
        await bot.send_message(BotDB.get_user_id(data['ping_user'][1:]),
                               '!!! ВНИМАНИЕ !!!\nАдминистратор бота просит вас связаться с '
                               'ним через @PWBaad')
        await message.answer('Уведомление отправлено успешно!', reply_markup=get_keyboard(message.from_user.id))
        await state.finish()

    elif confirm == '❌ Нет':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        await state.finish()
        await fsm_cancel(call=message)


########################################################################################################################
######################################################-+-PROMO-+-#######################################################

@dp.message_handler(commands=["promo"])
@dp.throttled(anti_flood, rate=1)
async def cmd_promo(message: types.Message):
    BotDB.update_username(message.from_user.id, message.from_user.username)
    if BotDB.check_ban(message.from_user.id):
        if BotDB.status(message.from_user.id) == 1:
            await message.answer('Вставь промокод:', reply_markup=keyboards.markup_back)
            await Promo.promo_key.set()
        else:
            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /promo (Нет карты) ({message.from_user.id} id)')

            # Сообщение
            await message.answer('У вас ещё нету карты PWBank. Чтобы её оформить, нажмите в меню "Новая карта"')
            await state.finish()
            await fsm_cancel(call=message)
    else:
        await message.answer('Вы забанены! Если вы не согласны с этим, напишите @PWBaad')


@dp.message_handler(state=Promo.promo_key)
async def promo_key(message: types.Message, state: FSMContext):
    await state.update_data(promo_key=message.text)
    data = await state.get_data()
    promo = data['promo_key']
    if data['promo_key'] == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    elif lastpromodef(str(message.from_user.id), str(promo)):
        if promos.get(str(promo)):
            BotDB.add_promo(message.from_user.id, promo)
            y = str(promos.get(promo))
            y = y.split()
            infopromo = ' '.join(y[:-1])
            count = y[-1]
            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /promo ({promo}) ({message.from_user.id} id)')
            await message.answer(
                f'Промокод {promo} найден!\nОписание промокода:\n{infopromo}\nБонус: {count}\n',
                reply_markup=get_keyboard(message.from_user.id))
            await state.finish()
            BotDB.add_money(message.from_user.id, count)
        else:
            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /promo ({promo}) ({message.from_user.id} id)')
            await message.answer(f'Промокод {promo} ненайден!')
            await state.finish()
            await fsm_cancel(call=message)
    else:
        await message.answer('Вы уже активировали этот промокод!')
        await state.finish()
        await fsm_cancel(call=message)


########################################################################################################################
####################################################-+-BALANCE-+-#######################################################

@dp.message_handler(commands=["balance"])
@dp.throttled(anti_flood, rate=1)
async def cmd_balance(message: types.Message):
    BotDB.update_username(message.from_user.id, message.from_user.username)
    if BotDB.check_ban(message.from_user.id):
        # Проверка на наличие карты
        if BotDB.status(message.from_user.id) == 0:
            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /balance (Нет карты) ({message.from_user.id} id)')

            # Сообщение
            await message.answer('У вас ещё нету карты PWBank. Чтобы её оформить, нажмите в меню "Новая карта"')

        elif BotDB.status(message.from_user.id) == 1:

            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /balance (Есть карта (Баланс: '
                         f'{BotDB.get_balance(message.from_user.id)})) '
                         f'({message.from_user.id} id)')

            # Сообщение
            await message.answer(f'Ваш баланс составляет: {BotDB.get_balance(message.from_user.id)} Пубедкоинов.')

        elif BotDB.status(message.from_user.id) == 2:

            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /balance (Карта на стадии  выпуска)')

            # Сообщение
            await message.answer(f'Ваша карта на стадии  выпуска!')
    else:
        await message.answer('Вы забанены! Если вы не согласны с этим, напишите @PWBaad')


########################################################################################################################
###################################################-+-ADDCOINS-+-#######################################################

@dp.message_handler(commands=["addcoins"])
async def cmd_addcoins(message: types.Message):
    # Проверка на админа
    if message.from_user.id in admins:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /addcoins (Админ) ({message.from_user.id} id)')

        # Кнопки
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='10 PWCoin', callback_data="coin10"))
        keyboard.add(types.InlineKeyboardButton(text='50 PWCoin', callback_data="coin50"))
        keyboard.add(types.InlineKeyboardButton(text='100 PWCoin', callback_data="coin100"))
        keyboard.add(types.InlineKeyboardButton(text='500 PWCoin', callback_data="coin500"))
        keyboard.add(types.InlineKeyboardButton(text='1000 PWCoin', callback_data="coin1000"))
        keyboard.add(types.InlineKeyboardButton(text='5000 PWCoin', callback_data="coin5000"))

        # Сообщение
        await message.answer(f'На сколько вы хотите пополнить баланс?', reply_markup=keyboard)
    else:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /addcoins (Не админ) ({message.from_user.id} id)')

        # Сообщение
        await message.answer('Доступ запрещён!')


########################################################################################################################

@dp.callback_query_handler(text="coin10")
async def coin10(call: types.CallbackQuery):
    # Зачисление
    money = 10
    BotDB.add_money(call.from_user.id, money)

    # Логи
    logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                 f'@{call.from_user.username} - /addcoins (+{money} Коинов) ({call.from_user.id} id)')

    # Чат
    await call.message.answer('Ожидайте...')
    await call.message.answer('Ваш баланс успешно пополнен!')
    await call.answer()


########################################################################################################################

@dp.callback_query_handler(text="coin50")
async def coin50(call: types.CallbackQuery):
    # Зачисление
    money = 50
    BotDB.add_money(call.from_user.id, money)

    # Логи
    logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                 f'@{call.from_user.username} - /addcoins (+{money} Коинов) ({call.from_user.id} id)')

    # Чат
    await call.message.answer('Ожидайте...')
    await call.message.answer('Ваш баланс успешно пополнен!')
    await call.answer()


########################################################################################################################

@dp.callback_query_handler(text="coin100")
async def coin100(call: types.CallbackQuery):
    # Зачисление
    money = 100
    BotDB.add_money(call.from_user.id, money)

    # Логи
    logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                 f'@{call.from_user.username} - /addcoins (+{money} Коинов) ({call.from_user.id} id)')

    # Чат
    await call.message.answer('Ожидайте...')
    await call.message.answer('Ваш баланс успешно пополнен!')
    await call.answer()


########################################################################################################################

@dp.callback_query_handler(text="coin500")
async def coin500(call: types.CallbackQuery):
    # Зачисление
    money = 500
    BotDB.add_money(call.from_user.id, money)

    # Логи
    logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                 f'@{call.from_user.username} - /addcoins (+{money} Коинов) ({call.from_user.id} id)')

    # Чат
    await call.message.answer('Ожидайте...')
    await call.message.answer('Ваш баланс успешно пополнен!')
    await call.answer()


########################################################################################################################

@dp.callback_query_handler(text="coin1000")
async def coin1000(call: types.CallbackQuery):
    # Зачисление
    money = 1000
    BotDB.add_money(call.from_user.id, money)

    # Логи
    logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                 f'@{call.from_user.username} - /addcoins (+{money} Коинов) ({call.from_user.id} id)')

    # Чат
    await call.message.answer('Ожидайте...')
    await call.message.answer('Ваш баланс успешно пополнен!')
    await call.answer()


########################################################################################################################

@dp.callback_query_handler(text="coin5000")
async def coin5000(call: types.CallbackQuery):
    # Зачисление
    money = 5000
    BotDB.add_money(call.from_user.id, money)

    # Логи
    logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                 f'@{call.from_user.username} - /addcoins (+{money} Коинов) ({call.from_user.id} id)')

    # Чат
    await call.message.answer('Ожидайте...')
    await call.message.answer('Ваш баланс успешно пополнен!')
    await call.answer()


########################################################################################################################
###################################################-+-SENDCOINS-+-######################################################

@dp.message_handler(commands=["sendcoins"])
@dp.throttled(anti_flood, rate=1)
async def cmd_sendcoins(message: types.Message):
    BotDB.update_username(message.from_user.id, message.from_user.username)
    if BotDB.check_ban(message.from_user.id):
        # Проверка на наличие карты
        if BotDB.status(message.from_user.id) == 0:

            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /sendcoins (Нет карты) ({message.from_user.id} id)')

            # Чат
            await message.answer('У вас ещё нету карты PWBank. Чтобы её оформить, нажмите в меню "Новая карта"')
        elif BotDB.status(message.from_user.id) == 1:
            await message.answer('Введите ник получателя (Пример @example):', reply_markup=keyboards.markup_back)
            await Send.send_user.set()
        elif BotDB.status(message.from_user.id) == 2:
            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /balance (Карта на стадии  выпуска)')

            # Сообщение
            await message.answer(f'Ваша карта на стадии  выпуска!')
    else:
        await message.answer('Вы забанены! Если вы не согласны с этим, напишите @PWBaad')


@dp.message_handler(state=Send.send_user)
async def send_user(message: types.Message, state: FSMContext):
    await state.update_data(send_user=message.text)
    data = await state.get_data()
    data = data['send_user']
    if data == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    elif BotDB.user_exists_username(data[1:]):
        await message.answer('Этот пользователь не зарегистрирован в боте!')
        await state.finish()
        await fsm_cancel(call=message)
    elif BotDB.status(BotDB.get_user_id(data[1:])) != 1:
        await message.answer('У этого пользователя нет карты!')
        await state.finish()
        await fsm_cancel(call=message)
    else:
        await message.answer("Введите сумму перевода (Минимум 1 коин):")
        await Send.send_summ.set()


@dp.message_handler(state=Send.send_summ)
async def send_summ(message: types.Message, state: FSMContext):
    await state.update_data(send_summ=message.text)
    data = await state.get_data()
    data = data['send_summ']
    if data == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        await message.answer("Введите сообщение для получателя:")
        await Send.send_msg.set()


@dp.message_handler(state=Send.send_msg)
async def send_msg(message: types.Message, state: FSMContext):
    await state.update_data(send_msg=message.text)
    data = await state.get_data()
    data = data['send_msg']
    if data == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        data = await state.get_data()
        sendid = BotDB.get_user_id(data['send_user'][1:])
        send_username = data['send_user'][1:]
        sendcount = data['send_summ']
        msg = data['send_msg']
        balance = BotDB.get_balance(message.from_user.id)
        block_sim = ['!', '@', '#', '$', '%', '^', '&', '*', '_', '"', '№', ';', ':', '<', '>']
        block = False
        for i in range(len(block_sim)):
            if block_sim[i] in list(msg):
                # Логи
                logging.info(
                    Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                    f'@{message.from_user.username} - /sendcoins (В сообщении содержатся запрещённые символы) '
                    f'({message.from_user.id} id)')

                # Чат
                await message.answer('В сообщении содержатся запрещённые символы!')
                await state.finish()
                await fsm_cancel(call=message)
                block = True
        # Проверка на наличие баланса
        if block:
            pass
        elif sendcount.isdigit():
            if float(balance) < float(sendcount):
                # Логи
                logging.info(
                    Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                    f'@{message.from_user.username} - /sendcoins (Не хватает коинов) '
                    f'({message.from_user.id} id)')

                # Чат
                await message.answer('У ваc не хватает Пубедкоинов для перевода!')
                await state.finish()
                await fsm_cancel(call=message)
            elif float(balance) < 1:
                # Логи
                logging.info(
                    Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                    f'@{message.from_user.username} - /sendcoins (Минусовой перевод) '
                    f'({message.from_user.id} id)')

                # Чат
                await message.answer('Минимальная сумма перевода 1 Пубедокоин!')
                await state.finish()
                await fsm_cancel(call=message)
            else:
                # Перевод
                BotDB.add_money(sendid, float(sendcount))
                sendcount = float(sendcount) * -1
                BotDB.add_money(message.from_user.id, sendcount)
                sendcount = int(sendcount * -1)

                # Логи
                logging.info(
                    Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                    f'@{message.from_user.username} - /sendcoins (Перевёл @{send_username} '
                    f'{sendcount} Пубедкоинов) (Сообщение: {msg})'
                    f'({message.from_user.id} id)')

                # Чат
                await message.answer(f'Пубедкоины отправлены @{send_username}\nСообщение для получателя: "{msg}"',
                                     parse_mode='HTML',
                                     reply_markup=get_keyboard(message.from_user.id))
                await bot.send_message(sendid,
                                       f'@{message.from_user.username} перевёл вам {sendcount} Пубедкоинов\n'
                                       f'Сообщение от @{message.from_user.username} : "' + str(msg) + '"')
                await state.finish()
        else:
            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /sendcoins (Неправельная сумма) '
                         f'({message.from_user.id} id)')

            # Чат
            await message.answer(f'Неправельная сумма!')
            await state.finish()
            await fsm_cancel(call=message)


########################################################################################################################
####################################################-+-MYCARD-+-########################################################

@dp.message_handler(commands=["mycard"])
@dp.throttled(anti_flood, rate=1)
async def cmd_mycard(message: types.Message):
    BotDB.update_username(message.from_user.id, message.from_user.username)
    if BotDB.check_ban(message.from_user.id):
        # Проверка на наличие карты
        if BotDB.status(message.from_user.id) == 0:
            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /mycard (Нет карты) ({message.from_user.id} id)')

            # Чат
            await message.answer('У вас ещё нету карты PWBank. Чтобы её оформить, нажмите в меню "Новая карта"')

        elif BotDB.status(message.from_user.id) == 1:
            # Подготовка
            x = BotDB.get_card(message.from_user.id)

            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /mycard (Есть карта) ({message.from_user.id} id)')

            # Чат
            await message.answer('Ваша карта:')
            await bot.send_sticker(chat_id=message.chat.id, sticker=f'{x}')

        elif BotDB.status(message.from_user.id) == 2:
            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /balance (Карта на стадии  выпуска)')

            # Сообщение
            await message.answer(f'Ваша карта на стадии  выпуска!')
    else:
        await message.answer('Вы забанены! Если вы не согласны с этим, напишите @PWBaad')


########################################################################################################################
#####################################################-+-LINK-+-#########################################################

@dp.message_handler(commands=["link"])
async def cmd_link(message: types.Message):
    # Проверка на админа
    if message.from_user.id in admins:
        await message.answer('Отправь мне стикер', reply_markup=keyboards.markup_back)
        await Link.link_token.set()
    else:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /link (Не Админ) ({message.from_user.id} id)')


@dp.message_handler(state=Link.link_token, content_types=['sticker', 'text'])
async def link_token(message: types.Message, state: FSMContext):
    if message.text == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        await state.update_data(link_token=message.sticker.file_id)
        data = await state.get_data()
        data = data['link_token']
        await message.answer('Введите ник пользователя (Пример: @example)', reply_markup=keyboards.markup_back)
        await Link.link_user.set()


@dp.message_handler(state=Link.link_user)
async def link_user(message: types.Message, state: FSMContext):
    await state.update_data(link_user=message.text)
    data = await state.get_data()
    data = data['link_user']
    if data == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        if not BotDB.user_exists_username(data[1:]):
            # Логи
            logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                         f'@{message.from_user.username} - /link (Админ) ({message.from_user.id} id)')
            await message.answer('Вы уверены?', reply_markup=keyboards.markup_confirm)
            await Link.link_confirm.set()
        else:
            await message.answer('Этот пользователь не зарегистритрован в боте!', reply_markup=keyboards.markup_confirm)
            await state.finish()
            await fsm_cancel(call=message)


@dp.message_handler(state=Link.link_confirm)
async def link_confirm(message: types.Message, state: FSMContext):
    await state.update_data(link_confirm=message.text)
    data = await state.get_data()
    data = data['link_confirm']
    if data == '✅ Да':
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /link (Админ) (Привязал) ({message.from_user.id} id)')
        data = await state.get_data()
        name = BotDB.get_user_id(data['link_user'][1:])
        card = data['link_token']
        # Связка
        BotDB.add_money(name, 500)
        BotDB.link(name, card)

        # Чат
        await state.finish()
        await message.answer('Привязано!', reply_markup=get_keyboard(message.from_user.id))
        await link(name)

    elif data == '❌ Нет':
        await state.finish()
        await fsm_cancel(call=message)


########################################################################################################################
######################################################-+-BAN-+-#########################################################

@dp.message_handler(commands=["ban"])
async def cmd_ban(message: types.Message):
    # Проверка на админа
    if message.from_user.id in admins:
        await message.answer('Введите имя пользователя (Пример: @example)', reply_markup=keyboards.markup_back)
        await Ban.ban_user.set()
    else:
        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /ban (Не Админ) ({message.from_user.id} id)')


@dp.message_handler(state=Ban.ban_user)
async def ban_user(message: types.Message, state: FSMContext):
    await state.update_data(ban_user=message.text)
    data = await state.get_data()
    data = data['ban_user']
    if data == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        await message.answer('Введите причину бана:', reply_markup=keyboards.markup_back)
        await Ban.ban_rezone.set()


@dp.message_handler(state=Ban.ban_rezone)
async def ban_user(message: types.Message, state: FSMContext):
    await state.update_data(ban_rezone=message.text)
    data = await state.get_data()
    data = data['ban_rezone']
    if data == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        await message.answer('Вы уверены?', reply_markup=keyboards.markup_confirm)
        await Ban.ban_confirm.set()


@dp.message_handler(state=Ban.ban_confirm)
async def ban_user(message: types.Message, state: FSMContext):
    await state.update_data(ban_confirm=message.text)
    data = await state.get_data()
    confirm = data['ban_confirm']
    if confirm == '✅ Да':
        name = data['ban_user']
        rezone = data['ban_rezone']
        name_id = BotDB.get_user_id(name[1:])
        BotDB.set_ban_status(name_id)

        # Логи
        logging.info(Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
                     f'@{message.from_user.username} - /ban ({name}) (Админ) (Причина: {rezone}) '
                     f'({message.from_user.id} id)')

        # Чат
        await message.answer(f'Вы заблокировали {name} по причине "{rezone}"! Для разблокировки обратитесь к '
                             f'@vokint_ru', reply_markup=get_keyboard(message.from_user.id))
        await bot.send_video(chat_id=name_id, video='https://gachi.gay/uyseN')
        await bot.send_message(name_id, f'Вы были забанены по причине: "{rezone}"! Если вы не согласны с этим, '
                                        f'напишите в @PWBaad')
    elif confirm == '❌ Нет':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        await state.finish()
        await fsm_cancel(call=message)


########################################################################################################################
###################################################-+-SETTINGS-+-#######################################################


@dp.message_handler(commands=["settings"])
@dp.throttled(anti_flood, rate=1)
async def cmd_settings(message: types.Message):
    BotDB.update_username(message.from_user.id, message.from_user.username)
    if BotDB.check_ban(message.from_user.id):
        logging.info(
            Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
            f'@{message.from_user.username} - /settings ({message.from_user.id} id)')
        await message.answer('Настройки:', reply_markup=keyboards.markup_settings)
        await Settings.settings_choice.set()
    else:
        await message.answer('Вы забанены! Если вы не согласны с этим, напишите @PWBaad')


@dp.message_handler(state=Settings.settings_choice)
async def settings_choice(message: types.Message, state: FSMContext):
    await state.update_data(settings_choice=message.text)
    data = await state.get_data()
    data = data['settings_choice']
    if data == '⌨ Клавиатура':
        await message.answer(f'Выбирете одно из списка: '
                             f'(Сейчас выбрано: {get_keyboard(message.from_user.id, text=True)})',
                             reply_markup=keyboards.markup_settings_keyboard)
        await Settings.Keyboard.keyboard.set()
    elif data == '🌐 Статус аккаунта':
        # Проверка на наличие карты
        if BotDB.status(message.from_user.id) == 0 or BotDB.status(message.from_user.id) == 2:
            await message.answer('У вас ещё нету карты PWBank. Чтобы её оформить, нажмите в меню "Новая карта"')
            await state.finish()
            await fsm_cancel(call=message)
        else:
            await message.answer('Данная настройка отвечает за отображение вас в топе по балансу бота')
            await message.answer(f'Выбирете одно из списка: '
                                 f'(Сейчас выбрано: {get_public_status(message.from_user.id, text=True)})',
                                 reply_markup=keyboards.markup_settings_public)
            await Settings.Public.choice.set()

    elif data == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        await state.finish()
        await fsm_cancel(call=message)


@dp.message_handler(state=Settings.Keyboard.keyboard)
async def settings_keyboard(message: types.Message, state: FSMContext):
    await state.update_data(keyboard=message.text)
    data = await state.get_data()
    data = data['keyboard']
    if data == 'Большие кнопки':
        BotDB.set_keyboard(message.from_user.id, 0)
        await message.answer('Выбрано: Большие кнопки', reply_markup=get_keyboard(message.from_user.id))
        await state.finish()
    elif data == 'Список':
        BotDB.set_keyboard(message.from_user.id, 1)
        await message.answer('Выбрано: Список', reply_markup=get_keyboard(message.from_user.id))
        await state.finish()
    elif data == 'Маленькие кнопки':
        BotDB.set_keyboard(message.from_user.id, 2)
        await message.answer('Выбрано: Маленькие кнопки', reply_markup=get_keyboard(message.from_user.id))
        await state.finish()
    elif data == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        await state.finish()
        await fsm_cancel(call=message)


@dp.message_handler(state=Settings.Public.choice)
async def settings_keyboard(message: types.Message, state: FSMContext):
    await state.update_data(choice=message.text)
    data = await state.get_data()
    data = data['choice']
    if data == 'Публичный':
        BotDB.set_public_status(message.from_user.id, 1)
        await message.answer('Выбрано: Публичный', reply_markup=get_keyboard(message.from_user.id))
        await state.finish()
    elif data == 'Приватный':
        BotDB.set_public_status(message.from_user.id, 0)
        await message.answer('Выбрано: Приватный', reply_markup=get_keyboard(message.from_user.id))
        await state.finish()
    elif data == '⬅ Отмена':
        await state.finish()
        await fsm_cancel(call=message)
    else:
        await state.finish()
        await fsm_cancel(call=message)


########################################################################################################################
######################################################-+-DEV-+-#########################################################


@dp.message_handler(commands=["dev_chat"])
async def dev_chat(message: types.Message):
    arg = message.get_args().split()[0]
    if arg == 'create':
        if message.from_user.id in admins:
            code = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
            check_invite_code(code=code, add=True)
            await message.answer(f'Новый код сгенерирован: <code>{code}</code>')
    elif check_invite_code(code=arg, use=False):
        check_invite_code(code=arg, use=True)
        chat_id = '-1001858159471'
        expire_date = datetime.datetime.now() + timedelta(days=1)
        link = await bot.create_chat_invite_link(chat_id, expire_date.timestamp, 1)
        await message.answer(f'Поздравляем! Вы были приглашены в группу разработчиков и тестировщиков PWBank`а! '
                             f'Вот ваша ссылка: {link.invite_link}\n'
                             f'Учитывайте что эта ссылка рассчитана на 1 человека!')


########################################################################################################################
#####################################################-+-RULES-+-########################################################


@dp.message_handler(commands=["rules"])
@dp.throttled(anti_flood, rate=1)
async def cmd_rules(message: types.Message):
    BotDB.update_username(message.from_user.id, message.from_user.username)
    logging.info(
        Fore.RED + Style.BRIGHT + '  [' + timestamp() + '] ' + Fore.GREEN + Style.BRIGHT +
        f'@{message.from_user.username} - /rules ({message.from_user.id} id)')
    await message.answer("Правила покупки карты PWBank'а:\n"
                         "1) Быть молодцом\n"
                         "2) Быть умным, а не глупым\n"
                         "3) Быть в беседе Пугода\n"
                         "4) Не иметь пубедкоинов\n"
                         "5) Не иметь карту PWBank'а\n"
                         "6) НЕ ТРОГАТЬ ЧУЖИЕ КАРТЫ!!1!1!!!!!111!!\n"
                         "7) Не срать деньгами и картами в чате\n"
                         "8) Не использовать количество денег, если у вас его нет*\n"
                         "9) Обращаться за пополнением и покупкой** карты ТОЛЬКО К БОТУ PWBANK-A ( @PWBankBot )\n"
                         "\n"
                         "*Проверить баланс карты и пополнить можно у бота @PWBankBot\n"
                         "**Цена карты+обслуживание навсегда+0% комиссии за операции с пубедкоинами+5% комиссии"
                         " за операции \n"
                         "с Пугодкоинами стоит 0 пубедкоинов или же 1 Пугодкоин\n"
                         "\n"
                         "Выпущенные ранее карты также должны соответствовать этим правилам!\n"
                         "\n"
                         "Created by VokintRu (@vokintru_feedback_bot)\n"
                         "Что бы поддержать автора бота: https://www.donationalerts.com/r/vokintrudonate")


########################################################################################################################
###################################################-+-FSM Cancel-+-#####################################################


@dp.callback_query_handler(text="cancel")
async def fsm_cancel(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, 'Отмена', reply_markup=get_keyboard(user_id=call.from_user.id))


########################################################################################################################
###################################################-+Admin Panel-+-#####################################################


@dp.message_handler(commands=["ap_on"])
@dp.throttled(anti_flood, rate=1)
async def ap_on(message: types.Message):
    await bot.send_message(message.from_user.id, 'Админ-Панель включена!',
                           reply_markup=get_keyboard(user_id=message.from_user.id))


@dp.message_handler(commands=["ap_off"])
@dp.throttled(anti_flood, rate=1)
async def ap_off(message: types.Message):
    await bot.send_message(message.from_user.id, 'Админ-Панель выключена!',
                           reply_markup=get_keyboard(user_id=message.from_user.id))


########################################################################################################################
##################################################-+-MENU BUTTONS-+-####################################################


@dp.message_handler()
async def tg_kb(message: types.Message):
    if BotDB.check_ban(message.from_user.id):
        msg = message['text']
        # Обычные кнопки
        if msg == '💰 Баланс':
            await cmd_balance(message)
        elif msg == '📦 Перевод':
            await cmd_sendcoins(message)
        elif msg == '🔑 Использовать Промокод':
            await cmd_promo(message)
        elif msg == '💎 Донат':
            await cmd_donate(message)
        elif msg == '📝 Тех. Поддержка':
            await cmd_hotline(message)
        elif msg == '💳 Ваша Карта':
            await cmd_mycard(message)
        elif msg == '💳 Создать карту':
            await cmd_newcard(message)
        elif msg == '⚙ Настройки':
            await cmd_settings(message)
        elif msg == '📈 Топ Баланса':
            await cmd_top(message)
        elif msg == '⚙ Админ-панель':
            if message.from_user.id in admins:
                BotDB.set_keyboard(message.from_user.id, int(f'1{BotDB.get_keyboard(message.from_user.id)}'))
                await ap_on(message)

        # Админ-Панель
        elif msg == '💰 Добавить баланс':
            await cmd_addcoins(message)
        elif msg == '🔗 Привязать карту':
            await cmd_link(message)
        elif msg == '🎫 Создать промокод':
            await cmd_createpromo(message)
        elif msg == '🔨 Выдать бан':
            await cmd_ban(message)
        elif msg == '🔔 Вызвать пользователя в хотлайн':
            await cmd_pinguser(message)
        elif msg == '⬅ Вернутся':
            if message.from_user.id in admins:
                BotDB.set_keyboard(message.from_user.id,
                                   int(f'{BotDB.get_keyboard(message.from_user.id)}'[1:]))
                await ap_off(message)
        elif msg == '🔄 Обновить кнопки':
            await message.answer('Обновлено!', reply_markup=get_keyboard(message.from_user.id))
    else:
        await message.answer('Вы забанены! Если вы не согласны с этим, напишите @PWBaad')


########################################################################################################################

# Запуск
if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
