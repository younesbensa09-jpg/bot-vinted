import requests
import time
import re

TELEGRAM_TOKEN = "8774623526:AAG4IXZvcme1_5C_gLNGhvQNq3lLXV6ygQs"
CHAT_ID = "7853415869"

URLS = [
    "https://www.psg.fr/billetterie",
    "https://www.psg.fr/matches",
    "https://billetterie.psg.fr",
]

MOTS_CLES = [
    "diffusion", "finale", "parc des princes", "ecran geant",
    "viewing", "fan zone", "30 mai", "budapest", "arsenal",
    "retransmission", "retransmission au parc", "alerte billetterie",
]

contenu_precedent = {}
notif_envoyee = False

def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})

def verifier():
    global notif_envoyee
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        for url in URLS:
            r = requests.get(url, headers=headers, timeout=15)
            contenu = r.text.lower()
            liens = re.findall(r'href=["\']([^"\']*(?:retransmission|diffusion|billetterie)[^"\']*)["\']', contenu)
            if liens and not notif_envoyee:
                lien = liens[0]
                if not lien.startswith("http"):
                    lien = "https://www.psg.fr" + lien
                envoyer_telegram(f"🚨 <b>BILLETTERIE PSG !</b>\n\n🎉 Page trouvée !\n\n👉 {lien}\n\n⚡ Fonce acheter !")
                notif_envoyee = True
                print(f"Lien : {lien}")
                return
            ancien = contenu_precedent.get(url, "")
            if ancien and contenu != ancien:
                nouveaux = [m for m in MOTS_CLES if m in contenu and m not in ancien]
                if nouveaux and not notif_envoyee:
                    envoyer_telegram(f"🚨 <b>PSG BILLETTERIE !</b>\n\nMots : {', '.join(nouveaux)}\n\n👉 {url}\n\n⚡ Va acheter !")
                    notif_envoyee = True
            contenu_precedent[url] = contenu
        print("Rien de nouveau...")
    except Exception as e:
        print(f"Erreur: {e}")

print("Bot PSG demarré !")
envoyer_telegram("✅ Bot PSG démarré !")

while True:
    verifier()
    time.sleep(30)
