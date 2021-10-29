from network import Network
import pygame, time
import buttons
import random 
from _thread import *



pygame.init()

BASE_FONT = pygame.font.Font("MinecraftRegular-Bmg3.otf", 40)



win = pygame.display.set_mode((450,700))
pygame.display.set_caption("Escape Plan")

run = True
clock = pygame.time.Clock()
game_state = 0
ongoing = False
name_input = ""
players = {}
role = None
tm = False #ค่าที่ใช้ในtimer()
move = False

def timer():
    global t_timer
    t_timer = 10
    while t_timer >= 0 and turn == role:
        if turn != role or game_state != 3:
            break 
        time.sleep(1) 
        t_timer = t_timer-1
        if turn == role and t_timer <=0:
            n.oneway_send('still') #ส่งไปให้server เมื่อเวลาหมด ทำให้ player นั้นเดินไม่ได้
    global tm
    tm = False
    
def main_menu(event): #เอาไว้พิมพ์ชื่อ
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_BACKSPACE:
            global name_input
            name_input = name_input[:-1]
        else:
            name_input += event.unicode

def draw_board(win, board, pos1, pos2, length, padding, color, po_skin, pri_skin): #เอาไว้วาดพื้นหลังและรูปตามตำแหน่งใน board ที่รับมาจาก server
    pygame.draw.rect(win, (11,91,152), pygame.Rect(pos1, pos2, length, length)) #สีและขนาดสีเหลี่ยมสีเข้ม
    rect_size = int((length - (6*padding))/5)
    for y in range(5):
        for x in range(5):
            pos = ((padding*(x+1))+(rect_size*x)+pos1, (padding*(y+1))+(rect_size*y)+pos2)
            if color == 'yellow':
                pygame.draw.rect(win, (255,255,0), [pos[0],pos[1],rect_size,rect_size]) #เปลี่ยนสีบอร์ดตรงนี้
            elif color == 'pink' :
                pygame.draw.rect(win, (254,184,198), [pos[0],pos[1],rect_size,rect_size])
            else:
                pygame.draw.rect(win, (254,255,255), [pos[0],pos[1],rect_size,rect_size])
            if board[x][y] == 1:
                img = pygame.image.load('obs.png').convert_alpha()
            elif board[x][y] == 2:
                if pri_skin == 1:
                    img = pygame.image.load('pirate.png').convert_alpha()
                else:
                    img = pygame.image.load('prisoner.png').convert_alpha()   
            elif board[x][y] == 3:
                if po_skin == 1:
                    img = pygame.image.load('marine.png').convert_alpha()
                else:
                    img = pygame.image.load('police.png').convert_alpha()
            elif board[x][y] == 4:
                img = pygame.image.load('tunnel.png').convert_alpha()
            if board[x][y] != 0: #ขยายรูป
                image = pygame.transform.scale(img,(rect_size, rect_size))
                win.blit(image, pos)


def blit_players(win, players):  #เอาไว้ blit player name กับ player score
    i = 0
    for player in players:
        text = player+" : "+str(players[player])
        global BASE_FONT
        show = BASE_FONT.render(text, 1, (255,0,0))
        win.blit(show, (100, 100+(i*60)))
        i = i+1

start_img = pygame.image.load('start.png').convert_alpha()
start_btn = buttons.Button(124, 450, start_img, 0.3, 'start')
movement_btns = []
img1 = pygame.image.load('reset.png').convert_alpha()
color_btn = buttons.Button(300, 627, img1, 0.05, '')

skin_btn = buttons.Button(360, 627, img1, 0.05, '')

