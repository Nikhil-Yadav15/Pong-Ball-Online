import pygame
import random
import socket
import threading

SIZE = 10
screen_width, screen_height = 900, 600
heightObject, widthObject = 80, 25
xPlayer, yPlayer = 10, screen_height / 2
xClient, yClient = screen_width - 40, screen_height / 2
screen_color, PLayerColor, ClientColor = (0, 0, 0), (200, 0, 70), (200, 0, 200)
xBall, yBall = screen_width / 2 - 10, screen_height / 2
time, dt = 5, 0
FPS = 60
vel, velBall = 5, 5
velClnt, velServ = 5, 5
velBall_list = [velBall, velBall - 2 * velBall, velBall - 2 * velBall, velBall - 2 * velBall]


#############################   NETWORK   ############################################


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recieved = ""
        self.data = ""
        self.addr = ('192.168.1.1', 17780)
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
        except:
            pass


################### PYGAME INITIALIZE  ############################

pygame.init()
global window
window = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ping Pong Client")
global clock
clock = pygame.time.Clock()
fnt = pygame.font.SysFont("Arial.tff", 45, False, True)


###############  Server_Player   #############
class Server_player():
    def __init__(self, window):
        global xPlayer, yPlayer
        self.win = window

    def draw(self):
        pygame.draw.rect(self.win, PLayerColor, (xPlayer, yPlayer, widthObject, heightObject))

    def movement(self, target):
        global xPlayer, yPlayer
        if target > yPlayer:
            yPlayer += velServ
        elif target < yPlayer:
            yPlayer -= velServ


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
            self.check = False
            self.moveBall = True

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
            self.scoreClient += 100
            self.xBall, self.yBall = screen_width / 2 - 10, screen_height / 2
        elif self.xBall > screen_width + 30:
            self.scorePlayer += 100
            self.xBall, self.yBall = screen_width / 2 - 10, screen_height / 2
        pygame.draw.circle(self.win, (243, 2, 21), (self.xBall, self.yBall), 20)


###############   Client Player   ###########
class ClientPlayer():
    def __init__(self, win):
        self.win = win
        global xClient, yClient

    def draw(self):
        pygame.draw.rect(self.win, ClientColor, (xClient, yClient, widthObject, heightObject))

    def movement(self):
        global xClient, yClient
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and yClient > 10:
            yClient -= velClnt
        elif keys[pygame.K_DOWN] and yClient < screen_height - (heightObject + 10):
            yClient += velClnt


def redraw(win, player, clint, ball, scrPlayer, scrClient):
    win.fill(screen_color)
    pygame.draw.rect(win, (250, 250, 250), (screen_width / 2 - 20, 0, 20, screen_height))
    ball.draw()
    player.draw()
    clint.draw()
    textP = fnt.render("Score: " + str(scrPlayer), True, (200, 0, 70))
    textC = fnt.render("Score: " + str(scrClient), True, (200, 0, 200))
    win.blit(textP, (screen_width / 2 - 250, 18))
    win.blit(textC, (screen_width / 2 + 100, 18))
    pygame.display.update()


class recv_thread:
    def __init__(self, client, Serv, ball):
        self.client = client
        self.comp = ""
        self.var = "300"
        new_msg = True
        while True:
            data = self.client.recv(SIZE + 6)

            if new_msg:
                msglen = int(data[:SIZE])
                new_msg = False
            self.comp += data.decode("utf-8")
            if len(self.comp) - SIZE == msglen:
                if len(self.comp[SIZE:]) != 0:
                    self.var = self.comp[SIZE:]
                Serv.movement(int(self.var))

                new_msg = True

            ball.movement()


#############################################################
class send_thread:
    def __init__(self, clnt, y):
        self.clnt = clnt
        data = str(int(y))
        data = f'{len(data):<{SIZE}}' + data
        self.clnt.send(bytes(str(data), "utf-8"))


############################################################
def main():
    running = True
    Serv = Server_player(window)
    Clnt = ClientPlayer(window)
    ball = Ball(window, xBall, yBall)
    n = Network()
    global velBall, velClnt, velServ
    while running:
        clock.tick(FPS)
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                running = False
        threading.Thread(target=recv_thread, args=(n.client, Serv, ball)).start()

        threading.Thread(target=send_thread, args=(n.client, yClient)).start()

        Clnt.movement()

        # if ball.scorePlayer% 400 or ball.scoreClient% 400 == 0:
        #     velBall += 1

        redraw(window, Serv, Clnt, ball, ball.scorePlayer, ball.scoreClient)


if __name__ == "__main__":
    main()
