import telebot

token = "8756879064:AAEltloWowA_mDnzlCE7-eBkGbbs25bAIdY"
bot = telebot.TeleBot(token)


cat_info = ("Коты — это высокотехнологичные существа с забавными «багами» в прошивке. Вот краткий дайджест их странностей: "
            "Жидкость и усы: Благодаря отсутствию ключиц коты — это официально жидкость, способная просочиться в любую щель, куда пролезла голова. А их усы (вибриссы) — это высокоточные датчики габаритов, которые иногда дают сбой после лишней порции корма. "
            "Режим «Ночной тыгыдык»: В 3 часа ночи у каждого кота открывается портал в другое измерение, требующий срочного забега по лицу хозяина со скоростью звука. "
            "Ошибка «Кусь»: Если кот сначала лижет твою руку, а потом резко кусает — это не агрессия, а «любовный кусь». У них просто перегружаются датчики нежности и вылетает ошибка Error: Too much cute. "
            "Кот Шрёдингера в миске: Если на дне миски показалось хотя бы крошечное пятнышко пустоты, для кота она считается абсолютно пустой. По их законам физики — это официальное объявление голодовки. "
            "Манипуляция: Коты почти не мяукают друг с другом. Этот звук они разработали специально для людей, чтобы эффективно выпрашивать еду и внимание.")

@bot.message_handler(commands=['start'])
def bot_start(message):
    bot.send_message(message.chat.id, "Приветствую! Это бот Графова Алексея. Функционал бота можно узнать по команде: /functional")

@bot.message_handler(commands=['functional'])
def functional_bot(message):
    bot.send_message(message.chat.id, "Этот бот умеет выводить определенную информацию по командам. Также ты можешь поменять текст команды на свой. "
                                      "\nКоманды бота:"
                                      "\n/start - приветствие "
                                      "\n/functional - Функционал бота "
                                      "\n/cat - про котиков "
                                      "\n/change - заменить текст команды /cat на свой")

@bot.message_handler(commands=['cat'])
def cat_bot(message):
    bot.send_message(message.chat.id, cat_info)

@bot.message_handler(commands=['change'])
def cat_text(message):
    msg = bot.send_message(message.chat.id, "Введите свой текст для команды /cat:")
    bot.register_next_step_handler(msg, new_text)

def new_text(message):
    global cat_info
    cat_info = message.text
    bot.send_message(message.chat.id, "Текст успешно изменен ^_^ ")


bot.polling(none_stop=True)