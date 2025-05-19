from lcd_api import LcdApi
import time

class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.backlight = 0x08  # Backlight ON
        time.sleep_ms(20)
        self.lcd_init()
        super().__init__(num_lines, num_columns)

    def lcd_init(self):
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x02)
        time.sleep_ms(1)

        self.write_command(0x28)  # Function set: 4-bit, 2 line, 5x8 dots
        self.write_command(0x08)  # Display OFF
        self.write_command(0x01)  # Clear Display
        time.sleep_ms(2)
        self.write_command(0x06)  # Entry mode set
        self.write_command(0x0C)  # Display ON, Cursor OFF, Blink OFF

    def hal_write_init_nibble(self, nibble):
        byte = (nibble << 4) & 0xF0
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.backlight]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | 0x04 | self.backlight]))  # Enable high
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.backlight]))         # Enable low

    def hal_write(self, data):
        self.i2c.writeto(self.i2c_addr, bytearray([data | self.backlight]))
        self.i2c.writeto(self.i2c_addr, bytearray([data | 0x04 | self.backlight]))  # Enable high
        self.i2c.writeto(self.i2c_addr, bytearray([data | self.backlight]))         # Enable low

    def write_command(self, cmd):
        upper = cmd & 0xF0
        lower = (cmd << 4) & 0xF0
        self.hal_write(upper)
        self.hal_write(lower)

    def write_char(self, char_val):
        upper = (char_val & 0xF0) | 0x01  # RS = 1 for data
        lower = ((char_val << 4) & 0xF0) | 0x01
        self.hal_write(upper)
        self.hal_write(lower)

    def backlight_state(self, state):
        if state:
            self.backlight = 0x08
        else:
            self.backlight = 0x00
        self.i2c.writeto(self.i2c_addr, bytearray([self.backlight]))

    def backlight_on(self):
        self.backlight_state(True)

    def backlight_off(self):
        self.backlight_state(False)
