import json
import grequests
import time

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

token = config['TOKEN']
language = config['LANGUAGE']
theme = config['THEME']
remove_friends = config['REMOVE_FRIENDS']
message_text = config['MESSAGE_TEXT']
leave_guilds = config['LEAVE_GUILDS']
block_friends = config['BLOCK_FRIENDS']
theme_carousel = config.get('THEME_CAROUSEL', False)

headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

def get_friends():
    response = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении списка друзей: {response.status_code} - {response.text}")
        return []

def send_message(user_id, message):
    payload = {"recipient_id": user_id}
    response = requests.post("https://discord.com/api/v9/users/@me/channels", headers=headers, json=payload)

    if response.status_code == 200:
        channel_id = response.json()['id']

        message_payload = {"content": message}
        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers, json=message_payload)

        if response.status_code == 200:
            print(f"Отправлено '{message}' пользователю {user_id}")
            return channel_id
        else:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {response.status_code} - {response.text}")
            return None
    else:
        print(f"Ошибка при создании ЛС-канала для пользователя {user_id}: {response.status_code} - {response.text}")
        return None

def delete_channel(channel_id):
    response = requests.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)

    if response.status_code == 204:
        print(f"Удален канал {channel_id}")
    else:
        print(f"Ошибка при удалении канала {channel_id}: {response.status_code} - {response.text}")

def remove_friend(user_id):
    response = requests.delete(f"https://discord.com/api/v9/users/@me/relationships/{user_id}", headers=headers)

    if response.status_code == 204:
        print(f"Удален пользователь {user_id} из друзей")
    else:
        print(f"Ошибка при удалении друга {user_id}: {response.status_code} - {response.text}")

def block_user(user_id):
    payload = {"type": 2}
    response = requests.put(f"https://discord.com/api/v9/users/@me/relationships/{user_id}", headers=headers, json=payload)

    if response.status_code == 204:
        print(f"Пользователь {user_id} заблокирован")
    else:
        print(f"Ошибка при блокировке пользователя {user_id}: {response.status_code} - {response.text}")

def change_language(language_code):
    payload = {"locale": language_code}
    response = requests.patch("https://discord.com/api/v9/users/@me/settings", headers=headers, json=payload)

    if response.status_code == 200:
        print(f"Язык изменен на {language_code}")
    else:
        print(f"Ошибка при изменении языка: {response.status_code} - {response.text}")

def change_theme(theme):
    payload = {"theme": theme}
    response = requests.patch("https://discord.com/api/v9/users/@me/settings", headers=headers, json=payload)

    if response.status_code == 200:
        print(f"Тема изменена на {theme}")
    else:
        print(f"Ошибка при изменении темы: {response.status_code} - {response.text}")


def theme_carousel():
    start_time = time.time()
    while time.time() - start_time < 10:
        change_theme("light")
        time.sleep(0.01)
        change_theme("dark")
        time.sleep(0.01)

def leave_guild(guild_id):
    while True:
        response = requests.delete(f"https://discord.com/api/v9/users/@me/guilds/{guild_id}", headers=headers)

        if response.status_code == 204:
            print(f"Покинут сервер {guild_id}")
            break
        elif response.status_code == 429:
            retry_after = response.json().get("retry_after", 1)
            print(f"Ошибка при выходе с сервера {guild_id}: {response.status_code} - {response.text}. Повтор через {retry_after} секунд")
            time.sleep(retry_after)
        else:
            print(f"Ошибка при выходе с сервера {guild_id}: {response.status_code} - {response.text}")
            break

def get_guilds():
    response = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении списка серверов: {response.status_code} - {response.text}")
        return []

def main():
    change_language(language)
    change_theme(theme)

    if theme_carousel:
        theme_carousel()

    if leave_guilds:
        guilds = get_guilds()
        for guild in guilds:
            leave_guild(guild['id'])

    friends = get_friends()
    if not friends:
        print("Список друзей пуст")
        return
    for friend in friends:
        channel_id = send_message(friend['id'], message_text)
        if channel_id:
            delete_channel(channel_id)
        if remove_friends:
            remove_friend(friend['id'])
        if block_friends:
            block_user(friend['id'])

if __name__ == "__main__":
    main()
