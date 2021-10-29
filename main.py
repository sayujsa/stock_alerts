import requests
import datetime
import html
from twilio.rest import Client
import decouple

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
ALPHAVANTAGE_KEY = decouple.config("ALPHAVANTAGE_KEY")
NEWSAPI_KEY = decouple.config('NEWSAPI_KEY')
message_to_send = ".\n"
send_message = False


def get_news(emoji):
    # Creates the message to be sent via SMS
    global message_to_send
    news_response = requests.get("https://newsapi.org/v2/everything?"
                                 f"q={COMPANY_NAME}&"
                                 f"from={str(yesterday)}&"
                                 "sortBy=publishedAt&"
                                 "language=en&"
                                 "pageSize=3&"
                                 f"apiKey={NEWSAPI_KEY}")
    news_response.raise_for_status()
    message_to_send += f"{STOCK}: {emoji}{round((stock_percentage - 100), 1)}%\n\n"
    for x in news_response.json()['articles']:
        message_to_send += f"---------------\nHeadline: {html.unescape(x['title'])}\n\n" \
                           f"Brief: {html.unescape(x['description'])}\n\n\n"
    message_to_send = message_to_send.strip()


# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then get_news()
alpha_response = requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&"
                              f"symbol={STOCK}&apikey={ALPHAVANTAGE_KEY}")
alpha_response.raise_for_status()
yesterday = datetime.datetime.now().date() - datetime.timedelta(1)
day_before_yesterday = datetime.datetime.now().date() - datetime.timedelta(2)
yesterday_stock = float(alpha_response.json()['Time Series (Daily)'][str(yesterday)]['1. open'])
day_before_yesterday_stock = float(alpha_response.json()['Time Series (Daily)'][str(day_before_yesterday)]['1. open'])
stock_percentage = (yesterday_stock / day_before_yesterday_stock) * 100
if stock_percentage >= 101 or stock_percentage <= 95:
    if stock_percentage >= 101:
        get_news("🔺")
        send_message = True
    elif stock_percentage <= 95:
        get_news("🔻")
        send_message = True

if send_message:
    # Check to see if in need to send message, if so, sends one via SMS
    account_sid = decouple.config('ACCOUNT_SID')
    auth_token = decouple.config('AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message_to_send,
        from_=decouple.config('FROM_NUM'),
        to=decouple.config('TO_NUM')
    )
