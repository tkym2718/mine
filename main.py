import pyxel

pyxel.init(256, 256, title="Mario", fps=60)
pyxel.load("mario.pyxres")
pyxel.playm(0, loop=True)

# 定数定義
TRANSPARENT = 6
GRAVITY = 15
INERTIA = 0.7
char_width = 16
char_height = 16
# プレイヤーの四隅チェック用オフセット
chk_point = [(0, 0), (char_width, 0), (0, char_height), (char_width, char_height)]

def is_collision(x, y):
    """指定座標でタイルとの衝突判定を行う"""
    for xi, yi in chk_point:
        tile_x = (x + xi) // 8
        tile_y = (y + yi) // 8
        # タイルの色番号が2～5の場合は衝突と判定
        if 2 <= pyxel.tilemap(0).pget(tile_x, tile_y)[1] < 6:
            return True
    return False

def update_position(x, y, dx, dy, is_jump):
    """1ピクセルずつ動かしながら衝突判定を行い、座標と速度、ジャンプ状態を更新する"""
    # 横方向の移動
    lr = pyxel.sgn(dx)
    steps_x = abs(dx)
    while steps_x > 0:
        if is_collision(x + lr, y):
            dx = 0
            break
        x += lr
        steps_x -= 1

    # 縦方向の移動
    ud = pyxel.sgn(dy)
    steps_y = abs(dy)
    while steps_y > 0:
        if is_collision(x, y + ud):
            dy = 0
            # 下方向への衝突なら着地とみなす
            if ud > 0:
                is_jump = False
            break
        y += ud
        steps_y -= 1
    else:
        # もし移動後に下方向に衝突がなければ空中状態
        if not is_collision(x, y + 1):
            is_jump = True
            dy = 0
    return x, y, dx, dy, is_jump

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = 1  # 1:右向き, -1:左向き
        self.is_alive = True
        self.is_jumping = False

    def update(self):
        # 横移動の入力処理
        if pyxel.btn(pyxel.KEY_A):
            self.dx = max(self.dx - 1, -3)
            self.direction = -1
        elif pyxel.btn(pyxel.KEY_D):
            self.dx = min(self.dx + 1, 3)
            self.direction = 1
        else:
            self.dx = int(self.dx * INERTIA)  # 減速（慣性）

        # ジャンプと重力処理
        if not self.is_jumping:
            # 地面がない場合は落下状態に
            if not is_collision(self.x, self.y + 1):
                self.is_jumping = True
            # ジャンプ開始
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.dy = GRAVITY
                self.is_jumping = True

        # 位置更新（衝突判定付き）
        self.x, self.y, self.dx, self.dy, self.is_jumping = update_position(
            self.x, self.y, self.dx, self.dy, self.is_jumping
        )

# グローバルのPlayerインスタンス
player = Player(32, 200)

def update():
    player.update()

def draw():
    pyxel.cls(0)
    # カメラをプレイヤー中心に合わせる
    cam_x = max(0, player.x - pyxel.width // 2 + char_width // 2)
    pyxel.bltm(0, 0, 0, cam_x, 0, pyxel.width, pyxel.height, 0)
    # プレイヤー描画（画面中央に表示）
    screen_x = pyxel.width // 2 - char_width // 2
    pyxel.blt(screen_x, player.y, 0, 0, 96, player.direction * char_width, char_height, TRANSPARENT)
    # デバッグ用：座標表示
    pyxel.text(5, 5, f"({player.x}, {player.y})", 7)

pyxel.run(update, draw)
