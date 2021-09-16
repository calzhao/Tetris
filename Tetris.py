import pgzrun as pg
import random
import time

# 俄罗斯方块小游戏

# 创建常量
WIDTH = 1000
HEIGHT = 480


BOXSIZE = 20  # 每个小格子的宽和高
BOARDWIDTH = 15  # 游戏窗宽度
BOARDHEIGHT = 24  # 游戏窗高度
BLANK = "."  # 表示空白空格


XMARGIN = int(
    (WIDTH - BOARDWIDTH * BOXSIZE) / 2
)  # (XMARGIN:窗口左边或右边剩下的像素数=总窗口的宽度-游戏界面一行上的方块个数*每个方块的宽度)/2
TOPMARGIN = (
    HEIGHT - (BOARDHEIGHT * BOXSIZE) - 5
)  # TOPMARGIN：游戏窗口上面剩下的像素数=总窗口的高度-（游戏界面一列上的方块个数*每个方块的高度）-5


SHAPEWIDTH = 5  # 砖块模板宽
SHAPEHEIGHT = 5  # 砖块模板高


STARTCOLOR = "olive drab"  # 开始界面字体颜色
ENDCOLOR = "gray18"  # 结束界面字体颜色
TEXTCOLOR = "olive drab"  # 文本的字体颜色


COLORS = (
    "darkolivegreen2",
    "gold",
    "coral1",
    "mediumpurple1",
    "lightskyblue1",
)  # 方块五种颜色，存于COLORS元组中


O_SHAPE = [[".....", ".....", ".OO..", ".OO..", "....."]]  # O型模板


S_SHAPE = [[".....", ".....", "..OO.", ".OO..", "....."],  # S形状的模板
    [".....", "..O..", "..OO.", "...O.", "....."]]  # S逆时针变化的形状


Z_SHAPE = [[".....", ".....", ".OO..", "..OO.", "....."],  # Z形模板
    [".....", "..O..", ".OO..", ".O...", "....."]] # z顺时针变化的形状


I_SHAPE = [["..O..", "..O..", "..O..", "..O..", "....."],  # I型模板
    [".....", ".....", "OOOO.", ".....", "....."]]


J_SHAPE = [[".....", ".O...", ".OOO.", ".....", "....."],  # J型模板
    [".....", "..OO.", "..O..", "..O..", "....."],
    [".....", ".....", ".OOO.", "...O.", "....."],
    [".....", "..O..", "..O..", ".OO..", "....."]]


L_SHAPE = [[".....", "...O.", ".OOO.", ".....", "....."],  # L型模板
    [".....", "..O..", "..O..", "..OO.", "....."],
    [".....", ".....", ".OOO.", ".O...", "....."],
    [".....", ".OO..", "..O..", "..O..", "....."]]


T_SHAPE = [[".....", "..O..", ".OOO.", ".....", "....."],  # T型模板
    [".....", "..O..", "..OO.", "..O..", "....."],
    [".....", ".....", ".OOO.", "..O..", "....."],
    [".....", "..O..", ".OO..", "..O..", "....."]]


SHAPES = {# SHAPES是一个字典，它储存了所有不同的模板(列表)。每个模板都拥有一个形状所有可能的旋转(列表)。
    "S": S_SHAPE, 
    "Z": Z_SHAPE,
    "J": J_SHAPE,
    "L": L_SHAPE,
    "I": I_SHAPE,
    "O": O_SHAPE,
    "T": T_SHAPE }


# 玩家的等级和模式
player = Actor("face_sweat")
player.flag = 0
player.lever = 1
player.mode = 0


#每次需要刷新窗口的时候，会自动调用draw函数
def draw():
    # 清除窗口，设置背景
    if player.flag == 0:
        startScreen()
        # print('错误')
    elif player.flag == 1:
        # 在此处添加游戏背景
        drawBoard(player.board)
        if player.currentPiece != None:  # 砖块没有下落到底部
            drawPiece(player.currentPiece)
        if player.currentPiece == None:  # 在下落的砖块已经着陆之后，currentPiece变量设置为None
            player.currentPiece = (
                player.nextPiece
            )  # 这意味着nextPiece中的砖块将会复制到currentPiece中。
            player.nextPiece = getPiece()  # 生成新的新的nextPiece砖块，砖块可以通过getPiece()函数生成。
            player.lastFall = (
                time.time()
            )  # 该变量也重新设置为当前时间，以便砖块能够在fallBreak中所设置的那么多秒之内下落。
            if not isValidPos(player.board, player.currentPiece):
                # 但是，如果游戏板已经填满了，isValidPos()将返回False，导致这是一个无效的位置，那么，我们知道游戏板已经填满了，玩家失败了。
                player.flag = 2  # 在这种情况下 runGame()函数将被返回。
        drawStatus(player.score, player.level)
        drawNext(player.nextPiece)
    elif player.flag == 2:
        screen.clear()
        drawStatus(player.score, player.level)
        showEndGame()
    else:
        screen.clear()
        showPause()


