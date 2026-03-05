from networking.client import Client
from networking.server import Server
from networking.message import Message

import time
import tkinter as tk
import random

WINDOWSIZE = 800 # px

FRAMEDELTATIME = 10 # ms (100fps)

PLAYERHEIGHT = 0.16 # screens
PLAYERWIDTH = 0.03 # screens
PLAYERVELOCITY = 0.6 # screens/s
AIVELOCITY = 0.4 # screens/s

BALLRADIUS = 0.02 # screens

LINEWIDTH = 0.005 # screens

window = tk.Tk()
canvas = tk.Canvas(
    window,
    width = WINDOWSIZE,
    height = WINDOWSIZE,
    background = "black"
)
canvas.pack()

isHost : bool
useAI : bool

def IsValidPort(port : str) -> bool:
    try:
        if int(port[1]) < 0 or int(port[1]) > 65535:
            return False
    except:
        return False

    return True

def IsValidAddress(address : str) -> bool:
    ip_port = address.split(":")
    if len(ip_port) not in [2, 3]:
        return False
    
    ipBytes = ip_port[0].split(".")
    if ipBytes != "localhost":
        if len(ipBytes) != 4:
            return False
        for i in ipBytes:
            try:
                if int(i) < 0 or int(i) > 255:
                    return False
            except:
                return False

    if not IsValidPort(ip_port[1]):
        return False
    if len(ip_port) == 3:
        if not IsValidPort(ip_port[2]):
            return False
    
    return True

def Menu():
    KEYS : dict[str, str]

    def OnClick(event):
        nonlocal KEYS, inputHelperText
        global isHost, useAI
        window.unbind("<Button-1>")
        isHost = event.y < WINDOWSIZE / 2
        useAI = (event.x > WINDOWSIZE / 2) and not isHost
        for element in menuElements:
            canvas.delete(element)
        window.bind("<KeyPress>", TypeChar)
        if isHost:
            KEYS = {"0" : "0", "1" : "1", "2" : "2", "3" : "3", "4" : "4", "5" : "5", "6" : "6", "7" : "7", "8" : "8", "9" : "9"}
            inputHelperText = canvas.create_text(
                WINDOWSIZE / 2,
                WINDOWSIZE / 2 - 20,
                fill = "white",
                text = "Port:",
                font = ("Arial", 25, "bold")
            )
        else:
            KEYS = {"0" : "0", "1" : "1", "2" : "2", "3" : "3", "4" : "4", "5" : "5", "6" : "6", "7" : "7", "8" : "8", "9" : "9", "period" : ".", "colon" : ":"}
            inputHelperText = canvas.create_text(
                WINDOWSIZE / 2,
                WINDOWSIZE / 2 - 20,
                fill = "white",
                text = "Host Address (Ip:ServerPort:ClientPort):",
                font = ("Arial", 25, "bold")
            )

    def TypeChar(event):
        currentText = canvas.itemcget(textField, "text")

        if event.keysym == "Return":
            if isHost:
                if IsValidPort(currentText):
                    window.unbind("<KeyPress>")
                    canvas.delete(inputHelperText)
                    canvas.delete(textField)
                    StartHost(int(currentText))
            else:
                if IsValidAddress(currentText):
                    window.unbind("<KeyPress>")
                    canvas.delete(inputHelperText)
                    canvas.delete(textField)
                    StartClient(currentText)

        if event.keysym == "BackSpace":
            if len(currentText) > 0:
                currentText = currentText[:-1]
        elif event.keysym in KEYS.keys():
            currentText += KEYS[event.keysym]
        canvas.itemconfig(textField, text = currentText)

    menuElements = [
        canvas.create_text(
            WINDOWSIZE / 2,
            WINDOWSIZE / 4,
            fill = "white",
            text = "Host",
            font = ("Arial", 30, "bold")
        ),
        canvas.create_text(
            WINDOWSIZE / 4,
            WINDOWSIZE / 4 * 3,
            fill = "white",
            text = "Client",
            font = ("Arial", 30, "bold")
        ),
        canvas.create_text(
            WINDOWSIZE / 4 * 3,
            WINDOWSIZE / 4 * 3,
            fill = "white",
            text = "AI",
            font = ("Arial", 30, "bold")
        ),
        canvas.create_line(
            0,
            WINDOWSIZE / 2,
            WINDOWSIZE,
            WINDOWSIZE / 2,
            fill = "#D0D0D0",
            width = 2
        ),
        canvas.create_line(
            WINDOWSIZE / 2,
            WINDOWSIZE / 2,
            WINDOWSIZE / 2,
            WINDOWSIZE,
            fill = "#D0D0D0",
            width = 2
        )
    ]
    textField = canvas.create_text(
        WINDOWSIZE / 2,
        WINDOWSIZE / 2 + 20,
        fill = "white",
        text = "",
        font = ("Arial", 25, "bold")
    )
    inputHelperText : any

    window.bind("<Button-1>", OnClick)

