import time

class LcdApi:
    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0

    def clear(self):
        self.move_to(0, 0)
        self.putstr(" " * (self.num_lines * self.num_columns))
        self.move_to(0, 0)

    def move_to(self, col, row):
        self.cursor_x = col
        self.cursor_y = row

    def putchar(self, char):
        raise NotImplementedError

    def putstr(self, string):
        for char in string:
            self.putchar(char)