#每一帧都会自动调用update函数
def update():
    if player.flag == 1:
        # 让砖块自然落下
        if time.time() - player.lastFall > player.fallBreak:  # fallBreak向下移动的速率
            if not isValidPos(
                player.board, player.currentPiece, adjY=1
            ):  # 当砖块下一个位置无效时，即表示砖块当前已经着陆了。
                fixInBoard(player.board, player.currentPiece)  # 在游戏板数据结构中记录这个着陆的砖块
                removeline = removeLines(player.board)
                player.score = (
                    player.score + removeline
                )  # removeLines()将负责删除掉游戏板上任何已经填充完整的行，并且将方块向下推动。
                # removeLines()函数还会返回一个整数值，表明消除了多少行，以便我们将这个数字加到得分上。
                oldlevel = player.level
                levelAndFallBreak(
                    player.score, player.mode
                )  # 由于分数已经修改了，我们调用LevelAndFallBreak()函数来更新当前的关卡以及砖块下落得频率。
                if oldlevel < player.level:  # 升级时播放升级音效
                    sounds.levelup.play()
                elif removeline != 0:  # 消除一行时，播放消除音效
                    sounds.remove.play()
                player.currentPiece = None  # 最后我们将currentPiece变量设置为None,并生成一个随机的新砖块作为下一个砖块。
            else:
                # 如果砖块没有着陆，我们直接将其Y位置向下设置一个空格，并且将lastFall重置为当前时间
                player.currentPiece["y"] = player.currentPiece["y"] + 1
                player.lastFall = time.time()


def showEndGame():
    music.stop()
    screen.blit("end3", (0, 0))
    drawStatus(player.score, player.level)
    screen.draw.text(
        "Game Over", (WIDTH / 2 - 250, HEIGHT / 2 - 60), fontsize=130, color=ENDCOLOR
    )


def showPause():
    screen.blit("stop2", (0, 0))
    screen.draw.text("Tap R to resume", (400, 100), fontsize=40, color=TEXTCOLOR)
    screen.draw.text("Help instructions:", (400, 160), fontsize=30, color=TEXTCOLOR)
    screen.draw.text(
        "LEFT/RIGHT for horizontal shift", (400, 190), fontsize=25, color=TEXTCOLOR
    )
    screen.draw.text("UP for rotation", (400, 220), fontsize=25, color=TEXTCOLOR)
    screen.draw.text(
        "DOWN for falling rapidly", (400, 250), fontsize=25, color=TEXTCOLOR
    )
    screen.draw.text(
        "SPACE for directly move to bottom", (400, 280), fontsize=25, color=TEXTCOLOR
    )


def isValidPos(
    board, piece, adjX=0, adjY=0
):  # board:游戏板 piece：砖块 adjX,adjY表示5x5砖块左上角方块的坐标
    for x in range(SHAPEWIDTH):  # SHAPEWIDTH=5 SHAPEWIDTH=5
        for y in range(SHAPEHEIGHT):  # 遍历砖块模板的所有方块
            isAboveBoard = y + piece["y"] + adjY < 0  # 模板还没完全进入游戏板
            if (
                isAboveBoard or SHAPES[piece["shape"]][piece["rotation"]][y][x] == BLANK
            ):  # 在5x5模板中不等于'.'的方块，即有效方块
                continue
            if not isOnBoard(
                x + piece["x"] + adjX, y + piece["y"] + adjY
            ):  # 有效砖块不在游戏板上
                return False
            if (
                board[x + piece["x"] + adjX][y + piece["y"] + adjY] != BLANK
            ):  # 有效砖块和游戏板上的方块重叠
                return False
    return True


def isOnBoard(x, y):  # isOnBoard()函数检查参数x,y坐标是否存在于游戏板上
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT  # BOARDWIDTH=10，BOARDHEIGHT=20


def fixInBoard(
    board, piece
):  # 游戏板数据结构用来记录之前着陆的砖块。该函数所做的事情是接受一个砖块数据结构，并且将其上的有效砖块添加到游戏板数据结构中
    for x in range(SHAPEWIDTH):  # 该函数这在一个砖块着陆之后进行
        for y in range(SHAPEHEIGHT):  # 嵌套for遍历了5x5砖块数据结构,当找到一个有效砖块时，将其添加到游戏板中
            if SHAPES[piece["shape"]][piece["rotation"]][y][x] != BLANK:
                player.board[x + piece["x"]][y + piece["y"]] = piece[
                    "color"
                ]  # 游戏板数据结构的值有两种形式：数字(表示砖块颜色)，'.'即空白，表示该处没有有效砖块


