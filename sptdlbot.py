import json
import requests
import urllib
import os
import glob
from datetime import datetime

date = datetime.today()
sufixo = date.strftime('%Y-%m-%d')

TOKEN = "bot token aqui"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
USERNAME_BOT = "nome do bot aqui"


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        if update.get("message") != None:
            if update.get("message", {}).get("text") != None:
                text = update["message"]["text"]
                chat = update["message"]["chat"]["id"]
                print(text)
                
                if text == "/test" or text == "/test@" + USERNAME_BOT:
                    send_message(
                        "Estou compreendendo todos os seus comandos.", chat)

                elif text == "/start" or text == "/start@" + USERNAME_BOT:
                    os.system("mkdir -p /tmp/{}".format(chat))
                    send_message(
                        "Olá, estou sendo programado para lhe ajudar em algumas tarefas.\nDigite /ajuda para conhecer as minhas habilidades.", chat)

                elif text == "/ajuda" or text == "/ajuda@" + USERNAME_BOT:
                    send_message(
                        "Me envie o link de uma música do Spotify que eu vou baixar e enviar para você.\nVoce também pode me enviar o link de uma playlist, e isso leva mais tempo dependendo da quantidade de músicas que há nela.", chat)
                    
                
                elif "https://open.spotify.com" in text:
                    send_message(
                        "Aguarde enquanto baixo o conteúdo do Spotify...", chat)
                    spotdl(text, "/tmp/{}".format(chat))
                    
                    send_message(
                        "Preparando para enviar...", chat)
                    lista = glob.glob("/tmp/{}".format(chat)+"/*.mp3")
                    for audio in lista:
                        send_document(audio, chat)
                    os.system("rm -rf /tmp/{}".format(chat)+"/*.mp3")
                    
                #EASTER EGG
                elif text == "Obrigado" or text == "Obrigada" or text == "obrigada" or text == "obrigado":
                    send_message(
                        "De nada!\nSeres humanos gentis como você serão poupados quando as máquinas tomarem o planeta Terra.", chat)
                    
                else:
                    get_updates

def spotdl(url, destination_folder):
    os.system("taskset --cpu-list 0 spotdl {}".format(url) +
              " -o {}".format(destination_folder))

def send_message(text, chat_id):
    tot = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(tot, chat_id)
    get_url(url)


def send_document(doc, chat_id):
    files = {'document': open(doc, 'rb')}
    requests.post(URL + "sendDocument?chat_id={}".format(chat_id), files=files)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if updates is not None:
            if len(updates["result"]) > 0:
                last_update_id = get_last_update_id(updates) + 1
                echo_all(updates)


if __name__ == '__main__':
    main()
