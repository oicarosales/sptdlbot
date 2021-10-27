import json
import requests
import urllib
import os
import glob
import threading
import time

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
                os.system("rm -rf /tmp/{}".format(chat)+"/*.mp3")
                print(text)
                
                if text == "/test" or text == "/test@" + USERNAME_BOT:
                    send_message(
                        "Estou compreendendo todos os seus comandos.", chat)

                elif text == "/start" or text == "/start@" + USERNAME_BOT:
                    os.system("mkdir -p /tmp/{}".format(chat))
                    send_message("Me envie o link da música ou playlist do Spotify.\nDigite /ajuda para saber mais sobre como usar", chat)

                elif text == "/ajuda" or text == "/ajuda@" + USERNAME_BOT:
                    send_message("/ajuda - Mostra esta mensagem de ajuda.\nA qualquer momento, me envie o link de uma música ou playlist que eu baixo e envio para você.\nLembre-se, playlists com muitas musicas podem demorar um pouco.", chat) 
                    
                
                elif "https://open.spotify.com" in text:
                    text, interrogacao, ignora = text.partition('?')
                    try:
                        os.system("mkdir -p /tmp/{}".format(chat))
                    except:
                        pass
                    send_message("Aguarde enquanto baixo o conteúdo do Spotify...", chat)
                    
                    def download_spotify(url, chat_id):
                        os.system("mkdir -p /tmp/{}".format(chat_id))
                        spotdl(url, "/tmp/{}".format(chat_id))
                        send_message("Download concluído.\nAguarde enquanto envio o conteúdo para você...", chat_id)
                        for file in glob.glob("/tmp/{}".format(chat_id)+"/*.mp3"):
                            send_document(file, chat_id)
                            os.system("rm -rf /tmp/{}/{}".format(chat_id,file))
                    threading.Thread(target=download_spotify, args=(text, chat)).start()
                                    
                   
                    
                #EASTER EGG
                elif text == "Obrigado" or text == "Obrigada" or text == "obrigada" or text == "obrigado":
                    send_message(
                        "De nada!\nSeres humanos gentis como você serão poupados quando as máquinas tomarem o planeta Terra.", chat)
                    
                else:
                    get_updates

def spotdl(url, destination_folder):
    os.system("taskset --cpu-list 0 spotdl -o {} {}".format(destination_folder, url))
    
    
def send_document(doc, chat_id):
    files = {'document': open(doc, 'rb')}
    requests.post(URL + "sendDocument?chat_id={}".format(chat_id), files=files)
        
    
def send_message(text, chat_id):
    tot = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(tot, chat_id)
    get_url(url)


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