class Vector:
    def __init__(self, x : float, y : float):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)

class Player:
    def __init__(self, pos):
        self.pos = pos
        self.graphics = canvas.create_rectangle(
            (pos.x - PLAYERWIDTH / 2) * WINDOWSIZE,
            (pos.y - PLAYERHEIGHT / 2) * WINDOWSIZE,
            (pos.x + PLAYERWIDTH / 2) * WINDOWSIZE,
            (pos.y + PLAYERHEIGHT / 2) * WINDOWSIZE,
            fill = "white",
            outline = "white"
        )
        self.yVelocity : float = 0
        self.pressingUp : bool = False
        self.pressingDown : bool = False

    def UpPress(self, event):
        self.pressingUp = True
        self.UpdateVelocity()
    def UpRelease(self, event):
        self.pressingUp = False
        self.UpdateVelocity()
    def DownPress(self, event):
        self.pressingDown = True
        self.UpdateVelocity()
    def DownRelease(self, event):
        self.pressingDown = False
        self.UpdateVelocity()

    def BindAll(self):
        if not useAI:
            window.bind("<KeyPress-Up>", self.UpPress)
            window.bind("<KeyRelease-Up>", self.UpRelease)
            window.bind("<KeyPress-Down>", self.DownPress)
            window.bind("<KeyRelease-Down>", self.DownRelease)

    def UnbindAll(self):
        if not useAI:
            window.unbind("<KeyPress-Up>")
            window.unbind("<KeyRelease-Up>")
            window.unbind("<KeyPress-Down>")
            window.unbind("<KeyRelease-Down>")
    
    def UpdateVelocity(self):
        self.yVelocity = 0
        velocity = AIVELOCITY if useAI else PLAYERVELOCITY
        if self.pressingUp:
            self.yVelocity -= velocity
        if self.pressingDown:
            self.yVelocity += velocity

    def MoveTo(self, newPos : Vector):
        self.pos = newPos
        canvas.moveto(
            self.graphics,
            round((newPos.x - PLAYERWIDTH / 2) * WINDOWSIZE),
            round((newPos.y - PLAYERHEIGHT / 2) * WINDOWSIZE)
        )
    
    def Destroy(self):
        canvas.delete(self.graphics)

class Ball:
    def __init__(self):
        self.pos = Vector(0.5, 0.5)
        self.graphics = canvas.create_oval(
            (self.pos.x - BALLRADIUS) * WINDOWSIZE,
            (self.pos.y - BALLRADIUS) * WINDOWSIZE,
            (self.pos.x + BALLRADIUS) * WINDOWSIZE,
            (self.pos.y + BALLRADIUS) * WINDOWSIZE,
            fill = "white",
            outline = "white"
        )
        self.velocity = Vector(1, 0)
        if(isHost):
            self.velocity = Vector(-1, 0)
        self.ownedByHost = True
    def MoveTo(self, newPos : Vector):
        self.pos = newPos
        canvas.moveto(
            self.graphics,
            round((newPos.x - BALLRADIUS) * WINDOWSIZE),
            round((newPos.y - BALLRADIUS) * WINDOWSIZE)
        )
        
    def Destroy(self):
        canvas.delete(self.graphics)

