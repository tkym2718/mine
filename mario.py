import pyxel

# Pyxelの初期化
pyxel.init(256, 256, title="Mario", fps=60)
pyxel.load("mario.pyxres")
pyxel.playm(0, loop=True)

# 定数定義
GRAVITY = 12
INERTIA = 0.7
TRANSPARENT = 6

# グローバル変数
x = 32
y = 200
dx = 0
dy = 0
direction = 1
jump = 0
char_width = 16
char_height = 16
chk_point = [(0, 0), (char_width, 0), (0, char_height), (char_width, char_height)]
enemy_positions = [(300, 200),(550, 200), (3140, 200)]

music_time = 0
music_playing = False

def is_collision(x, y):
    """
    指定された座標が地形と衝突しているかを判定する関数。
    """
    for xi, yi in chk_point:
        tile_x = (x + xi) // 8
        tile_y = (y + yi) // 8

        # タイルマップの切り替え
        if tile_x < 256:  # 2048ピクセル以内
            tilemap_index = 0
        else:  # 2048ピクセル以降
            tilemap_index = 1
            tile_x -= 256  # タイルマップ1の座標に変換

        # 衝突判定
        if 2 <= pyxel.tilemaps[tilemap_index].pget(tile_x, tile_y)[1] < 6:
            return True
    return False

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = 1
        self.is_alive = True
        self.is_jumping = False
        self.is_dead = False

    def death(self):

        if not self.is_alive:
            return
        self.is_alive = False
        pyxel.stop()
        pyxel.play(3, 49)

        # 死亡アニメーション用のジャンプ
        for _ in range(10):  # 短いジャンプアニメーション
            self.y -= 8  # 上方向に移動
            draw()  # 描画を更新
            pyxel.flip()  # フレームを更新
        for _ in range(20):  # 落下アニメーション
            self.y += 8  # 下方向に移動
            draw()  # 描画を更新
            pyxel.flip()  # フレームを更新
        self.is_dead = True  # 死亡状態にする

    def update(self):

        # 横方向の移動
        if pyxel.btn(pyxel.KEY_A):
            self.dx = max(self.dx - 1, -3)
            self.direction = -1
        elif pyxel.btn(pyxel.KEY_D):
            self.dx = min(self.dx + 1, 3)
            self.direction = 1
        else:
            self.dx = int(self.dx * INERTIA)  # 慣性

        # ジャンプ処理
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.is_jumping:
            self.dy = -9  # ジャンプの初速度
            self.is_jumping = True

        # 重力の適用
        self.dy += 0.5  # 重力加速度
        if self.dy > GRAVITY:
            self.dy = GRAVITY  # 最大落下速度を制限

        # 縦方向の移動
        next_y = self.y + self.dy
        if not is_collision(self.x, next_y):
            self.y = next_y
        else:
            self.dy = 0  # 地面に接触した場合は停止
            self.is_jumping = False  # ジャンプ状態を解除

        # 横方向の移動
        next_x = self.x + self.dx
        if not is_collision(next_x, self.y):
            self.x = next_x
        else:
            self.dx = 0  # 壁に衝突した場合は停止

    def draw(self):
        if self.x < pyxel.width // 2:
            screen_x = self.x
        else:
            screen_x = pyxel.width // 2 - char_width // 2

        if self.is_alive:
            # 生存時のスプライト描画
            pyxel.blt(
                screen_x, self.y, 0, 0, 96, self.direction * char_width, char_height, TRANSPARENT
            )
        else:
            # 死亡時のスプライト描画
            pyxel.blt(
                screen_x, self.y, 0, 32, 96, char_width, char_height, TRANSPARENT
            )

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = -1  # 左方向に移動
        self.dy = 0
        self.width = 16
        self.height = 16
        self.direction = 0  # 0: 左, 1: 右
        self.is_alive = True
        self.death_time = 0
        self.is_in_camera = True

    def is_stomped(self, player): #踏んだかどうか
        if (
            player.x + char_width > self.x
            and player.x < self.x + self.width
            and player.y + char_height >= self.y
            and player.dy > 0
        ):
            self.is_alive = False
            self.death_time = 12
            pyxel.play(3,53,resume=True) #敵を踏んだ音
            return True
        return False

    def genarate(self, player):
        if self.x - player.x + pyxel.width:
            self.is_in_camera = True

    def update(self):

        if not self.is_in_camera:
            return

        if not self.is_alive:
            if self.death_time > 0:
                self.death_time -= 1
            return

        # 重力の適用
        if not is_collision(self.x, self.y + 1):
            self.dy += 1  # 重力加速
        else:
            self.dy = 0  # 床に接触している場合は停止

        # 縦方向の移動
        next_y = self.y + self.dy
        if not is_collision(self.x, next_y):
            self.y = next_y
        else:
            self.dy = 0  # 衝突している場合は停止

        # 横方向の移動
        next_x = self.x + self.dx
        if is_collision(next_x, self.y):
            self.direction = 1 if self.direction == 0 else 0
            self.dx = -self.dx
        else:
            self.x = next_x

    def draw(self, cam_x):
        if self.is_in_camera:
            if self.is_alive:
                pyxel.blt(
                    self.x - cam_x, self.y, 0, 0, 48, self.width, self.height, TRANSPARENT
                )
            elif self.death_time > 0:
                pyxel.blt(
                    self.x - cam_x, self.y, 0, 0, 64, self.width, self.height, TRANSPARENT
                )

