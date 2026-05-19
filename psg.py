import requests
import time
import re

TELEGRAM_TOKEN = "8774623526:AAG4IXZvcme1_5C_gLNGhvQNq3lLXV6ygQs"
CHAT_ID = "7853415869"

URLS_A_SURVEILLER = [
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
        for url in URLS_A_SURVEILLER:
            r = requests.get(url, headers=headers, timeout=15)
            contenu = r.text.lower()

            # Cherche les liens qui contiennent des mots clés billetterie
            liens = re.findall(r'href=["\']([^"\']*(?:retransmission|diffusion|billetterie)[^"\']*)["\']', contenu)

            if liens and not notif_envoyee:
                lien = liens[0]
                if not lien.startswith("http"):
                    lien = "https://www.psg.fr" + lien
                envoyer_telegram(
                    f"🚨 <b>BILLETTERIE PSG TROUVÉE !</b>\n\n"
                    f"🎉 Une page de billetterie finale/diffusion vient d'apparaître !\n\n"
                    f"👉 {lien}\n\n"
                    f"⚡ Fonce acheter !"
                )
                notif_envoyee = True
                print(f"✅ Lien trouvé : {lien}")
                return

            # Détecte aussi si le contenu a changé avec des mots clés
            anclen = contenu_precedent.get(url, "")
            if anclen and contenu != anclen:
                nouveaux_mots = [m for m in MOTS_CLES if m in contenu and m not in anclen]
                if nouveaux_mots and not notif_envoyee:
                    envoyer_telegram(
                        f"🚨 <b>PSG - NOUVEAU CONTENU BILLETTERIE !</b>\n\n"
                        f"Mots détectés : {', '.join(nouveaux_mots)}\n\n"
                        f"👉 {url}\n\n"
                        f"⚡ Va vérifier et achète !"
                    )
                    notif_envoyee = True
                    print(f"✅ Nouveau contenu : {nouveaux_mots}")

            contenu_precedent[url] = contenu

        print("⏳ Rien de nouveau...")

    except Exception as e:
        print(f"Erreur: {e}")

print("✅ Bot PSG démarré !")
envoyer_telegram("✅ Bot PSG Finale démarré — surveillance active !")

while True:
    verifier()
    time.sleep(30)
