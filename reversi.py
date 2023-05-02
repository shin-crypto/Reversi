import tkinter as tk
from tkinter import font, messagebox

def put_piece(event): #クリック時の処理
    global PASS, PASSTIME, TURN
    if PASS: #パスフラグが真なら手番を相手に移す
        PASS = False
        PASSTIME += 1
        TURN *= -1
        search_space()
    else:
        if 20<event.x<660 and 20<event.y<660: #クリックした画面上の座標から盤面上のマスを割り出す
            X = (event.x-20)//80
            Y = (event.y-20)//80
            if BOARD[X][Y] >= 2: #パスフラグが偽でクリックしたマスが設置可能なら石を設置する処理を呼び出す
                PASSTIME = 0
                TURN_piece(X, Y, BOARD[X][Y]-2)

def TURN_piece(x, y, map): #石を設置して反転させる処理
    global TURN
    RECODE.append((TURN, x, y, MAP[map])) #棋譜に設置する石の色と位置、反転させるマスを記録
    BOARD[x][y] = TURN
    for i in enumerate(MAP[map]):
        for j in range(1,i[1][2]):
            BOARD[x + j*i[1][0]][y + j*i[1][1]] *= -1
    TURN *= -1
    search_space() #手番を変更して設置可能マスを探索する処理を呼び出す

def search_space(): #設置可能なマスを探索する処理
    global MAP,PASS
    fin = True #ゲーム終了のフラグ
    black = 0 #黒石の数
    white = 0 #白石の数
    MAP.clear() #一手前の反転可能な石の情報を初期化
    for y in range(8):
        for x in range(8): #盤面を探索し全ての空白のマスを0にしつつ黒石と白石の数を計上する
            if BOARD[x][y]>=2:
                BOARD[x][y]=0
            if BOARD[x][y] == 0: #空白マスがあれば終了フラグを偽にする
                fin = False
            elif BOARD[x][y] == 1:
                black += 1
            elif BOARD[x][y] == -1:
                white += 1
    point = 2 #設置可能なマスを示す　マスごとに2以上の異なる数字を割り当てる
    for y in range(8):
        for x in range(8):
            if BOARD[x][y] == TURN: #盤面から手番の色の石を探索する
                for y_offset in range(-1, 2):
                    for x_offset in range(-1, 2): #探索した石の八方をさらに探索
                        x_pos = x + x_offset #探索した石と隣接した石のX座標
                        y_pos = y + y_offset #探索した石と隣接した石のY座標
                        offset = 1 #探索した石からの距離
                        if x_pos>7 or y_pos>7 or x_pos<0 or y_pos<0: #盤面外を参照しないようにスキップ
                            continue
                        while BOARD[x_pos][y_pos] == -TURN: #隣接した石が相手の色なら空白か自分の石に当たるまで同方向に探索
                            x_pos += x_offset
                            y_pos += y_offset
                            offset += 1
                            if x_pos>7 or y_pos>7 or x_pos<0 or y_pos<0 or BOARD[x_pos][y_pos] == TURN:
                                break
                            if BOARD[x_pos][y_pos] == 0: #相手の石を挟んだ空白があれば設置可能マスとして反転できる石を記録
                                BOARD[x_pos][y_pos] = point
                                MAP.append([(-x_offset, -y_offset, offset)])
                                point += 1
                            elif BOARD[x_pos][y_pos] >= 2: #すでに設置可能なマスとして記録してあればMAPの対応する要素に反転できる石を記録
                                MAP[BOARD[x_pos][y_pos]-2].append((-x_offset, -y_offset, offset))
    if point == 2: #設置可能なマスが無かった場合の処理
        if fin or PASSTIME > 1: #終了フラグが真、または2回連続でパスを行った場合ゲーム終了
            if black > white:
                font_black.pack()
            elif white > black:
                font_white.pack()
            else:
                text_draw.pack()
        else: #終了フラグが偽ならパス
            PASS = True

