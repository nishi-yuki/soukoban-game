#! /usr/bin/env python3
#-*-coding:utf8;-*-
import sys
import termios
import tty

LINUX = True
WINDOWS = False
CLEAR = '×'


def getkeyfunc():
    if LINUX:
        fd = sys.stdin.fileno()
        pr = termios.tcgetattr(fd)
        def linuxgetkey():
            'POSIXキー入力受付'
            try:
                tty.setcbreak(sys.stdin.fileno())
                result = sys.stdin.read(1)
                return result
            finally:
                termios.tcsetattr(fd, termios.TCSANOW, pr)
        return linuxgetkey
    elif WINDOWS:
        print('未対応です')
        exit()

#移動定義クラス
class Empty():
    '空白を意味するクラス'
    icon = ' '
    def up(self):
        return True
    def down(self):
        return True
    def right(self):
        return True
    def left(self):
        return True

class Null():
    '虚無を意味するクラス'
    def up(self):
        return False
    def down(self):
        return False
    def right(self):
        return False
    def left(self):
        return False

#属性指定クラス
class Setproperty:
    def __init__(self, x, y, icon):
        self._x = x
        self._y = y
        self.icon = icon
        self._before = empty
        set_stage(x, y, self)

class Mono(Setproperty):
    #書き込みメソッド
    def spawn(self, x = None, y = None):
        '成功したらTrue,失敗したらFalse'
        #デフォルト引数処理
        if x == None: x=self._x
        if y == None: y=self._y
        #世界の外へ行けないように
        if x < 0 or y < 0 or \
        x >= X_MAX or y >= Y_MAX:
            return False
        else:
            before = getele(x, y)
            set_stage(self._x, self._y, self._before)
            set_stage(x, y, self)
            self._x, self._y = x, y
            self._before = before
            return True
    #移動用メソッド
    def up(self):
        dest = self._x, self._y-1
        if not getele(*dest).up():
            return False
        return self.spawn(*dest)
    def down(self):
        dest = self._x, self._y+1
        if not getele(*dest).down():
            return False
        return self.spawn(*dest)
    def right(self):
        dest = self._x+1, self._y
        if not getele(*dest).right():
            return False
        return self.spawn(*dest)
    def left(self):
        dest = self._x-1, self._y
        if not getele(*dest).left():
            return False
        return self.spawn(*dest)

class Nimotu(Mono):
    def __init__(self, x, y, icon):
        super().__init__(x, y, icon)
        self.is_del = False
    def dele(self):
        set_stage(self._x, self._y, empty)
        self.is_del = True
        return True
    def up(self):
        dest = self._x, self._y-1
        result = getele(*dest).up()
        if self.is_del:
            #このときこのオブジェクトは消去されている
            return True
        elif not result:
            return False
        elif result:
            return self.spawn(*dest)
    def down(self):
        dest = self._x, self._y+1
        result = getele(*dest).down()
        if self.is_del:
            #このときこのオブジェクトは消去されている
            return True
        elif not result:
            return False
        elif result:
            return self.spawn(*dest)
    def right(self):
        dest = self._x+1, self._y
        result = getele(*dest).right()
        if self.is_del:
            #このときこのオブジェクトは消去されている
            return True
        elif not result:
            return False
        elif result:
            return self.spawn(*dest)
    def left(self):
        dest = self._x-1, self._y
        result = getele(*dest).left()
        if self.is_del:
            #このときこのオブジェクトは消去されている
            return True
        elif not result:
            return False
        elif result:
            return self.spawn(*dest)

class Player(Mono):
    def dele(self):
        return False

class Wall(Setproperty,Null):
    pass    #これで完成形

class Goal(Setproperty):
    goallist = []
    clearedicon = CLEAR
    def __init__(self, x, y, icon):
        super().__init__(x, y, icon)
        self.is_clear = False
        Goal.goallist.append(self)
    #移動関数
    def up(self):
        if getele(self._x, self._y+1).dele():
            self._clear()
        return True
        #return False
    def down(self):
        if getele(self._x, self._y-1).dele():
            self._clear()
        return True
        #return False
    def right(self):
        if getele(self._x-1, self._y).dele():
            self._clear()
        return True
        #return False
    def left(self):
        if getele(self._x+1, self._y).dele():
            self._clear()
        return True
        #return False
    #勝利
    def _clear(self):
        Wall(self._x, self._y, Goal.clearedicon)
        self.is_clear = True
        #print('ok1')
        if all([goal.is_clear for goal in Goal.goallist]):
            #print('ok2')
            clear()

'''
def anime():
    for i in range(144):
        x,y = divmod(i,12)
        print(x,y)
        stage[x][y]
        time.sleep(0.1)
        stage_print()
'''
def stage_setup(raw):
    """ステージ生成用関数
    文字列からステージを作成する
    raw文字列推奨
    例
    stage_setup('''
    	000wwwwwwwg0g0
     www0000000w000
     wg000000000w00
     wwww00nnn00000
     0000w000000000
     0000w000000000
    	00000w00000000
    	''')
    	
    """
    global stage, X_MAX, Y_MAX
    eledict = {
    'n': lambda x, y : Nimotu(x,y,'$'),
    'g': lambda x, y : Goal(x,y,'@'),
    'w': lambda x, y : Wall(x,y,'#'),
    '0': lambda x, y : None,
    	}
    raw = raw.split()
    Y_MAX = len(raw)
    X_MAX = len(raw[0])
    stage = [[empty]*X_MAX for i in range(Y_MAX)]
    for y, line in enumerate(raw):
        #print(line)
        for x, etype in enumerate(line):
            eledict[etype](x, y)
    

def clear():
    global is_clear
    #print('ok3')
    is_clear = True

def set_stage(x, y, obj):
    global stage
    stage[y][x] = obj

def stage_print():
    for line in stage:
        for dot in line:
            #~~~ここから横行印字~~~
            print(dot.icon,end=' ')
            #~~~ここまで~~~
        print()

def getele(x,y):
    if x < 0 or y < 0 or \
        x >= X_MAX or y >= Y_MAX:
            return null
    ele = stage[y][x]
    return ele

def move(x,y):
    player = Player(x,y,'O')
    stage_print()
    while True:
        cmd = getkey()
        if cmd == 'w':
            player.up()
        elif cmd == 'a':
            player.left()
        elif cmd == 's':
            player.down()
        elif cmd == 'd':
            player.right()
        elif cmd == 'q':
            return
        if is_clear:
            stage_print()
            #print('ok4')
            break
        #print('__' * X_MAX)
        stage_print()
    print('おめでとう！！！')

empty = Empty()
null = Null()
getkey = getkeyfunc()
stage = None
Y_MAX = None
X_MAX = None
is_clear = False

if __name__ == '__main__':
    stage_setup('''
000wwwwwwwg0g0
www0000000w000
wg00000000w000
wwww00nnn00w00
0000w000000000
0000w000000000
00000w00000000
0000n0000n0000
00000000000000
00000n00000000
0000000g000000
00000000000000
00000000000000
00000000000000
    ''')
    move(5,2)
