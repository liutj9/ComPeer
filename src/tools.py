import json
import requests
import datetime
from termcolor import colored
from src.settings import CITY
def get_today_info():
    city = CITY
    f = open('weather_json.json', 'rb')
    cities = json.load(f)
    city = cities.get(city)
    url = 'http://t.weather.sojson.com/api/weather/city/'
    response = requests.get(url + city)
    # print(response)
    d = response.json()
    if(d['status'] == 200):
        weather_data={
                      "today": d["time"]+" "+d["data"]["forecast"][0]["week"],
                      "temperature": d["data"]["forecast"][0]["high"]+" "+d["data"]["forecast"][0]["low"],
                      "weather": d["data"]["forecast"][0]["type"]
                      }
        weather_data["today"] = weather_data["today"][:10]+" "+weather_data["today"][19:]
        print(weather_data)
        return weather_data

def load_prompt(filename: str):
    file_path = f'prompt_en/{filename}'
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        print(colored(f'prompt文件加载成功！({file_path})', 'green'))
    except:
        print(colored(f'prompt文件: {file_path} 不存在', 'red'))
    return system_prompt