def undo(event): #一手戻す処理
    global TURN
    if RECODE: #棋譜に記録があればpopして設置したマスから石を除き反転させたマスに-1を掛けて元に戻す
        pre = RECODE.pop()
        BOARD[pre[1]][pre[2]] = 0
        for i in enumerate(pre[3]):
            for j in range(1,i[1][2]):
                BOARD[pre[1] + j*i[1][0]][pre[2] + j*i[1][1]] *= -1
        font_black.pack_forget()
        font_white.pack_forget()
        text_draw.pack_forget()
        TURN = pre[0]
        search_space()

def restart(event): #リスタート処理
    global TURN, PASS
    ret = messagebox.askyesno("Restart", "Restart?")
    if ret: #メッセージボックスでリスタートの確認を行いyesならゲームを初期化
        PASS = False
        font_black.pack_forget()
        font_white.pack_forget()
        text_draw.pack_forget()
        RECODE.clear()
        for y in range(8):
            for x in range(8):
                BOARD[x][y] = 0
        BOARD[3][3] = BOARD[4][4] = -1
        BOARD[3][4] = BOARD[4][3] = 1
        TURN = 1
        search_space()

def main_proc(): #画面描画処理
    canvas.delete("piece")
    for y in range(8):
        for x in range(8):
            X = 20+x*80
            Y = 20+y*80
            if BOARD[x][y]==1: #盤面の情報が1のマスに黒石を描画
                canvas.create_oval(X, Y, X+80, Y+80, fill="black", tags="piece")
            elif BOARD[x][y]==-1: #盤面の情報が-1のマスに白石を描画
                canvas.create_oval(X, Y, X+80, Y+80, fill="white", tags="piece")
            elif BOARD[x][y]>=2: #盤面の情報が2以上のマスに設置可能を示すオレンジ色の四角形を描画
                canvas.create_rectangle(X, Y, X+80, Y+80, fill="orange", tags="piece")
    if PASS: #パスフラグが真なら設置不可を表すアイコンを描画
        if TURN == 1:
            canvas.create_oval(690, 580, 770, 660, fill="black", tags="piece")
        elif TURN == -1:
            canvas.create_oval(690, 580, 770, 660, fill="white", tags="piece")
        canvas.create_line(690, 580, 770, 660, width=10, fill="red", tags="piece")
        canvas.create_line(770, 580, 690, 660, width=10, fill="red", tags="piece")
    root.after(100, main_proc)

root = tk.Tk()
canvas = tk.Canvas(root, width=800, height=680, bg="green")
canvas.pack()
for n in range(20, 680, 80): #盤面の描画
    canvas.create_line(n, 20, n, 660, width=2)
    canvas.create_line(20, n, 660, n, width=2)

canvas.bind("<ButtonPress>", put_piece) #画面がクリックされるとクリック時の処理を呼び出す
 
font = tk.font.Font(family= "Times", size=40)

#各種メッセージテキストのラベルを作成
font_black = tk.Label(root, text="BLACK WIN", font=font)
font_white = tk.Label(root, text="WHITE WIN", font=font)
text_draw = tk.Label(root, text="Draw", font=font)
text_undo = tk.Label(root, text="Undo", font=font)
text_restart = tk.Label(root, text="Restart", font=font)

text_undo.bind("<ButtonPress>", undo) #一手戻す処理をラベルに紐付け
text_restart.bind("<ButtonPress>", restart) #リスタート処理をラベルに紐付け

text_undo.place(x=670,y=20)
text_restart.place(x=670, y=100)

BOARD = [[0 for _ in range(8)]for _ in range(8)] #盤面の情報を表す二次元配列　空白を示す0で初期化
MAP = [] #石を設置した際に反転する石の位置の情報を設置箇所ごとに記録する配列
RECODE = [] #棋譜　設置した石の色、位置、設置した時に反転した石の情報を設置した順に記録する

PASS = False #パスフラグ　石を設置できない場合真になる
PASSTIME = 0 #連続のパス回数

#石の初期配置
BOARD[3][3] = BOARD[4][4] = -1
BOARD[3][4] = BOARD[4][3] = 1

TURN = 1 #手番を示す変数　1が黒、-1が白を示す　最初の手番は黒から始める

search_space() #最初に石の設置可能なマスを探索

main_proc() #画面描画

root.mainloop()