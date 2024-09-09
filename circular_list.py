#author: jumail-j
#date : 2024-08-25

class CircularList:
    def __init__ (self, items):
        self.items = items
        self.index = 0

    def next(self):
        current_item = self.items[self.index]
        self.index = (self.index + 1) % len(self.items)
        return current_item

    def current(self):
        return self.items[self.index]

    def reset(self):
        self.index = 0