def removeLines(board):  # 删除所有填满行，每删除一行要将游戏板上该行之上的所有方块都下移一行。返回删除的行数
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1  # BOARDHEIGHT=20-1=19即从最低行开始
    while y >= 0:  # 注意当删除一行时y没有生变化，因为此时它的值已经更新为新的一行了
        if isCompleteLine(board, y):  # 如果该行填满
            for pullDownY in range(y, 0, -1):  # range(y, 0, -1)范围[y,1]
                for x in range(BOARDWIDTH):
                    player.board[x][pullDownY] = board[x][
                        pullDownY - 1
                    ]  # 将删除的行之上的每一行的值都复制到下一行
                for x in range(BOARDWIDTH):  # 删除第一行
                    player.board[x][0] = BLANK
            numLinesRemoved = numLinesRemoved + 1
        else:
            y = y - 1  # 移到下一行
    return numLinesRemoved


def isCompleteLine(board, y):  # 判断y行是否填满，填满返回True
    for x in range(BOARDWIDTH):  # 遍历该行的所有砖块
        if board[x][y] == BLANK:  # 如果存在空白，则没填满
            return False
    return True


def drawStatus(score, level):
    screen.draw.text(
        "Score: %s" % player.score,
        topleft=(WIDTH - 150, 20),
        fontsize=30,
        color=TEXTCOLOR,
    )
    screen.draw.text(
        "Level: %s" % player.level,
        topleft=(WIDTH - 150, 50),
        fontsize=30,
        color=TEXTCOLOR,
    )


def drawNext(piece):
    screen.draw.text("Next:", topleft=(WIDTH - 120, 80), fontsize=30, color=TEXTCOLOR)
    drawPiece(piece, pixelx=WIDTH - 120, pixely=100)


