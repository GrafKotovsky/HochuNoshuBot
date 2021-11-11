from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import datetime
from datetime import timedelta
import requests
from config import API_KEY, NEW_KEY, TOKEN  # импортирую токены из файла config

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# получаю дату сегодня и вчера
get_today = datetime.datetime.now(datetime.timezone.utc)
today = get_today.strftime('%Y-%m-%d')
get_yesterday = get_today - timedelta(days=1)
yesterday = get_yesterday.strftime('%Y-%m-%d')

get_sunday = datetime.date.today()
weekday = get_sunday.weekday() + 1
sunday = str(get_sunday - datetime.timedelta(days=weekday % 7))

# запрос на получение продаж
SALES = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/sales?'
# запрос на получение заказов
ORDERS = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders?'
# запрос на получение сборочных заданий и параметры
TASKS = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/reportDetailByPeriod?'
tempDate = "https://suppliers-api.wildberries.ru/api/v2/orders?"
date = "date_start="+today+"T00%3A00%3A00%2B00%3A00&take=100&skip=0"
date2 = "date_start="+yesterday+"T00%3A00%3A00%2B00%3A00&date_end="+today+"T00%3A00%3A00%2B00%3A00&take=100&skip=0"
headers = {'Authorization': NEW_KEY}
search_task = 'https://suppliers-api.wildberries.ru/api/v2/stocks?search='
search_task2 = '&skip=0&take=150'
bar1 = 'https://barcode.tec-it.com/barcode.ashx?data='
bar2 = '&code=EAN13&translate-esc=on&download=true'
show_stock = 'https://suppliers-api.wildberries.ru/api/v2/stocks?search='
show_stock2 = '&skip=0&take=1000&sort=name'
# URL для ссылки на товар
URL1 = 'https://www.wildberries.ru/catalog/'
URL2 = '/detail.aspx?targetUrl=SP'
# запрос на получение стикеров
stk = 'https://suppliers-api.wildberries.ru/api/v2/orders/stickers/pdf?'
# мои клиенты
get_clients = "https://suppliers-api.wildberries.ru/api/v2/orders?date_start=2021-08-15T00%3A00%3A00.00Z&date_end="+today+"T00%3A00%3A00.00Z&take=1000&skip=0"
# кнопки бота:
# sales_menu
sales_today_btn = KeyboardButton('Продажи за сегодня')
sales_yest_btn = KeyboardButton('Продажи за вчера')
orders_today_btn = KeyboardButton('Заказы за сегодня')
orders_yest_btn = KeyboardButton('Заказы за вчера')
ref_today_btn = KeyboardButton('Возвраты за сегодня')
ref_yest_btn = KeyboardButton('Возвраты за вчера')
# main_menu
menu_sales = KeyboardButton('Продажи/Заказы/Возвраты')
menu_tasks = KeyboardButton('Сборочные задания')
menu_tot = KeyboardButton('Итоги')
# back
back = KeyboardButton('Назад')
#tasks
tasks_td = KeyboardButton('Задания Сегодня')
tasks_yt = KeyboardButton('Задания Вчера')
make_bar = KeyboardButton('Сделать баркоды на задания')
#total
tot_btn_td = KeyboardButton('Итоги за сегодня')
tot_btn_wk = KeyboardButton('Итоги за неделю')

sales_menu = ReplyKeyboardMarkup(resize_keyboard=True).row(sales_today_btn, orders_today_btn, ref_today_btn).add(sales_yest_btn, orders_yest_btn, ref_yest_btn).row(back)
main_menu = ReplyKeyboardMarkup(resize_keyboard=True).row(menu_sales, menu_tasks, menu_tot)
back_btn = ReplyKeyboardMarkup(resize_keyboard=True).row(back)
tasks = ReplyKeyboardMarkup(resize_keyboard=True).row(tasks_td, tasks_yt, back)
menu_tot = ReplyKeyboardMarkup(resize_keyboard=True).row(tot_btn_td, tot_btn_wk, back)

response = None
response_1 = None
response_2 = None
response_3 = None
response_4 = None
response_5 = None
new_tasks = None
yt_tasks = None


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Привет! Выбери меню', reply_markup=main_menu)


