# CS2 GSI Auto Mute (Python)

A small Python tool that listens to **Counter-Strike 2 Game State Integration (GSI)** events and automatically **mutes / unmutes the game audio** when:

- You **die** (HP becomes 0) => **mute**
- You **respawn** (HP becomes > 0) => **unmute**
- You are **spectating another player** (different SteamID) => **mute**

It can toggle game audio mute in two ways:

- **Voicemeeter API** (recommended) via `voicemeeterlib`
- **Keyboard key presses** (fallback) via `pynput` (you bind keys in CS2)

## Requirements

- Windows
- Python 3.10+ (3.11 also OK)
- CS2 with **Game State Integration** enabled

Python packages:

- `flask`
- `pynput`
- (optional) `voicemeeterlib` if you enable Voicemeeter mode

## Installation

### 1) Clone the repo

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd "cs2 python"
```

### 2) Install dependencies

```bash
pip install flask pynput
```

If you want Voicemeeter control:

```bash
pip install voicemeeterlib
```

## Configuration

Edit `config.json`:

- `key_bindings.mute` / `key_bindings.unmute`
  - Keys that will be pressed if Voicemeeter is disabled.
- `settings.server_host`
  - Usually `127.0.0.1`.
- `settings.server_port`
  - Must match the port you put in the CS2 GSI config.
- `settings.min_switch_delay`
  - Minimum delay between mute/unmute actions (seconds).
- `voicemeeter.enabled`
  - `true` to use Voicemeeter API.
- `voicemeeter.kind`
  - `banana` / `potato` / etc. (depends on your Voicemeeter version).
- `voicemeeter.button_index`
  - Which Voicemeeter macro button to toggle (0 = first button).

## Keyboard mode (CS2 binds)

If `voicemeeter.enabled` is `false`, the script will press `key_bindings.mute` / `key_bindings.unmute` on your keyboard.

- Pick 2 keys you do not use in-game (example: `o` = mute, `p` = unmute).
- Bind them in CS2 to whatever you use to mute/unmute game audio (example: `volume`).

Example (CS2 console):

```cfg
bind o "volume 0"
bind p "volume 0.5"
```

Adjust to your setup (your usual volume level, alias, etc.).

## Voicemeeter mode (macro button)

If `voicemeeter.enabled` is `true`, you must create a **Macro Button** in Voicemeeter and assign it to mute/unmute (or any action you want), then set `voicemeeter.button_index` to that button index.

- Macro Buttons: create a button
- Set it to toggle the mute state you want
- Use `button_index: 0` for the first button, `1` for the second, etc.

Macro example image :

<img width="656" height="830" alt="image" src="https://github.com/user-attachments/assets/37fede72-3b26-405d-a534-e07c5e638bee" />


## CS2 Setup (Game State Integration)

You must create a GSI config file in your CS2 config folder.

1. Go to your CS2 install folder.

Typical Steam path:

```text
C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg\
```

2. Create a file named for example:

```text
gamestate_integration_pythonmute.cfg
```

3. Paste this (adjust the port if you changed it in `config.json`):

```cfg
"CS2 Python Mute"
{
  "uri" "http://127.0.0.1:3000/"
  "timeout" "5.0"
  "buffer" "0.1"
  "throttle" "0.1"
  "heartbeat" "30.0"

  "data"
  {
    "provider"            "1"
    "player_id"           "1"
    "player_state"        "1"
  }
}
```

4. Restart CS2.

## Run

Start the listener:

```bash
python index.py
```

You should see:

- `Starting GSI on port ...`
- Then once you are in a match, CS2 will start sending events.

## Notes / Troubleshooting

- If nothing happens:
  - Make sure the `.cfg` file is in the correct folder.
  - Make sure the `uri` port matches `config.json` (`server_port`).
  - Make sure CS2 is restarted after adding the GSI config.
- If keyboard mute/unmute does nothing:
  - Ensure the keys in `config.json` match your binds (in CS2, Discord, etc.).
  - Run the script as Administrator if your system blocks synthetic keypresses.
- If Voicemeeter does nothing:
  - Set `voicemeeter.enabled` to `true`.
  - Verify `kind` and `button_index`.
  - Make sure Voicemeeter is running.

## Disclaimer

This project is not affiliated with Valve. Use at your own risk.
