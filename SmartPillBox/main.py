import network
import urequests
import time
from machine import Pin, I2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

# Wi-Fi credentials
SSID = 'YOUR_WIFI_NAME'
PASSWORD = 'WIFI_PASSWORD'

# Telegram bot credentials
BOT_TOKEN = 'BOT_TOKEN'
CHAT_ID = 'CHAT_ID'

# Medicines and schedules
medicines = [
    {"name": "Salospir", "hour": 20, "minute":46, "led": Pin(19, Pin.OUT)}, 
    {"name": "Diamicron", "hour": 20, "minute": 24, "led": Pin(18, Pin.OUT)},
    {"name": "Concor", "hour": 20, "minute": 26, "led": Pin(32, Pin.OUT)} 
]

# Buzzer setup
buzzer = Pin(23, Pin.OUT)

# Button Pin
button = Pin(25, Pin.IN)

# I2C & LCD setup
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
lcd_addresses = i2c.scan()
if not lcd_addresses:
    raise Exception("No I2C LCD found!")
lcd = I2cLcd(i2c, lcd_addresses[0], 2, 16)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print('Connected to WiFi:', wlan.ifconfig())

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        response = urequests.get(url)
        print("Message sent:", response.text)
    except Exception as e:
        print("Failed to send message:", e)

def alert_medicine(name, led):
    print(f"Triggered for {name}!")

    lcd.backlight_on()
    lcd.clear()
    time.sleep_ms(5) 
    lcd.home()
    time.sleep_ms(5) 

    lcd.putstr(f"Take: {name}")

    end_time = time.time() + 50
    dismissed = False

    while time.time() < end_time:
        if button.value() == 1:
            print("Alarm dismissed by button.")
            dismissed = True
            lcd.clear()
            lcd.backlight_off()
            break

        for _ in range(3):
            buzzer.value(1)
            led.value(1)
            time.sleep(0.3)
            buzzer.value(0)
            led.value(0)
            time.sleep(0.3)

            if button.value() == 1:
                print("Alarm dismissed by button during beep.")
                dismissed = True
                lcd.clear()
                lcd.backlight_off()
                break

        if dismissed:
            break

        time.sleep(2)

    if not dismissed:
        send_telegram_message(f"It's time to take {name}!")
    else:
        send_telegram_message(f"{name} alarm dismissed manually.")

    time.sleep(2)
    lcd.clear()
    time.sleep_ms(5)
    lcd.putstr("Waiting...")

triggered_today = set()

connect_wifi()
lcd.putstr("Waiting...")

while True:
    now = time.localtime()
    current_hour = now[3]
    current_minute = now[4]
    current_day = now[2]

    for med in medicines:
        trigger_key = f"{med['name']}_{current_day}"
        if (
            current_hour == med["hour"]
            and current_minute == med["minute"]
            and trigger_key not in triggered_today
        ):
            alert_medicine(med["name"], med["led"])
            triggered_today.add(trigger_key)

    time.sleep(1)