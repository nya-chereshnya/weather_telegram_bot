import aiohttp
from datetime import datetime
from config import OPENWEATHER_API_KEY, TELEGRAM_BOT_TOKEN
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


class WeatherBot:
    def __init__(self, bot_token, openweather_token) -> None:
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher(self.bot)
        self.openweather_token = openweather_token

        self.dp.register_message_handler(
            self.start_command, commands=['start'])
        self.dp.register_message_handler(self.get_weather)

    async def start_command(self, message: types.Message) -> None:
        await message.reply('tell me the city and I will send the weather in it')

    async def get_weather(self, message: types.Message) -> None:
        message_text = message.text
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.openweathermap.org/data/2.5/weather?q={message_text}&appid={self.openweather_token}&units=metric') as response:
                data = await response.json()
            if data['cod'] == 200:
                city_data = self.parse_weather_data(data)
                await self.send_weather_message(message, city_data)
            else:
                await message.reply('check city name')

    def parse_weather_data(self, data) -> dict:
        city_data = {
            'city_name': data['name'],
            'city_temp': data['main']['temp'],
            'city_humidity': data['main']['humidity'],
            'city_pressure': data['main']['pressure'],
            'city_wind_speed': data['wind']['speed'],
            'city_sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S'),
            'city_sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S'),
            'city_day_length': datetime.fromtimestamp(data['sys']['sunset'] - data['sys']['sunrise']).strftime('%H:%M:%S')
        }
        return city_data

    async def send_weather_message(self, message: types.Message, city_data) -> None:
        response_message = (f'weather inforamtion for {city_data["city_name"]}:\n'
                            f'temperature: {city_data["city_temp"]}°C\n'
                            f'humidity: {city_data["city_humidity"]} %\n'
                            f'pressure: {city_data["city_pressure"]} hPa\n'
                            f'wind speed: {city_data["city_wind_speed"]} m/s\n'
                            f'sunrise: {city_data["city_sunrise"]}\n'
                            f'sunset: {city_data["city_sunset"]}\n'
                            f'day length: {city_data["city_day_length"]}')
        await self.bot.send_message(message.chat.id, response_message)

    def start(self) -> None:
        executor.start_polling(self.dp)


# if __name__ == '__main__':
#     weather_bot = WeatherBot(TELEGRAM_BOT_TOKEN, OPENWEATHER_TOKEN)
#     weather_bot.start()
