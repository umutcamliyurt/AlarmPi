import argparse
import subprocess
import time
import os
import re
from gpiozero import Buzzer

CHECK_INTERVAL = 5
RECONNECT_INTERVAL = 3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAC_FILE = os.path.join(SCRIPT_DIR, "bluetooth_mac.txt")

parser = argparse.ArgumentParser(description="Buzzer or dry-fire mode")
parser.add_argument(
    "--dry-fire",
    action="store_true",
    help="Run without buzzer hardware (print messages instead).",
)
args = parser.parse_args()
DRY_FIRE = args.dry_fire

buzzer = None

def buzzer_on():
    global buzzer
    if DRY_FIRE:
        print("[DRY FIRE MODE] Buzzer ON")
    else:
        if buzzer is None:
            buzzer = Buzzer(17)  
        buzzer.off()

def buzzer_off():
    global buzzer
    if DRY_FIRE:
        print("[DRY FIRE MODE] Buzzer OFF")
    else:
        if buzzer is not None:
            buzzer.on()
            buzzer.close()  
            buzzer = None

def run_btctl_commands(commands):
    try:
        bt_input = "\n".join(commands) + "\n"
        subprocess.run(["bluetoothctl"], input=bt_input, text=True, capture_output=True)
    except Exception as e:
        print("Bluetoothctl error:", e)

def start_bt_agent():
    try:
        print("Starting Bluetooth agent...")
        subprocess.Popen(
            ["sudo", "bt-agent", "-c", "NoInputNoOutput"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print("Error starting bt-agent:", e)

def start_advertising():
    print("Starting Bluetooth advertising...")
    commands = [
        "power on",
        "discoverable on",
        "pairable on",
        "advertise on",
        "system-alias AlarmPi",
    ]
    run_btctl_commands(commands)

def is_connected(mac):
    try:
        result = subprocess.run(["hcitool", "con"], capture_output=True, text=True)
        return mac in result.stdout
    except Exception as e:
        print("Error checking connection:", e)
        return False

def reconnect(mac):
    try:
        print(f"Attempting to reconnect to {mac}...")
        subprocess.run(["bluetoothctl", "connect", mac], capture_output=True, text=True)
    except Exception as e:
        print("Reconnect error:", e)

def clear_bluetooth():
    print("Clearing all previous Bluetooth pairings...")
    try:
        result = subprocess.run(
            ["bluetoothctl", "paired-devices"], capture_output=True, text=True
        )
        paired = re.findall(r"([0-9A-F:]{17})", result.stdout, re.I)
        for mac in paired:
            subprocess.run(
                ["bluetoothctl", "remove", mac], capture_output=True, text=True
            )
            print(f"Removed paired device: {mac}")
    except Exception as e:
        print("Error clearing Bluetooth:", e)

def get_first_connection():
    print("Waiting for first Bluetooth device to connect...")
    while True:
        result = subprocess.run(["hcitool", "con"], capture_output=True, text=True)
        matches = re.findall(r"([0-9A-F:]{17})", result.stdout, re.I)
        if matches:
            return matches[0]
        time.sleep(2)

def load_or_get_mac():
    if os.path.exists(MAC_FILE):
        with open(MAC_FILE, "r") as f:
            mac = f.read().strip()
            if mac:
                print(f"Loaded stored MAC: {mac}")
                return mac

    mac = get_first_connection()
    print(f"New device connected, storing MAC: {mac}")
    with open(MAC_FILE, "w") as f:
        f.write(mac)
    return mac

def keep_alive(mac):
    try:
        subprocess.run(["l2ping", "-c", "1", mac], capture_output=True, text=True)
        print(f"Keep-alive ping sent to {mac}")
    except Exception as e:
        print("Keep-alive error:", e)

start_bt_agent()
start_advertising()

stored_mac = None
if os.path.exists(MAC_FILE):
    with open(MAC_FILE, "r") as f:
        stored_mac = f.read().strip()

clear_bluetooth()

if stored_mac:
    run_btctl_commands([f"trust {stored_mac}"])
    PHONE_MAC = stored_mac
else:
    PHONE_MAC = load_or_get_mac()

print("Bluetooth alarm started. Monitoring connection to", PHONE_MAC)

while True:
    if is_connected(PHONE_MAC):
        buzzer_off()
        print("Phone connected, buzzer off")
        keep_alive(PHONE_MAC)
    else:
        buzzer_on()
        print("Phone disconnected! Buzzer ON")
        reconnect(PHONE_MAC)
        retry = 0
        while not is_connected(PHONE_MAC) and retry < 5:
            time.sleep(RECONNECT_INTERVAL)
            reconnect(PHONE_MAC)
            retry += 1
    time.sleep(CHECK_INTERVAL)