def DrawMiddleLine():
    canvas.create_line(
        WINDOWSIZE * 0.5,
        0,
        WINDOWSIZE * 0.5,
        WINDOWSIZE,
        fill = "white",
        dash = (1, 10),
        width = WINDOWSIZE * LINEWIDTH
    )

def IncrementCounter(textID):
    currentScore = int(canvas.itemcget(textID, "text"))
    canvas.itemconfig(
        textID,
        text = str(currentScore + 1)
    )

def StartHost(port : int):
    messageBox = canvas.create_text(
        WINDOWSIZE / 2,
        40,
        fill = "white",
        text = "",
        font = ("Arial", 20, "bold")
    )
    def SetMessageBoxText(text : str):
        canvas.itemconfig(messageBox, text = text)
    
    hostWinCounter = canvas.create_text(
        WINDOWSIZE / 4,
        80,
        fill = "white",
        text = "0",
        font = ("Arial", 40, "bold")
    )
    clientWinCounter = canvas.create_text(
        WINDOWSIZE / 4 * 3,
        80,
        fill = "white",
        text = "0",
        font = ("Arial", 40, "bold")
    )

    gameStarted = False
    gameOver = False
    def ClientReady(clientID : int, message : Message):
        nonlocal gameStarted
        gameStarted = True
        SetMessageBoxText("")
    def MovePlayerClientTo(clientID : int, message : Message):
        if playerClient:
            playerClient.MoveTo(Vector(playerClient.pos.x, message.GetFloat()))
    def TransferBallOwnership(clientID : int, message : Message):
        ball.ownedByHost = True
        ball.velocity = Vector(-1, message.GetFloat())
        ball.MoveTo(Vector(1 - message.GetFloat(), message.GetFloat()))
    def ClientLost(clientID : int, message : Message):
        GameOver(True)

    def GameOver(hostWon : bool):
        playerHost.UnbindAll()
        nonlocal gameOver
        gameOver = True
        if hostWon:
            SetMessageBoxText(f"Game over!\nThe host won!")
            IncrementCounter(hostWinCounter)
        else:
            SetMessageBoxText(f"Game over!\nThe client won!")
            IncrementCounter(clientWinCounter)

    def OnClientConnected(client : Client):
        nonlocal playerClient
        playerClient = Player(Vector(0.9, 0.5))
        SetMessageBoxText("Waiting for the other play to start the game...")

    server : Server = Server(port, 1)
    server.RegisterMessageID(0, ClientReady)
    server.RegisterMessageID(1, MovePlayerClientTo)
    server.RegisterMessageID(3, TransferBallOwnership)
    server.RegisterMessageID(4, ClientLost)
    server.onClientJoin = OnClientConnected

    playerHost : Player = Player(Vector(0.1, 0.5))
    playerClient : None | Player = None
    ball : Ball = Ball()
    DrawMiddleLine()

    playerHost.BindAll()

    def Update():
        nonlocal lastFrame, nextFrame
        deltaTime = time.time() - lastFrame
        lastFrame = time.time()

        newPlayerPos = playerHost.pos + Vector(0, playerHost.yVelocity * deltaTime)
        newPlayerPos.y = min(1 - PLAYERHEIGHT / 2, max(PLAYERHEIGHT / 2, newPlayerPos.y))
        playerHost.MoveTo(newPlayerPos)

        msg = Message(id = 1)
        msg.AddFloat(playerHost.pos.y)
        server.SendToAll(msg)

        if gameStarted:
            newPos = ball.pos + ball.velocity * deltaTime
            
            if newPos.y - BALLRADIUS <= 0:
                ball.velocity.y = abs(ball.velocity.y)
            elif newPos.y + BALLRADIUS >= 1:
                ball.velocity.y = -abs(ball.velocity.y)
            
            ball.MoveTo(newPos)

            if ball.ownedByHost:
                if (playerHost.pos.x + PLAYERWIDTH / 2 >= ball.pos.x - BALLRADIUS and
                   ball.pos.x >= playerHost.pos.x and
                   abs(playerHost.pos.y - ball.pos.y) <= PLAYERHEIGHT / 2
                ):
                    ball.velocity = Vector(1, random.uniform(-0.5, 0.5))
                    msg = Message(id = 3)
                    msg.AddFloat(ball.velocity.y)
                    msg.AddFloat(ball.pos.x)
                    msg.AddFloat(ball.pos.y)
                    server.SendToAll(msg)
                    ball.ownedByHost = False
                
                elif ball.pos.x <= 0:
                    GameOver(False)
                    server.SendToAll(Message(id = 4))

        server.Update()

        if gameOver:
            KeepConnectionAlive()
            window.after(3000, Restart)
            return

        nextFrame += FRAMEDELTATIME / 1000
        timeUntilNextFrame = nextFrame - time.time()
        if timeUntilNextFrame < 0:
            timeUntilNextFrame = 0
        window.after(
            round(timeUntilNextFrame * 1000),
            Update
        )

    SetMessageBoxText("Waiting for a player to connect...")

    def KeepConnectionAlive():
        if gameOver:
            server.Update()
            window.after(FRAMEDELTATIME, KeepConnectionAlive)

    def Restart():
        nonlocal gameOver, lastFrame, nextFrame, playerHost, playerClient, ball

        gameOver = False
        lastFrame = time.time()
        nextFrame = time.time() + FRAMEDELTATIME / 1000
        window.after(FRAMEDELTATIME, Update)

        playerHost.Destroy()
        playerHost = Player(Vector(0.1, 0.5))
        playerHost.BindAll()
        playerClient.Destroy()
        playerClient = Player(Vector(0.9, 0.5))
        ball.Destroy()
        ball = Ball()

        SetMessageBoxText("")

    lastFrame = time.time()
    nextFrame = time.time() + FRAMEDELTATIME / 1000
    window.after(FRAMEDELTATIME, Update)

