import pygame
import threading
import socket
import random
SIZE = 10
screen_width, screen_height = 900, 600
heightObject, widthObject = 80, 25
xPlayer, yPlayer = 10, screen_height/2
xClient, yClient = screen_width-40, screen_height/2
screen_color, PLayerColor, ClientColor = (0,0,0), (200, 0, 70), (200, 0, 200)
xBall, yBall = screen_width/2 - 10, screen_height/2
FPS = 70
vel, velBall = 5, 5
velServ, velClnt = 5, 5
velBall_list = [velBall, velBall - 2*velBall, velBall - 2*velBall, velBall - 2*velBall]
#############################   NETWORK   ############################################
class Network:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = ("0.0.0.0", 9229)
        self.recv_data = ""
        self.data = ""
        self.join()
    def join(self):
        try:
            self.server.bind(self.address)
            self.server.listen(1)
        except:
            pass
################### PYGAME INITIALIZE  ############################
pygame.init()
window = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ping Pong Server")
clock = pygame.time.Clock()
fnt = pygame.font.SysFont("Arial.tff", 45, False, True)
###############  Server_Player   #############
class Server_player():
    def __init__(self, window):
        global xPlayer, yPlayer
        self.win = window
    def draw(self):
        pygame.draw.rect(self.win, PLayerColor, (xPlayer, yPlayer, widthObject, heightObject))
    def movement(self):
        global xPlayer, yPlayer
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and yPlayer > 10:
            yPlayer-= velServ

        elif keys[pygame.K_DOWN] and yPlayer < screen_height - (heightObject + 10):
            yPlayer+= velServ

#################  BALL   ##########################
class Ball():
    def __init__(self, win, xBall, yBall):
        self.win = win
        global xPlayer, yPlayer, xClient, yClient
        self.xBall = xBall
        self.yBall = yBall
        self.began_motion, self.moveBall = True, False
        self.xBall_random, self.yBall_random = 0, 0
        self.scorePlayer, self.scoreClient = 0, 0
    def draw(self):
        pygame.draw.circle(self.win, (243, 2, 21), (self.xBall, self.yBall), 20)
    def movement(self):
        self.check = True
        if self.check:
            self.first = True
        else:
            self.first = False
        if xPlayer + 40 >= self.xBall and xPlayer + 10 <= self.xBall:
            if self.yBall in range(int(yPlayer - 10), int(yPlayer + 80)):
                self.xBall_random = velBall
        elif xClient - 20 <= self.xBall and xClient - 10 >= self.xBall:
            if self.yBall in range(int(yClient - 10), int(yClient + 90)):

                self.xBall_random = -velBall
        if self.began_motion == True:
            if self.first:
                self.xBall_random = -velBall
                self.yBall_random = velBall
            else:
                self.xBall_random = random.choice(velBall_list)
                self.yBall_random = random.choice(velBall_list)
            self.moveBall = True
            self.check = False

        if self.moveBall == True:
            self.began_motion = False
            if self.yBall < screen_height - 20 and self.yBall > 20:
                self.xBall += self.xBall_random
                self.yBall += self.yBall_random
            else:
                if self.yBall_random < 0:
                    self.yBall_random -= self.yBall_random * 2

                elif self.yBall_random > 0:
                    self.yBall_random -= self.yBall_random * 2

                self.yBall += self.yBall_random
                self.xBall += self.xBall_random
        if self.xBall < -30:
            self.xBall, self.yBall = screen_width / 2 - 10, screen_height / 2
            self.scoreClient += 100
        elif self.xBall > screen_width + 30:
            self.xBall, self.yBall = screen_width / 2 - 10, screen_height / 2
            self.scorePlayer += 100
        pygame.draw.circle(self.win, (243, 2, 21), (self.xBall, self.yBall), 20)

###############   Client Player   ###########
class ClientPlayer():
    def __init__(self, win):
        self.win = win
        global xClient, yClient
    def draw(self):
        pygame.draw.rect(self.win, ClientColor, (xClient, yClient, widthObject, heightObject))
    def movement(self, target):
        global xClient, yClient
        if float(target) > yClient:
            yClient += velClnt
        elif float(target) < yClient:
            yClient -= velClnt

def redraw(win, player, clint, ball, scrPlayer, scrClient):
    win.fill(screen_color)
    pygame.draw.rect(win, (250, 250, 250), (screen_width / 2 - 20, 0, 20, screen_height))
    ball.draw()
    player.draw()
    clint.draw()
    textP = fnt.render("Score: " + str(scrPlayer), True, (200, 0, 70))
    textC = fnt.render("Score: " + str(scrClient), True, (200, 0, 200))
    win.blit(textP, (screen_width / 2 - 250, 18))
    win.blit(textC, (screen_width/2 + 100, 18))

    pygame.display.update()
class send_thread:
    def __init__(self, conn, y):
        data = str(int(y))
        data = f'{len(data):<{SIZE}}' + data
        if len(data) != 0:
            conn.send(bytes(str(data), "utf-8"))

class recv_thread:
    def __init__(self, conn, Clnt, ball):
        self.conn = conn
        self.comp = ""
        new_msg = True
        self.var = "300"
        while True:
            data = self.conn.recv(SIZE + 6)
            if new_msg:
                msglen = int(data[:SIZE])
                new_msg = False
            self.comp += data.decode("utf-8")
            if len(self.comp) - SIZE == msglen:
                if len(self.comp[SIZE:]) != 0:
                    self.var = self.comp[SIZE:]
                Clnt.movement(int(self.var))
                new_msg = True

            ball.movement()


def main():
    running = True

    Serv = Server_player(window)
    Clnt = ClientPlayer(window)
    ball = Ball(window, xBall, yBall)
    global velBall, velClnt, velServ
    n = Network()
    conn, addr = n.server.accept()
    while running:
        clock.tick(FPS)
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                running = False

        if len(str(conn)) !=0:
            threading.Thread(target=send_thread, args=(conn, yPlayer)).start()
            threading.Thread(target=recv_thread, args=(conn, Clnt, ball)).start()

            Serv.movement()


        redraw(window, Serv, Clnt, ball, ball.scorePlayer, ball.scoreClient)



if __name__ == "__main__":
    main()
