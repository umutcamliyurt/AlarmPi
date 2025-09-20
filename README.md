# AlarmPi

<!-- DESCRIPTION -->

## A Bluetooth proximity alarm using Raspberry Pi

AlarmPi uses Raspberry Pi to monitor the presence of a paired Bluetooth device, such as a smartphone. When the paired device goes out of range or disconnects, the alarm is triggered using a buzzer. The system automatically tries to reconnect to the trusted device and sends keep-alive pings to maintain a stable connection.

## Use cases

Use AlarmPi to monitor your phone (or another trusted device). If someone steals or moves it out of range, the buzzer sounds immediately. Can be placed in dorms, hotels, or public spaces as a simple security measure.

<!-- REQUIREMENTS -->

## Requirements

### Hardware:

- Raspberry Pi (any model with Bluetooth support, e.g., Pi 3, Pi 4, Pi Zero W)

- Active internet connection (for setup)

- Active buzzer or passive buzzer connected to GPIO17

- Power supply for Raspberry Pi

### Software:

- Raspberry Pi OS (Debian-based, with Bluetooth support)

- Python 3

- Bluetooth stack (bluez tools installed by default on Raspberry Pi OS)

<!-- INSTALLATION -->

## Installation

    sudo apt update
    sudo apt install pulseaudio pulseaudio-module-bluetooth pavucontrol bluetooth bluez bluez-tools python3-gpiozero python3 python3-pip git
    pulseaudio --start
    sudo systemctl restart bluetooth
    git clone https://github.com/umutcamliyurt/AlarmPi.git
    cd AlarmPi/
    pip3 install -r requirements.txt
    sudo python3 AlarmPi.py

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE` for more information.