def update_position(x, y, dx, dy, is_jump):
    """
    プレイヤーや敵の位置を更新する関数。
    """
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
    while 0 < steps_y:
        if is_collision(x, y + ud):
            dy = 0
            if ud > 0:
                is_jump = False
            break
        y += ud
        steps_y -= 1
    else:
        if not is_collision(x, y + 1):
            is_jump = True
            dy = 0

    return x, y, dx, dy, is_jump

# プレイヤーと敵の初期化
player = Player(x, y)
enemies = [Enemy(x, y) for x, y in enemy_positions]

def update():
    """
    ゲームの更新処理。
    """
    global x, y, dx, dy, direction, jump, music_time, music_playing

    # プレイヤーが画面外に落下した場合
    if player.y > 512 and player.is_alive:  # y座標が512より大きい場合
        player.death()
        return

    # プレイヤーの更新処理
    if player.is_alive:
        player.update()

    # 敵の更新処理
    for enemy in enemies[:]:
        enemy.update()
        if enemy.is_stomped(player):
            enemies.remove(enemy)
        elif (
            player.x + char_width > enemy.x
            and player.x < enemy.x + enemy.width
            and player.y + char_height > enemy.y
            and player.y < enemy.y + enemy.height
        ):
            # プレイヤーと敵が衝突した場合
            player.death()

    # プレイヤーが指定の座標を通過した場合
    if not music_playing and 1648 <= player.x <= 1650 and 140 <= player.y <= 144:
        pyxel.stop()  # 現在の音楽を停止
        pyxel.playm(1, loop=True)  # 新しい音楽を再生
        music_time = 600  # タイマーを開始
        music_playing = True

    # 10秒後に元の音楽に戻す
    if music_playing:
        music_time -= 1
        if music_time < 0:
            pyxel.stop()
            pyxel.playm(0, loop=True)
            music_playing = False

def draw():

    pyxel.cls(0)  # 画面クリア

    # カメラのX座標を計算
    if player.x < pyxel.width // 2:
        cam_x = 0  # カメラは画面左端で固定
    else:
        cam_x = player.x - pyxel.width // 2 + char_width // 2  # キャラクターを追尾

    # タイルマップの描画範囲を拡張
    if cam_x < 2048 - pyxel.width:
        pyxel.bltm(0, 0, 0, cam_x, 0, pyxel.width, pyxel.height, 0)
    elif cam_x >= 2048 - pyxel.width and cam_x < 2048:
        overlap = cam_x - (2048 - pyxel.width)
        pyxel.bltm(0, 0, 0, cam_x, 0, pyxel.width - overlap, pyxel.height, 0)
        pyxel.bltm(pyxel.width - overlap, 0, 1, 0, 0, overlap, pyxel.height, 0)
    else:
        pyxel.bltm(0, 0, 1, cam_x - 2048, 0, pyxel.width, pyxel.height, 0)

    # プレイヤーを描画
    player.draw()

    # 敵を描画
    for enemy in enemies:
        enemy.draw(cam_x)

    # デバッグ用：座標表示
    pyxel.text(5, 5, f"Player: ({player.x},{player.y})", 7)
    for i, enemy in enumerate(enemies):
        pyxel.text(5, 15 + i * 10, f"Enemy {i}: {enemy.is_in_camera}", 7)

# Pyxelのメインループ
pyxel.run(update, draw)