@dp.message_handler()
async def menus(message: types.Message):
    global response, response_1, response_2, response_3, response_4, response_5, new_tasks, yt_tasks
    #keyboards
    if message.text == 'Продажи/Заказы/Возвраты':
        await bot.send_message(message.from_user.id, 'Выбери кнопку ниже', reply_markup=sales_menu)
    elif message.text == 'Назад':
        await bot.send_message(message.from_user.id, 'Выбери меню', reply_markup=main_menu)
    elif message.text == 'Сборочные задания':
        await bot.send_message(message.from_user.id, 'Выбери кнопку ниже', reply_markup=tasks)
    elif message.text == 'Итоги':
        await bot.send_message(message.from_user.id, 'Выбери кнопку ниже', reply_markup=menu_tot)
    # получаю заказы
    elif message.text == 'Заказы за вчера':
        counter = 0
        try:
            req_orders_yt = requests.get(f'{ORDERS}dateFrom={yesterday}&flag=1&key={API_KEY}')
            response = req_orders_yt.json()
            if not response.status_code // 100 == 2:
                return "Error: Unexpected response {}".format(response)
        except Exception as ex:
            print(ex)
            pass
        for i in response:
            orders_yt = (URL1 + str(i['nmId']) + URL2)
            count_discont = i['totalPrice'] * (i['discountPercent'] / 100)
            price_with_discount = i['totalPrice'] - count_discont
            counter += price_with_discount
            await bot.send_message(message.from_user.id, orders_yt)
        total = 'Сумма заказов за вчерашний день = ' + str(counter) + ' ₽'
        rm_sig = (''.join([i for i in total]))
        await bot.send_message(message.from_user.id, rm_sig)
    elif message.text == 'Заказы за сегодня':
        counter = 0
        try:
            req_orders_td = requests.get(f'{ORDERS}dateFrom={today}&flag=1&key={API_KEY}')
            response_1 = req_orders_td.json()
            if not response_1.status_code // 100 == 2:
                return "Error: Unexpected response {}".format(response_1)
        except Exception as ex:
            print(ex)
            pass
        for i in response_1:
            orders_td = (URL1 + str(i['nmId']) + URL2)
            count_discont = int(i['totalPrice'] * (i['discountPercent'] / 100))
            price_with_discount = int(i['totalPrice'] - count_discont)
            counter += price_with_discount
            await bot.send_message(message.from_user.id, orders_td)
        total = 'Сумма заказов за сегодняшний день = ' + str(counter) + ' ₽'
        rm_sig = (''.join([i for i in total]))
        await bot.send_message(message.from_user.id, rm_sig)
    # получаю продажи
    elif message.text == 'Продажи за сегодня':
        counter = 0
        try:
            req_sales_td = requests.get(f'{SALES}dateFrom={today}&flag=1&key={API_KEY}')
            response_2 = req_sales_td.json()
            if not response_2.status_code // 100 == 2:
                return "Error: Unexpected response {}".format(response_2)
        except Exception as ex:
            print(ex)
            pass
        for i in response_2:
            if i['quantity'] >= 1:
                sales_td = (URL1 + str(i['nmId']) + URL2)
                price_with_discount = int(i['totalPrice'] * ((100 - i['discountPercent']) / 100) * ((100 - i['promoCodeDiscount']) / 100) * ((100 - i['spp']) / 100))
                counter += price_with_discount
                await bot.send_message(message.from_user.id, sales_td)
        total = 'Сумма продаж за сегодняшний день = '+str(counter)+' ₽'
        rm_sig = (''.join([i for i in total]))
        await bot.send_message(message.from_user.id, rm_sig)
    elif message.text == 'Продажи за вчера':
        counter = 0
        try:
            req_sales_yt = requests.get(f'{SALES}dateFrom={yesterday}&flag=1&key={API_KEY}')
            response_3 = req_sales_yt.json()
            if not response_3.status_code // 100 == 2:
                return "Error: Unexpected response {}".format(response_3)
        except Exception as ex:
            print(ex)
            pass
        for i in response_3:
            if i['quantity'] >= 1:
                sales_yt = (URL1 + str(i['nmId']) + URL2)
                price_with_discount = int(i['totalPrice'] * ((100 - i['discountPercent']) / 100) * ((100 - i['promoCodeDiscount']) / 100) * ((100 - i['spp']) / 100))
                counter += price_with_discount
                await bot.send_message(message.from_user.id, sales_yt)
        total = 'Сумма продаж за вчерашний день = '+str(counter)+' ₽'
        rm_sig = (''.join([i for i in total]))
        await bot.send_message(message.from_user.id, rm_sig)
    # получаю возвраты
    elif message.text == 'Возвраты за сегодня':
        counter = 0
        try:
            req_sales_td = requests.get(f'{SALES}dateFrom={today}&flag=1&key={API_KEY}')
            response_4 = req_sales_td.json()
            if not response_4.status_code // 100 == 2:
                return "Error: Unexpected response {}".format(response_4)
        except Exception as ex:
            print(ex)
            pass
        for i in response_4:
            if i['quantity'] <= -1:
                ref_today = (URL1 + str(i['nmId']) + URL2)
                counter += i['priceWithDisc']
                await bot.send_message(message.from_user.id, ref_today)
        total = 'Сумма возвратов за сегодняшний день: ' + str(counter) + ' ₽'
        rm_sig = (''.join([i for i in total]))
        await bot.send_message(message.from_user.id, rm_sig)
    elif message.text == 'Возвраты за вчера':
        counter = 0
        try:
            req_sales_yt = requests.get(f'{SALES}dateFrom={yesterday}&flag=1&key={API_KEY}')
            response_5 = req_sales_yt.json()
            if not response_5.status_code // 100 == 2:
                return "Error: Unexpected response {}".format(response_5)
        except Exception as ex:
            print(ex)
            pass
        for i in response_5:
            if i['quantity'] <= -1:
                ref_yest = (URL1 + str(i['nmId']) + URL2)
                counter += i['priceWithDisc']
                await bot.send_message(message.from_user.id, ref_yest)
        total = 'Сумма возвратов за вчерашний день: ' + str(counter) + ' ₽'
        rm_sig = (''.join([i for i in total]))
        await bot.send_message(message.from_user.id, rm_sig)
    elif message.text == 'Задания Сегодня':
        try:
            td_tasks = requests.get(tempDate, date, headers=headers)
            new_tasks = td_tasks.json()
            req_orders_td = requests.get(f'{ORDERS}dateFrom={today}&flag=1&key={API_KEY}')
            response = req_orders_td.json()
        except Exception as ex:
            print(ex)
            pass
        for i in new_tasks['orders']:
            data = i['barcode']
            data_task = requests.get(search_task + data + search_task2, headers=headers).json()
            for j in data_task['stocks']:
                data_task_td = j['brand'], j['name'], j['article'], j['size'], j['barcode']
                goods = ('\n'.join([i for i in data_task_td]))
                code = bar1 + j['barcode'] + bar2
                await bot.send_message(message.from_user.id, str(goods))
                await bot.send_message(message.from_user.id, str(code))
    elif message.text == 'Задания Вчера':
        try:
            yt_tasks = requests.get(tempDate, date2, headers=headers)
            new_tasks = yt_tasks.json()
            req_orders_yt = requests.get(f'{ORDERS}dateFrom={yesterday}&flag=1&key={API_KEY}')
            response = req_orders_yt.json()
        except Exception as ex:
            print(ex)
            pass
        for i in new_tasks['orders']:
            data = str(i['barcode'])
            data_task = requests.get(search_task + data + search_task2, headers=headers).json()
            for j in data_task['stocks']:
                data_task_td = j['brand'], j['name'], j['article'], j['size'], j['barcode']
                check = ('\n'.join([i for i in data_task_td]))
                code = bar1 + j['barcode'] + bar2
                await bot.send_message(message.from_user.id, str(check))
                await bot.send_message(message.from_user.id, str(code))
    elif message.text == 'Итоги за сегодня':
        counter_s = 0
        counter_o = 0
        counter_r = 0
        sales_tod = None
        orders_tod = None
        try:
            sales_tod = requests.get(f'{SALES}dateFrom={today}&flag=1&key={API_KEY}', timeout=2).json()
            orders_tod = requests.get(f'{ORDERS}dateFrom={today}&flag=1&key={API_KEY}', timeout=1).json()
        except Exception as ex:
            print(ex)
            pass
        for i in sales_tod:
            if i['quantity'] >= 1:
                price_with_discount = int(i['totalPrice'] * ((100 - i['discountPercent']) / 100) * ((100 - i['promoCodeDiscount']) / 100) * ((100 - i['spp']) / 100))
                counter_s += price_with_discount
        total_1 = 'Продажи: '+str(counter_s)+' ₽'
        for k in orders_tod:
            count_discont = int(k['totalPrice'] * (k['discountPercent'] / 100))
            price_with_discount = int(k['totalPrice'] - count_discont)
            counter_o += price_with_discount
        total_2 = 'Заказы: ' + str(counter_o) + ' ₽'
        for j in sales_tod:
            if j['quantity'] <= -1:
                counter_r += j['priceWithDisc']
        total_3 = 'Возвраты: ' + str(counter_r) + ' ₽'
        total = total_1, total_2, total_3
        rm_sig = ('\n'.join([i for i in total]))
        await bot.send_message(message.from_user.id, rm_sig)
executor.start_polling(dp)