while run:
        clock.tick(60)
        win.fill((202, 228, 241))
        
        if game_state == 0:
            start_btn.draw(win)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if game_state == 0:
                
                main_menu(event) #รัน menu method
                name = BASE_FONT.render(name_input, 1, (255,0,0)) #render nameขณะพิมพ์
                
            if event.type == pygame.MOUSEBUTTONDOWN :
                pos = pygame.mouse.get_pos()
                if game_state == 0:  
                    if start_btn.click(pos): #ถ้ากดปุ่ม start ใน client
                        n = Network(name_input) #เรียกใช้ network ตามชื่อ player
                        players = n.getP() #get name_input มาจาก network
                        if players != None:
                            game_state = 1

                if game_state == 3 and turn == role: #ถ้ากด movement btns ใน state 3
                    for btn in movement_btns:
                        if btn.click(pos):
                            n.oneway_send(btn.text)
                            movement_btns = []
                if game_state == 3:
                    if color_btn.click(pos):
                        n.oneway_send('color')
                    if skin_btn.click(pos):
                        n.oneway_send(role)
                

        if game_state == 0: #หน้าพิมพ์ชื่อ
            win.blit(name, (100,200))

        elif game_state == 1: #หน้า lobby
            try:
                recieved_data = n.send("players") 
                game_state, new_players = recieved_data #game state จะเป็น 2 เมื่อ server กด start และเรารับเข้ามา
                if new_players != players:  
                    players = new_players.copy() 
                    print(players)  
                blit_players(win, players)
            except:
                game_state = 0  #คือไรนะ

        elif game_state == 2: #หน้าบอกrole
            try:
                game_state, role = n.send("role")
                text_role = BASE_FONT.render('You are '+role, 1, (0,0,255))
                win.blit(text_role, (100,320))  #ทั้งหน้ามีแค่ text_role
                pygame.display.update()  
                time.sleep(3)
                game_state = 3
            except:
                game_state = 0

        elif game_state == 3: #หน้าboard
            try:
                for btn in movement_btns: #draw movement btns จากด้านล่างตาม turn
                    btn.draw(win)
                game_state, turn, game = n.send("board") #รับตัวแปรมา
                draw_board(win, game.get_board(), 0, 50, 450, 5, game.c_color, game.po_skin, game.pri_skin)
                
                color_btn.draw(win)
                skin_btn.draw(win)

                if turn == role:
                    if move == False: #move ไว้checkแค่ตรงนี้
                        move = True
                        if tm == False: #tm ไว้checkแค่ตรงนี้
                            start_new_thread(timer, ()) #timer จบจะส่ง still เข้า server
                            tm = True
                        if role == 'prisoner':
                            pos1, pos2 = game.get_pri_pos() #pos1 = x, pos2 = y ของ prisoner
                            if game.check_legit((pos1, pos2-1)): #check legit ของตำแหน่งเดินขึ้น
                                if not game.check_obs((pos1, pos2-1)):
                                    img = pygame.image.load('up.png').convert_alpha()
                                    up_btn = buttons.Button(100, 600, img, 0.05, 'up')
                                    if up_btn not in movement_btns: 
                                        movement_btns.append(up_btn) #ใส่button ไว้ใน list movement_btns

                            if game.check_legit((pos1+1, pos2)):
                                if not game.check_obs((pos1+1, pos2)): 
                                    img = pygame.image.load('right.png').convert_alpha()
                                    right_btn = buttons.Button(127, 627, img, 0.05, 'right')
                                    if right_btn not in movement_btns:
                                        movement_btns.append(right_btn)

                            if game.check_legit((pos1, pos2+1)):
                                if not game.check_obs((pos1, pos2+1)):
                                    img = pygame.image.load('down.png').convert_alpha()
                                    down_btn = buttons.Button(100, 627, img, 0.05, 'down')
                                    if down_btn not in movement_btns:
                                        movement_btns.append(down_btn)

                            if game.check_legit((pos1-1, pos2)):
                                if not game.check_obs((pos1-1, pos2)):
                                    img = pygame.image.load('left.png').convert_alpha()
                                    left_btn = buttons.Button(73, 627, img, 0.05, 'left')
                                    if left_btn not in movement_btns:
                                        movement_btns.append(left_btn)

                        if role == 'police':
                            pos1, pos2 = game.get_po_pos()
                            if game.check_legit((pos1, pos2-1)):
                                if not game.check_obs((pos1, pos2-1)) and not game.check_tunnel((pos1, pos2-1)): #check obs และ tunnel
                                    img = pygame.image.load('up.png').convert_alpha()
                                    up_btn = buttons.Button(100, 600, img, 0.05, 'up')
                                    if up_btn not in movement_btns:
                                        movement_btns.append(up_btn)

                            if game.check_legit((pos1+1, pos2)):
                                if not game.check_obs((pos1+1, pos2)) and not game.check_tunnel((pos1+1, pos2)):
                                    img = pygame.image.load('right.png').convert_alpha()
                                    right_btn = buttons.Button(127, 627, img, 0.05, 'right')
                                    if right_btn not in movement_btns:
                                        movement_btns.append(right_btn)

                            if game.check_legit((pos1, pos2+1)):
                                if not game.check_obs((pos1, pos2+1)) and not game.check_tunnel((pos1, pos2+1)):
                                    img = pygame.image.load('down.png').convert_alpha()
                                    down_btn = buttons.Button(100, 627, img, 0.05, 'down')
                                    if down_btn not in movement_btns:
                                        movement_btns.append(down_btn)

                            if game.check_legit((pos1-1, pos2)):
                                if not game.check_obs((pos1-1, pos2)) and not game.check_tunnel((pos1-1, pos2)):
                                    img = pygame.image.load('left.png').convert_alpha()
                                    left_btn = buttons.Button(73, 627, img, 0.05, 'left')
                                    if left_btn not in movement_btns:
                                        movement_btns.append(left_btn)
                    text_timer = BASE_FONT.render(str(t_timer), 1, (0,0,255)) 
                    win.blit(text_timer, (50,50)) #blit timer บนหน้าจอ
                elif turn != role :
                    movement_btns = []
                    move = False
            except:
                game_state = 0

        
        elif game_state == 4: #เมื่อเจอ winner จาก server
            try:
                move = False
                game_state, winner, game, players = n.send("winner") #รับตัวแปร
                draw_board(win, game.get_board(), 0, 50, 450, 5, game.c_color, game.po_skin, game.pri_skin)
                winner_text = BASE_FONT.render(winner+' wins', 1, (255, 0, 0))
                win.blit(winner_text, (100, 320)) #blit winner
                pygame.display.update()
                time.sleep(1)
                win.fill((202, 228, 241))
                draw_board(win, game.get_board(), 0, 50, 450, 5, game.c_color, game.po_skin, game.pri_skin)
                blit_players(win, players) #blit player กับ score
                pygame.display.update()
                time.sleep(2)
                game_state = 2 #กลับไปหน้าเลือก role
            except:
                game_state = 0
                
        pygame.display.update()