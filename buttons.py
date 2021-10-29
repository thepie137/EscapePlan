import pygame

class Button: #วาดFigureทีuploadเข้ามาตามpositionที่ใส่เข้ามา
    def __init__(self, x, y, image, scale, text):
        self.text = text
        self.width = int(image.get_width() * scale)
        self.height = int(image.get_height() * scale)
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.rect = self.image.get_rect()

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False
