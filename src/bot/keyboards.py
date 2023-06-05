from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.callbacks import cb_store, cb_buy
from database import db_session, users, usersskins


def get_menu(my_skins=True, store=True):
    keyboard = InlineKeyboardMarkup()
    bnts = []
    if my_skins:
        bnts.append(InlineKeyboardButton('My skins', callback_data='my_skins'))
    if store:
        bnts.append(InlineKeyboardButton('Store', callback_data=cb_store.new(1)))
    keyboard.add(*bnts)
    return keyboard


def get_store_menu(user_id, page, max_page, this_skin_id):
    keyboard = InlineKeyboardMarkup()
    db_sess = db_session.create_session()
    account_id = db_sess.query(users.Users).filter_by(user_id=user_id).first().id
    q_skin = db_sess.query(usersskins.UsersSkins).filter_by(user_id=account_id,
                                                            skin_id=this_skin_id).all()
    pagination = []
    if max_page < 7:
        pagination += [InlineKeyboardButton(str(i), callback_data=cb_store.new(i)) if i != page
                       else InlineKeyboardButton('[{}]'.format(page), callback_data='pass')
                       for i in range(1, max_page + 1)]
    elif page < 4:
        pagination += [InlineKeyboardButton(str(i), callback_data=cb_store.new(i)) if i != page
                       else InlineKeyboardButton('[{}]'.format(page), callback_data='pass')
                       for i in range(1, 6)] + \
                      [InlineKeyboardButton('...', callback_data='pass'),
                       InlineKeyboardButton(str(max_page), callback_data=cb_store.new(max_page))]
    elif max_page - page < 3:
        pagination += [InlineKeyboardButton('1', callback_data=cb_store.new(1)),
                       InlineKeyboardButton('...', callback_data='pass')] + \
                      [InlineKeyboardButton(str(i), callback_data=cb_store.new(i)) if i != page
                       else InlineKeyboardButton('[{}]'.format(page), callback_data='pass')
                       for i in range(max_page - 4, max_page + 1)]

    else:
        pagination += [InlineKeyboardButton('1', callback_data=cb_store.new(1)),
                       InlineKeyboardButton('...', callback_data='pass') if page - 1 > 3
                       else InlineKeyboardButton('2', callback_data=cb_store.new(2)),
                       InlineKeyboardButton(str(page - 1), callback_data=cb_store.new(page - 1)),
                       InlineKeyboardButton('[{}]'.format(page), callback_data='pass'),
                       InlineKeyboardButton(str(page + 1), callback_data=cb_store.new(page + 1)),
                       InlineKeyboardButton('...', callback_data='pass') if max_page - page > 3
                       else InlineKeyboardButton(str(page + 2), callback_data=cb_store.new(page + 2)),
                       InlineKeyboardButton(str(max_page), callback_data=cb_store.new(max_page))]
    btn_library = InlineKeyboardButton('My skins', callback_data='my_skins')
    if not q_skin and this_skin_id != -1:
        btn_buy = InlineKeyboardButton('Buy', callback_data=cb_buy.new(this_skin_id))
        keyboard.row(btn_buy)
    keyboard.row(*pagination)
    keyboard.row(btn_library)
    return keyboard


def get_pay():
    keyboard = InlineKeyboardMarkup()
    btn_pay = InlineKeyboardButton('Pay', pay=True)
    btn_cancel = InlineKeyboardButton('Close', callback_data='close')
    keyboard.row(btn_pay)
    keyboard.row(btn_cancel)
    return keyboard


def get_close():
    keyboard = InlineKeyboardMarkup()
    btn_cancel = InlineKeyboardButton('Close', callback_data='close')
    keyboard.row(btn_cancel)
    return keyboard

