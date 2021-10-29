import socket
import pickle
from _thread import *
import pygame, os
import buttons
import random 
import Game 
import time


SERVER = "192.168.1.105"
PORT = 5050


#0-accepting connection, 2-game start, (1 for client waiting room), 3-game-ongoing
game_state = 1
ongoing = False


#current prisoner and police
current_T = None
current_P = None

turn = 'police'  #กำหนด turn แรกให้เป็นของ Police

game = Game.Game()

def blit_players(win, players, base_font):
    i = 0
    for player in players:
        text = player+" : "+str(players[player])
        show = base_font.render(text, 1, (255,0,0))
        win.blit(show, (100, 350+(i*60)))
        i = i+1

def timer(): 
    time.sleep(3)
    global game_state
    game_state = 3

def timer_two(): 
    time.sleep(1)
    new_game()
    
def new_game(): 
    global turn
    turn = 'police'
    global game_state
    game_state = 2
    start_new_thread(timer, ())
    random_TP(players, False)
    global game
    game.make_zeros()
    game.random_board()

def second_state():
    global turn
    turn = 'police'
    global game_state
    game_state = 2
    start_new_thread(timer, ()) #ทำอะไร
    random_TP(players, True)
    global game
    game.make_zeros()
    game.random_board() 

def random_TP(players, new_game): 
    global current_P, current_T
    if new_game:
        current_T = random.choice(list(players.keys()))
        while current_P == None or current_P == current_T:
            current_P = random.choice(list(players.keys()))
    else: 
        global winner
        current_P = winner
        current_T = random.choice(list(players.keys()))
        while current_T == current_P:
            current_T = random.choice(list(players.keys()))

def server_interface():
    pygame.init()
    BASE_FONT = pygame.font.Font("MinecraftRegular-Bmg3.otf", 40)
    win = pygame.display.set_mode((300,500))
    pygame.display.set_caption("Server")
    clock = pygame.time.Clock()

    start_img = pygame.image.load('start.png').convert_alpha()
    start_btn = buttons.Button(65,100,start_img,0.25, 'start')

    reset_img = pygame.image.load('reset.png').convert_alpha()
    reset_btn = buttons.Button(100,200,reset_img,0.1, 'reset')

    while True: #คลิก reset -> gamestate = 1, start -> gamestate = 2 , render player name on server ui
        global game_state
        clock.tick(60)
        win.fill((255,255,255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                os._exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN :
                pos = pygame.mouse.get_pos()
                if game_state != 2:
                    if start_btn.click(pos) and len(players.keys())>= 2:
                        second_state() #รัน method
                    if reset_btn.click(pos):
                        game_state = 1
                        for player in players:
                            players[player] = 0 #ใส่ลิสplayersด้วย 0
                    

        blit_players(win, players, BASE_FONT)
        start_btn.draw(win)
        reset_btn.draw(win)
        pygame.display.update()

start_new_thread(server_interface, ()) #รันไอนี้ตลอดเวลาที่serverรัน

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((SERVER, PORT))
except socket.error as e:
    str(e)



print("Waiting for a connection, Server Started")

players = {}
winner = None

s.listen()

def threaded_client(conn, addr):
    global game_state
    name = conn.recv(4096).decode() #receive มาจาก network
    if name in players:
        print("Duplicate Names.")
        conn.close()
    players[name]=0 #ใส่scoreตามชื่อให้เป็น 0
    print("Welcome, ", name, addr)
    conn.sendall(pickle.dumps(players)) #ถ้าไม่มี Client กด Start ไม่ได้
    while True:
        try:
            global winner
            data = conn.recv(4096).decode()
            if not data:
                break
            else:
                

                if data == "players":
                    conn.sendall(pickle.dumps((game_state, players)))
                elif data == "role":
                    if current_P == name:
                        conn.sendall(pickle.dumps((game_state,'police')))
                    elif current_T == name:
                        conn.sendall(pickle.dumps((game_state,'prisoner')))
                    else:
                        conn.sendall(pickle.dumps((game_state,'spectator')))
                elif data == "board":
                    global game, turn
                    conn.sendall(pickle.dumps((game_state, turn, game)))
                elif data == "winner":
                    conn.sendall(pickle.dumps((game_state, winner, game, players)))
                elif data == "color":
                    game.change_color()
                elif data == "police":
                    game.poskin()
                elif data == "prisoner":
                    game.priskin()

                else: #รับ movement btns text มาจาก client
                    old_po = game.get_po_pos()
                    old_pr = game.get_pri_pos()
                    tun = game.get_tun_pos()


                    if name == current_P:
                        if data == "up":
                            po = (old_po[0], old_po[1]-1)
                        elif data ==  "right":
                            po = (old_po[0]+1, old_po[1])
                        elif data == "down":
                            po = (old_po[0], old_po[1]+1)
                        elif data == "left":
                            po = (old_po[0]-1, old_po[1])
                        else: 
                            po = (old_po[0],old_po[1])
                        pr = old_pr #กำหนด pos ใหม่
                        
                    else:
                        if data == "up":
                            pr = (old_pr[0], old_pr[1]-1)
                        elif data == "right":
                            pr = (old_pr[0]+1, old_pr[1])
                        elif data == "down":
                            pr = (old_pr[0], old_pr[1]+1)
                        elif data == "left":
                            pr = (old_pr[0]-1, old_pr[1])
                        else:
                            pr = (old_pr[0],old_pr[1])
                        po = old_po #กำหนด pos ใหม่
                    
                    if po == pr or pr == tun: #check winner ก่อน move , ถ้ามี winner ก็ state 4 เลยไม่ต้อง move แล้ว
                        if po == pr: #ตำรวจจับโจรได้
                            players[current_P] = players[current_P] + 1 #คะแนน?
                            winner = current_P
                            game_state = 4
                            start_new_thread(timer_two, ())
                        else: #โจรเข้าtunnelได้
                            players[current_T] = players[current_T] + 1 #คะแนน?
                            winner = current_T
                            game_state = 4
                            start_new_thread(timer_two, ())
                    else:
                        if name == current_P and data != "still": #ถ้ายังไม่หมดเวลา
                            game.move(old_po[0], old_po[1], po[0], po[1])
                        elif name == current_T and data != "still": #ถ้ายังไม่หมดเวลา
                            game.move(old_pr[0], old_pr[1], pr[0], pr[1])
                                
                        if turn =='police': # move แล้วเปลี่ยน turn
                            turn = 'prisoner'
                        else:
                            turn = 'police'
                        
        except:
            break

    print("Lost connection, ", name, addr)
    if name == current_P or name == current_T: #ใครออกให้เปลี่ยน state เป็น 1
        game_state = 1
    players.pop(name, None)
    conn.close()

    
while True:
    conn, addr = s.accept()
    start_new_thread(threaded_client, (conn, addr))


    


        