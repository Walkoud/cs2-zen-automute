import json
import logging
import time
from flask import Flask, request
from pynput.keyboard import Controller

app = Flask(__name__)
keyboard = Controller()
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# --- CONFIGURATION ---
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {
        "key_bindings": {"mute": "o", "unmute": "p"},
        "settings": {"min_switch_delay": 0.3, "server_port": 3000, "server_host": "127.0.0.1"},
        "voicemeeter": {"enabled": False, "kind": "banana", "button_index": 0}
    }

VM_ENABLED = config['voicemeeter']['enabled']
VM_KIND = config['voicemeeter']['kind']
VM_BUTTON_INDEX = config['voicemeeter']['button_index']

is_muted = False
last_health = 100
last_action_time = 0
my_steamid = None  # Stockage de ton ID au premier paquet reçu

# --- INITIALISATION API ---
vm = None
if VM_ENABLED:
    try:
        import voicemeeterlib
        vm = voicemeeterlib.api(VM_KIND)
        vm.login()
    except Exception as e:
        print(f"!! Erreur connexion Voicemeeter : {e}")
        VM_ENABLED = False

def set_volume(action):
    global is_muted, last_action_time
    now = time.time()
    if now - last_action_time < config['settings']['min_switch_delay']:
        return

    state = 1 if action == "mute" else 0
    if is_muted == (state == 1): return

    if VM_ENABLED and vm:
        try:
            vm.button[VM_BUTTON_INDEX].state = state
            print(f">> VM API : {action.upper()}")
        except: pass
    else:
        key = config['key_bindings']['mute'] if action == "mute" else config['key_bindings']['unmute']
        keyboard.press(key)
        keyboard.release(key)
        print(f">> CLAVIER : {action.upper()}")
    
    is_muted = (state == 1)
    last_action_time = now

@app.route('/', methods=['POST'])
def gsi_listener():
    global last_health, my_steamid
    data = request.json
    if not data: return 'OK', 200
    if data:
        print(f"Provider présent: {'provider' in data}")
        print(f"SteamID: {data.get('provider', {}).get('steamid')}")

    try:
        # 1. Récupération des IDs
        current_my_sid = data.get('provider', {}).get('steamid')
        player = data.get('player', {})
        observed_sid = player.get('steamid')

        # Debug : Affiche ton SteamID une seule fois au lancement
        if current_my_sid and my_steamid is None:
            my_steamid = current_my_sid
            print(f"\n[INFO] Ton SteamID a été détecté : {my_steamid}")
            print("[INFO] Filtrage spectateur activé.\n")

        # --- LOGIQUE DE DÉCISION ---
        
        # CAS A : On regarde quelqu'un d'autre (SID différent)
        if observed_sid and current_my_sid and observed_sid != current_my_sid:
            if not is_muted:
                print(f"[SPECTATE] Target: {player.get('name', '???')} -> Mute")
                set_volume("mute")
            last_health = 0 # Prépare le respawn
            return 'OK', 200

        # CAS B : C'est NOUS (SID identiques)
        if observed_sid == current_my_sid and 'state' in player and 'health' in player['state']:
            hp = player['state']['health']
            
            if hp != last_health:
                if hp == 0:
                    print("[MORT] HP à 0 -> Mute")
                    set_volume("mute")
                elif hp > 0:
                    if is_muted:
                        print(f"[ALIVE] Respawn détecté ({hp} HP) -> Unmute")
                        set_volume("unmute")
                
                last_health = hp

    except Exception as e:
        pass

    return 'OK', 200

if __name__ == '__main__':
    try:
        print(f"Démarrage GSI sur port {config['settings']['server_port']}...")
        print("En attente de données venant de CS2 (lance une partie)...")
        app.run(port=config['settings']['server_port'], host=config['settings']['server_host'])
    finally:
        if vm: vm.logout()