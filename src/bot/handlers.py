from aiogram import types
from aiogram.utils.markdown import hide_link

from database import db_session, users, skins, usersskins
from bot.keyboards import get_menu, get_store_menu, get_pay
from bot.menu import set_starting_commands
from bot.bot_init import bot
from utils.load_local_variables import BANK_TOKEN
from utils.loggers import logger_message


async def start_message(message: types.Message):
    await set_starting_commands(bot, message.chat.id)
    db_sess = db_session.create_session()
    q = db_sess.query(users.Users).filter_by(user_id=message.from_user.id)
    if not q.all():
        user = users.Users(user_id=message.from_user.id)
        db_sess.add(user)
        db_sess.commit()
    await message.answer('Welcome, <b>{}</b>!'.format(message.from_user.username),
                         reply_markup=get_menu())
    await message.delete()
    extra = {
        'user': message.from_user.username,
        'user_id': message.from_user.id,
        'content_type': '/start'
    }
    logger_message.info(message, extra=extra)


async def help_message(message: types.Message):
    await message.answer('This is a bot for buying skins.')
    extra = {
        'user': message.from_user.username,
        'user_id': message.from_user.id,
        'content_type': '/help'
    }
    logger_message.info(message, extra=extra)


async def library(callback: types.CallbackQuery):
    await callback.answer()
    db_sess = db_session.create_session()
    skins_in_account = [db_sess.query(skins.Skins).filter_by(id=i.skin_id).first()
                        for i in db_sess.query(usersskins.UsersSkins).filter_by(
            user_id=db_sess.query(users.Users).filter_by(user_id=callback.from_user.id).first().id).all()]
    if skins_in_account:
        await bot.edit_message_text(
            text='<b>{} skins</b>\n\n'.format(callback.from_user.username) +
                 '\n'.join('<b>{}</b>'.format(i.title)
                           for i in skins_in_account),
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=get_menu(my_skins=False))
    else:
        await bot.edit_message_text(
            text='<b>There are no purchased skins on the {} account😞</b>\n\n'.format(callback.from_user.username),
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=get_menu(my_skins=False))
    extra = {
        'user': callback.from_user.username,
        'user_id': callback.from_user.id,
        'content_type': 'view library'
    }
    logger_message.info(callback.message, extra=extra)


async def store(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    db_sess = db_session.create_session()
    q = db_sess.query(skins.Skins)
    all_skins = q.all()
    page = int(callback_data['page'])
    max_page = len(all_skins)
    if page <= max_page:
        this_skin = all_skins[page - 1]
        await bot.edit_message_text(text='<b>Page:</b> {}\n\n'
                                         '{}'
                                         '<b>{}</b>\n'
                                         '{}\n'
                                         '<b>Price:</b> {} RUB'.format(
            page,
            hide_link(this_skin.image),
            this_skin.title,
            '<em>{}</em>\n'.format(
                this_skin.description)
            if this_skin.description else '',
            this_skin.price + this_skin.price * 0.01),
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            reply_markup=get_store_menu(callback.from_user.id,
                                        page,
                                        max_page,
                                        this_skin.id))
    else:
        await bot.edit_message_text(message_id=callback.message.message_id,
                                    chat_id=callback.message.chat.id,
                                    text='This page not found 👀',
                                    reply_markup=get_store_menu(callback.from_user.id,
                                                                page,
                                                                max_page,
                                                                -1))
    extra = {
        'user': callback.from_user.username,
        'user_id': callback.from_user.id,
        'content_type': 'load store'
    }
    logger_message.info(callback.message, extra=extra)


async def passing(callback: types.CallbackQuery):
    await callback.answer()


async def payload(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    db_sess = db_session.create_session()
    skin = db_sess.query(skins.Skins).filter_by(id=callback_data['skin_id']).first()
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await bot.send_invoice(chat_id=callback.message.chat.id,
                           title=skin.title,
                           description='Purchase of {}'.format(skin.title),
                           payload=skin.id,
                           provider_token=BANK_TOKEN,
                           currency='RUB',
                           start_parameter='pay',
                           prices=[{'label': 'Skin', 'amount': int(skin.price * 100)},
                                   {'label': 'Store commission', 'amount': int(skin.price)}],
                           reply_markup=get_pay())
    extra = {
        'user': callback.from_user.username,
        'user_id': callback.from_user.id,
        'content_type': 'start payment'
    }
    logger_message.info(callback.message, extra=extra)


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    db_sess = db_session.create_session()
    q = db_sess.query(usersskins.UsersSkins).filter_by(user_id=pre_checkout_query.from_user.id,
                                                       skin_id=pre_checkout_query.invoice_payload).all()
    if not q:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    else:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False,
                                            error_message='You already have this skin in your library')
    extra = {
        'user': pre_checkout_query.from_user.username,
        'user_id': pre_checkout_query.from_user.id,
        'content_type': 'passed the pre checkout query'
    }
    logger_message.info(pre_checkout_query, extra=extra)


async def process_pay(message: types.Message):
    db_sess = db_session.create_session()
    account = db_sess.query(users.Users).filter_by(user_id=message.from_user.id).first()
    skin = db_sess.query(skins.Skins).filter_by(id=message.successful_payment.invoice_payload).first()
    account.skins.append(skin)
    db_sess.add(account)
    db_sess.commit()
    await message.delete()
    await bot.send_message(message.from_user.id, 'Thank you for buying {} ❤️'.format(skin.title),
                           reply_markup=get_menu())
    extra = {
        'user': message.from_user.username,
        'user_id': message.from_user.id,
        'content_type': 'purchase skin ({})'.format(skin.title)
    }
    logger_message.info(message, extra=extra)


async def push_close(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    extra = {
        'user': callback.from_user.username,
        'user_id': callback.from_user.id,
        'content_type': 'close purchase'
    }
    logger_message.info(callback.message, extra=extra)
