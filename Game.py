import numpy as np
import random


class Game:

    def __init__(self):
        #0-empty space, 1-obs, 2-prisoner, 3-police, 4-tunnel
        self.board = np.zeros((5,5), dtype=int)
        self.po_pos = None
        self.pri_pos = None
        self.colors = ['white','yellow','pink']
        self.c_color = 'white'
        self.po_skin = 0
        self.pri_skin = 0

    def make_zeros(self):
        self.board = np.zeros((5,5), dtype=int)

    def random_pos(self):
        x = random.randrange(0,5)
        y = random.randrange(0,5)
        return (x,y)
    
    def get_board(self):
        return self.board

    def random_board(self): 
        #random_ob
        for j in range(5):
            x, y = self.random_pos()
            while self.board[x][y] != 0:
                x, y = self.random_pos()
            self.board[x][y] = 1

        #random theif, police, tunnel positions
        for i in range(3):
            x, y = self.random_pos()
            while self.board[x][y] != 0:
                x, y = self.random_pos()
            self.board[x][y] = i+2
    
    def decode_where(self, a):
        x, y = np.where(self.board == a) #method จากnumpy
        return (int(x),int(y))

    def get_pri_pos(self):
        self.pri_pos = self.decode_where(2)
        return self.pri_pos
    
    def get_po_pos(self):
        self.po_pos = self.decode_where(3)
        return self.po_pos

    def get_tun_pos(self):
        self.tun_pos = self.decode_where(4)
        return self.tun_pos

    def move(self, x, y, x2, y2):
        self.board[x2][y2] = self.board[x][y]
        self.board[x][y] = 0
        
    def set(self, x, y, c):
        self.board[x][y] = c

    def set_color(self, value):
        self.c_color = value
    
    def change_color(self):
        if (self.colors.index(self.c_color)+1) >= len(self.colors):
            self.c_color = self.colors[0]
        else:
            self.c_color = self.colors[self.colors.index(self.c_color)+1]

    def set_poskin(self, value):
        self.po_skin = value
    
    def get_poskin(self):
        return self.po_skin
    
    def set_priskin(self, value):
        self.pri_skin = value

    def get_priskin(self):
        return self.pri_skin
    
    def poskin(self):
        if self.po_skin == 1:
            self.po_skin = 0
        else:
            self.po_skin = self.po_skin+1

    def priskin(self):
        if self.pri_skin == 1:
            self.pri_skin = 0
        else:
            self.pri_skin = self.pri_skin+1

    def check_legit(self, pos): #check ว่าอยู่ในตารางมั้ย
        if 0 <= pos[0] <=4 and 0 <= pos[1] <=4:
            return True
        else:
            return False
    
    def check_obs(self, pos):
        if self.board[pos] == 1:
            return True
        else:
            return False
    
    def check_tunnel(self, pos):
        if self.board[pos] == 4:
            return True
        else:
            return False


