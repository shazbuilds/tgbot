import telebot
import json
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 123456789
JADVAL = {
    "dushanba": "Python 15:00",
    "seshanba": "Backend 14:00",
    "chorshanba": "Python 15:00",
    "payshanba": "Frontend 14:00",
    "juma": "Cyber 15:00",
}

SAVOLLAR = [
    ("Python'da ro'yxat qanday belgilanadi?", ["[ ]", "{ }", "( )"], 0),
    ("Ekranga yozuv chiqarish funksiyasi qaysi?", ["input()", "print()", "len()"], 1),
    ("2 ** 3 nimaga teng?", ["6", "9", "8"], 2),
]

test_holat = {}


def asosiy_menyu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(" Dars jadvali", " Ro'yxatdan o'tish")
    markup.row(" Test", " Yordam")
    return markup


def royxatni_oqi():
    try:
        with open("royxat.json") as f:
            return json.load(f)
    except:
        return {}


def royxatni_yoz(malumot):
    with open("royxat.json", "w") as f:
        json.dump(malumot, f)


@bot.message_handler(commands=['start'])
def start(message):
    ism = message.from_user.first_name
    bot.send_message(message.chat.id,
                     f"Salom, <b>{ism}</b>! \nMen <i>Ustudy</i> maktab botiman.\nBuyruqlar: /help",
                     parse_mode="HTML", reply_markup=asosiy_menyu())


@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda m: m.text == "ℹ Yordam")
def yordam(message):
    bot.reply_to(message, "/start — boshlash\n/jadval — dars jadvali\n/jadval juma — bitta kun\n"
                          "/royxat — ro'yxatdan o'tish\n/test — mini test\n/id — chat_id")


@bot.message_handler(commands=['id'])
def mening_id(message):
    bot.reply_to(message, f"Sizning chat_id: {message.chat.id}")


@bot.message_handler(commands=['jadval'])
@bot.message_handler(func=lambda m: m.text == " Dars jadvali")
def jadval(message):
    qismlar = message.text.split()
    if len(qismlar) > 1:
        kun = qismlar[1].lower()
        if kun in JADVAL:
            bot.reply_to(message, f"{kun.capitalize()}: {JADVAL[kun]}")
        else:
            bot.reply_to(message, "Bunday kun yo'q. Masalan: /jadval juma")
    else:                                     # hamma kunlar
        matn = " Dars jadvali:\n"
        for kun in JADVAL:
            matn += f" {kun.capitalize()}: {JADVAL[kun]}\n"
        bot.reply_to(message, matn)

@bot.message_handler(commands=['royxat'])
@bot.message_handler(func=lambda m: m.text == "Ro'yxatdan o'tish")
def royxat(message):
    javob = bot.send_message(message.chat.id, "Ismingizni yozing:")
    bot.register_next_step_handler(javob, ism_qabul)


def ism_qabul(message):
    ism = message.text
    javob = bot.send_message(message.chat.id, "Yoshingiz nechada?")
    bot.register_next_step_handler(javob, yosh_qabul, ism)


def yosh_qabul(message, ism):
    if not message.text.isdigit():
        javob = bot.send_message(message.chat.id, "Yoshni raqam bilan yozing:")
        bot.register_next_step_handler(javob, yosh_qabul, ism)
        return
    telefon_sora(message.chat.id, ism, message.text)


def telefon_sora(chat_id, ism, yosh):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("Raqamni yuborish", request_contact=True))
    javob = bot.send_message(chat_id, "Telefon raqamingizni tugma orqali yuboring ",
                             reply_markup=markup)
    bot.register_next_step_handler(javob, telefon_qabul, ism, yosh)


def telefon_qabul(message, ism, yosh):
    if message.contact is None:
        telefon_sora(message.chat.id, ism, yosh)
        return
    malumot = royxatni_oqi()
    malumot[str(message.chat.id)] = {"ism": ism, "yosh": yosh,
                                     "telefon": message.contact.phone_number}
    royxatni_yoz(malumot)
    bot.send_message(message.chat.id, "✅ Ro'yxatdan o'tdingiz!", reply_markup=asosiy_menyu())


@bot.message_handler(commands=['royxatlar'])
def royxatlar(message):
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "Faqat admin uchun.")
        return
    bot.reply_to(message, f"Ro'yxatdan o'tganlar: {len(royxatni_oqi())} ta")



@bot.message_handler(commands=['test'])
@bot.message_handler(func=lambda m: m.text == "Test")
def test(message):
    test_holat[message.chat.id] = {"nomer": 0, "ball": 0}
    savol_yubor(message.chat.id)


def savol_yubor(chat_id):
    n = test_holat[chat_id]["nomer"]
    if n == len(SAVOLLAR):
        ball = test_holat[chat_id]["ball"]
        bot.send_message(chat_id, f"Natija: {ball} / {len(SAVOLLAR)}")
        del test_holat[chat_id]
        return
    savol, variantlar, togri = SAVOLLAR[n]
    markup = telebot.types.InlineKeyboardMarkup()
    for i in range(len(variantlar)):
        markup.add(telebot.types.InlineKeyboardButton(variantlar[i], callback_data=str(i)))
    bot.send_message(chat_id, f"{n + 1}/{len(SAVOLLAR)}: {savol}", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: True)
def javob(call):
    chat_id = call.message.chat.id
    if chat_id not in test_holat:
        bot.answer_callback_query(call.id, "Avval /test bosing")
        return
    n = test_holat[chat_id]["nomer"]
    if int(call.data) == SAVOLLAR[n][2]:
        test_holat[chat_id]["ball"] += 1
        bot.answer_callback_query(call.id, " To'g'ri!")
    else:
        bot.answer_callback_query(call.id, " Noto'g'ri")
    bot.edit_message_reply_markup(chat_id, call.message.message_id)   # tugmalarni o'chirish
    test_holat[chat_id]["nomer"] += 1
    savol_yubor(chat_id)


@bot.message_handler(content_types=['photo'])
def rasm(message):
    bot.reply_to(message, "📷 Rasm qabul qilindi! Chiroyli ekan.")


@bot.message_handler(content_types=['sticker'])
def stiker(message):
    bot.send_sticker(message.chat.id, message.sticker.file_id)


@bot.message_handler(content_types=['location'])
def joy(message):
    lat, lon = message.location.latitude, message.location.longitude
    bot.reply_to(message, f"📍 Siz shu yerdasiz: {lat:.4f}, {lon:.4f}")
    bot.send_location(message.chat.id, 41.3111, 69.2797)


@bot.message_handler(func=lambda m: True)
def boshqa(message):
    bot.reply_to(message, "Tushunmadim  /help yoki tugmalardan foydalaning")


bot.infinity_polling()