def StartClient(address : str):
    messageBox = canvas.create_text(
        WINDOWSIZE / 2,
        40,
        fill = "white",
        text = "",
        font = ("Arial", 20, "bold")
    )
    def SetMessageBoxText(text : str):
        canvas.itemconfig(messageBox, text = text)
        
    hostWinCounter = canvas.create_text(
        WINDOWSIZE / 4 * 3,
        80,
        fill = "white",
        text = "0",
        font = ("Arial", 40, "bold")
    )
    clientWinCounter = canvas.create_text(
        WINDOWSIZE / 4,
        80,
        fill = "white",
        text = "0",
        font = ("Arial", 40, "bold")
    )

    gameStarted = False
    gameOver = False
    def MovePlayerHostTo(message : Message):
        playerHost.MoveTo(Vector(playerHost.pos.x, message.GetFloat()))
    def TransferBallOwnership(message : Message):
        ball.ownedByHost = False
        ball.velocity = Vector(-1, message.GetFloat())
        ball.MoveTo(Vector(1 - message.GetFloat(), message.GetFloat()))
    def HostLost(message : Message):
        GameOver(False)

    def GameOver(hostWon : bool):
        playerClient.UnbindAll()
        nonlocal gameOver
        gameOver = True
        if hostWon:
            SetMessageBoxText(f"Game over!\nThe host won!")
            IncrementCounter(hostWinCounter)
        else:
            SetMessageBoxText(f"Game over!\nThe client won!")
            IncrementCounter(clientWinCounter)
    
    def OnConnected():
        SetMessageBoxText("Press Enter to start the game")
        window.bind("<Return>", Ready)
    def OnDisconnected():
        if not gameOver:
            SetMessageBoxText(f"Lost connection to host")

    SetMessageBoxText("Connecting to host...")
    temp = address.split(":")
    client : Client = Client(temp[0], int(temp[1]), int(temp[2]))
    client.RegisterMessageID(1, MovePlayerHostTo)
    client.RegisterMessageID(3, TransferBallOwnership)
    client.RegisterMessageID(4, HostLost)
    client.onJoin = OnConnected
    client.onLeft = OnDisconnected
    
    playerHost : Player = Player(Vector(0.9, 0.5))
    playerClient : Player = Player(Vector(0.1, 0.5))
    ball : Ball = Ball()
    DrawMiddleLine()
    
    playerClient.BindAll()

    def Ready(event):
        nonlocal gameStarted
        gameStarted = True
        window.unbind("<Return>")
        client.Send(Message(id = 0))
        SetMessageBoxText("")

    def Update():
        nonlocal lastFrame, nextFrame, updateCallID
        deltaTime = time.time() - lastFrame
        lastFrame = time.time()

        newPlayerPos = playerClient.pos + Vector(0, playerClient.yVelocity * deltaTime)
        newPlayerPos.y = min(1 - PLAYERHEIGHT / 2, max(PLAYERHEIGHT / 2, newPlayerPos.y))
        playerClient.MoveTo(newPlayerPos)

        msg = Message(id = 1)
        msg.AddFloat(playerClient.pos.y)
        client.Send(msg)

        if gameStarted:
            
            newPos = ball.pos + ball.velocity * deltaTime
            
            if newPos.y - BALLRADIUS <= 0:
                ball.velocity.y = abs(ball.velocity.y)
            elif newPos.y + BALLRADIUS >= 1:
                ball.velocity.y = -abs(ball.velocity.y)
            
            ball.MoveTo(newPos)

            if not ball.ownedByHost:
                client.Send(msg)
                if (playerClient.pos.x + PLAYERWIDTH / 2 >= ball.pos.x - BALLRADIUS and
                   ball.pos.x >= playerClient.pos.x and
                   abs(playerClient.pos.y - ball.pos.y) <= PLAYERHEIGHT / 2
                ):
                    ball.velocity = Vector(1, random.uniform(-0.5, 0.5))
                    msg = Message(id = 3)
                    msg.AddFloat(ball.velocity.y)
                    msg.AddFloat(ball.pos.x)
                    msg.AddFloat(ball.pos.y)
                    client.Send(msg)
                    ball.ownedByHost = True
                
                elif ball.pos.x <= 0:
                    GameOver(True)
                    client.Send(Message(id = 4))
                
            if useAI:
                AITargetPosY = 0.5 if ball.ownedByHost else ball.pos.y
                relativeTarget = AITargetPosY - playerClient.pos.y
                positionTolarence = 0.2 if ball.ownedByHost else 0.01
                if abs(relativeTarget) < positionTolarence:
                    playerClient.pressingDown = False
                    playerClient.pressingUp = False
                elif relativeTarget < 0:
                    playerClient.pressingDown = False
                    playerClient.pressingUp = True
                else:
                    playerClient.pressingDown = True
                    playerClient.pressingUp = False
                playerClient.UpdateVelocity()

        client.Update()

        if gameOver:
            KeepConnectionAlive()
            window.after(3000, Restart)
            return
        
        nextFrame += FRAMEDELTATIME / 1000
        timeUntilNextFrame = nextFrame - time.time()
        if timeUntilNextFrame < 0:
            timeUntilNextFrame = 0
        updateCallID = window.after(
            round(timeUntilNextFrame * 1000),
            Update
        )

    def KeepConnectionAlive():
        if gameOver:
            client.Update()
            window.after(FRAMEDELTATIME, KeepConnectionAlive)
        
    def Restart():
        nonlocal gameOver, lastFrame, nextFrame, playerHost, playerClient, ball

        gameOver = False
        lastFrame = time.time()
        nextFrame = time.time() + FRAMEDELTATIME / 1000
        window.after(FRAMEDELTATIME, Update)

        playerHost.Destroy()
        playerHost = Player(Vector(0.9, 0.5))
        playerClient.Destroy()
        playerClient = Player(Vector(0.1, 0.5))
        playerClient.BindAll()
        ball.Destroy()
        ball = Ball()

        SetMessageBoxText("")

    lastFrame = time.time()
    nextFrame = time.time() + FRAMEDELTATIME / 1000
    updateCallID = window.after(FRAMEDELTATIME, Update)

Menu()

window.mainloop()
