from tgclient import *
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=2, decode_responses=True)
token = ''
bot = TelegramBot(token, True)
admins = [463152143]
full_admin = 463152143
chat_ids = [-1001398292750, -1001289729560]
channel_id = '@PG_SOUND'
print("Bot Now is Runnig !!!")


@bot.message('text')
def message_handler(message):
    matches = message['text']
    chat_id = message['chat']['id']

    if matches == '/start':
        if message['from']['id'] in admins:
            bot.sendMessage(chat_id, 'Hi', reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text='👍', callback_data='LIKE'),
                    InlineKeyboard(text='👎', callback_data='disLIKE')
                ],
            ]
        }, parse_mode='Markdown')
    
@bot.message('audio')
def audio_handler(message):
    if message['chat']['id'] in chat_ids:
        caption = f"👤 {message['from']['first_name']}\n\n📣 @PG_sound"
        bot.sendAudio(full_admin, message['audio']['file_id'], caption=caption, reply_markup={
                'inline_keyboard': [
                    [
                        InlineKeyboard(text='Accept ✅', callback_data='accept'),
                    ],
                ]
            })

@bot.callback_query()
def callback(message):
    data=message['data']
    chat_id = message['message']['chat']['id']
    from_id = message['from']['id']
    message_id = message['message']['message_id']
    if data == 'accept':
        send = bot.sendAudio(channel_id, str(message['message']['audio']['file_id']), caption=message['message']['caption'], reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text='👍', callback_data=f'LIKE_{message["id"]}'),
                    InlineKeyboard(text='👎', callback_data=f'disLIKE_{message["id"]}')
                ],
            ]
        })
        if send:
            bot.deleteMessage(message['message']['chat']['id'], message_id)
        else:
            bot.answerCallbackQuery(message['id'], f'⚠️ محدودیت ارسال / چند ثانیه صبر کنید', True)
    elif data.split('_')[0] == 'LIKE':
        r.sadd(f"LIKE:{message_id}", from_id)
        r.srem(f"disLIKE:{message_id}", from_id)
        like_count = r.scard(f"LIKE:{message_id}")
        dislike_count = r.scard(f"disLIKE:{message_id}")
        bot.answerCallbackQuery(message['id'], 'رای شما با موفقیت ثبت شد ✅', True)
        bot.editMessageReplyMarkup(chat_id, message_id, reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text=f'👍 {like_count}', callback_data=f'LIKE_{message["id"]}'),
                    InlineKeyboard(text=f'👎 {dislike_count}', callback_data=f'disLIKE_{message["id"]}')
                ],
            ]
        })
    elif data.split('_')[0] == 'disLIKE':
        r.sadd(f"disLIKE:{message_id}", from_id)
        r.srem(f"LIKE:{message_id}", from_id)
        like_count = r.scard(f"LIKE:{message_id}")
        dislike_count = r.scard(f"disLIKE:{message_id}")
        bot.answerCallbackQuery(message['id'], 'رای شما با موفقیت ثبت شد ✅', True)
        bot.editMessageReplyMarkup(chat_id, message_id, reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text=f'👍 {like_count}', callback_data=f'LIKE_{message["id"]}'),
                    InlineKeyboard(text=f'👎 {dislike_count}', callback_data=f'disLIKE_{message["id"]}')
                ],
            ]
        })

try:
    bot.run(report_http_errors=False)
except:
    print('Error!')