def drawPiece(piece, pixelx=None, pixely=None):  # pixelx, pixely为5x5砖块数据结构左上角在游戏板上的的坐标
    shapeToDraw = SHAPES[piece["shape"]][
        piece["rotation"]
    ]  # SHAPES[piece['shape']][piece['rotation']]为一个图形的一种旋转方式
    if pixelx == None and pixely == None:
        # 然而，'Next'砖块并不会绘制到游戏板上。在这种情况下，我们忽略砖块数据结构中包含的位置信息，而是让drawPiece()函数的调用者
        # 为pixelx何pixely参数传递实参，以指定应该将砖块确切地绘制到窗口上的什么位置。
        pixelx, pixely = toPixelCoords(piece["x"], piece["y"])  # 将砖块坐标转换为像素坐标。
    for x in range(SHAPEWIDTH):  # 遍历5x5砖块数据结构
        for y in range(SHAPEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                drawBox(
                    None,
                    None,
                    piece["color"],
                    pixelx + (x * BOXSIZE),
                    pixely + (y * BOXSIZE),
                )


def on_key_down():
    if keyboard[keys.A] or keyboard[keys.N] or keyboard[keys.H]:
        player.flag = 1
        player.board = initBoard()
        player.lastFall = time.time()  # 最后下落砖块的时间
        player.score = 0  # 得分
        levelAndFallBreak(
            player.score, player.mode
        )  # 计算关卡数和下落频率，因为此时score=0，所以经计算后level=1,fallBreak=0.25
        player.currentPiece = getPiece()  # currentPiece变量将设置为能够被玩家操作的当前下落的砖块
        player.nextPiece = getPiece()  # nextPice为在屏幕的Next部分出现的砖块，即下一个将要下落的砖块
        music.play("bgm2")
        if keyboard[keys.A]:
            player.mode = 1
        elif keyboard[keys.N]:
            player.mode = 2
        elif keyboard[keys.H]:
            player.mode = 3

    elif keyboard[keys.LEFT] and isValidPos(player.board, player.currentPiece, adjX=-1):
        player.currentPiece["x"] = player.currentPiece["x"] - 1  # 左移

    elif keyboard[keys.RIGHT] and isValidPos(player.board, player.currentPiece, adjX=1):
        player.currentPiece["x"] = player.currentPiece["x"] + 1

    # 按向上箭头将会把砖块为其下一个旋转状态。代码所需要做的只是currentPiece字典中的'rotation'键的值增加1。然而，如果增加'rotation'键的值
    # 大于旋转的总数目，那么用该形状可能旋转的总数目(这就是len(SHAPES[currentPiece['shape']的含义)来模除它，然后，这个值将回滚到从0开始。
    elif keyboard[keys.UP]:
        player.currentPiece["rotation"] = (player.currentPiece["rotation"] + 1) % len(
            SHAPES[player.currentPiece["shape"]]
        )
        if not isValidPos(player.board, player.currentPiece):
            player.currentPiece["rotation"] = (
                player.currentPiece["rotation"] - 1
            ) % len(SHAPES[player.currentPiece["shape"]])

    # 如果按下了向下键，说明玩家想要砖块下落得比正常速度更快一些。
    elif keyboard[keys.DOWN]:
        if isValidPos(player.board, player.currentPiece, adjY=1):  # 下一个位置有效
            player.currentPiece["y"] = player.currentPiece["y"] + 1  # 移动

    elif keyboard[keys.SPACE]:
        while isValidPos(player.board, player.currentPiece, adjY=1):
            player.currentPiece["y"] = player.currentPiece["y"] + 1
    elif keyboard[keys.R]:
        player.flag = 1
    elif keyboard[keys.ESCAPE]:
        player.flag = -1


def levelAndFallBreak(score, mode):  # 每次玩家填满一行，起分数都将增加1分。每增加3分，游戏就进入下一个关卡，砖块下落得会更快。
    player.level = (int(score / 3) + 1)  # 给该函数的分数来计算的。
    player.fallBreak = 0.3 - (score * 0.005 * mode)  # 舍入到0。代码这里的+1部分，是因为我们想要第一个关卡作为第一关，而不是第0关。
    return


def getPiece():
    shape = random.choice(list(SHAPES.keys()))  # SHAPES是一个字典，它的键为代表形状的字母，值为一个形状所有可能的旋转(列表的列表)。
    # SHAPES.keys()返回值是(['Z','J','L','I','O','T'])的元组，list(SHAPES.keys())返回值是['Z','J','L','I','O','T']列表
    # 这样转换是因为random.choice()函数只接受列表值作为其参数。 random.choice()函数随机地返回列表中的一项的值，即可能是'Z'。
    newPiece = {
        "shape": shape,
        "rotation": random.randint(
            0, len(SHAPES[shape]) - 1
        ),  # rotation：随机出砖块是多个旋转形装的哪个
        # 列如SHAPES['Z']的返回值为[[形状],[形状]]，len(SHAPES['z'])的返回值为2 2-1=1 random.randint(0,1)随机范围是[0,1]
        "x": int(BOARDWIDTH / 2)
        - int(SHAPEWIDTH / 2),  #'x'代表砖块5x5数据结构左上角第一个方格的横坐标，键的值总是要设置为游戏板的中间。
        "y": -2,  #'x'代表砖块5x5数据结构左上角第一个方格的纵坐标，'y'键的值总是要设置为-2以便将其放置到游戏板上面一点点(游戏板的首行是0行)
        "color": random.randint(0, len(COLORS) - 1),  # COLORS：不同颜色的一个元组
    }
    return newPiece  # getPiece()函数返回newPiece字典


def startScreen():
    screen.clear()
    screen.blit("小王子1", (0, 0))
    screen.draw.text("Tetromino", (320, 100), fontsize=100, color=STARTCOLOR)
    screen.draw.text("——Do you see my rose?", (420, 180), fontsize=40, color=STARTCOLOR)
    screen.draw.text(
        """Press A/N/H to enter easy/normal/hard mode""",
        (290, 300),
        fontsize=30,
        color=STARTCOLOR,
    )


def drawBoard(board):  # 绘制游戏板边界
    screen.clear()
    rect1 = Rect(
        (XMARGIN - 3, TOPMARGIN - 7),
        (BOARDWIDTH * BOXSIZE + 8, BOARDHEIGHT * BOXSIZE + 20),
    )
    screen.blit("back1", (0, 0))
    rect2 = Rect((XMARGIN, TOPMARGIN), (BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    for x in range(BOARDWIDTH):  # 遍历游戏板
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])  # 这个函数会自动找出有效方块并绘制


def drawBox(boxx, boxy, color, pixelx=None, pixely=None):  # 绘制一个有效方块
    if color == BLANK:  # 如果这不是一个有效方块，这是5x5一个空白
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = toPixelCoords(boxx, boxy)  # 将游戏板上方块的坐标转化成像素坐标
    rect1 = Rect((pixelx + 1, pixely + 1), (BOXSIZE - 1, BOXSIZE - 1))
    screen.draw.filled_rect(
        rect1, COLORS[color]
    )  # 留出1像素的空白，这样才能在砖块中看到组成砖块,不然砖块看起来就只有一片颜色。


def toPixelCoords(boxx, boxy):  # 将游戏板上方块的坐标转化成像素坐标
    return (
        (XMARGIN + (boxx * BOXSIZE)),
        (TOPMARGIN + (boxy * BOXSIZE)),
    )  # XMARGIN为游戏板左顶点的横坐标，TOPMARGIN为游戏板左顶点的纵坐标


def initBoard():  # 创建一个新的游戏板数据结构。
    board = []  # 创建一个空白的游戏板
    for i in range(BOARDWIDTH): 
        board.append([BLANK] * BOARDHEIGHT)
    return board


pg.go()