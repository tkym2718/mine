import pyxel

class App:

    def __init__(self):
        pyxel.init(256, 256, title="Quantum Gomoku")  # 画面サイズを適切に設定
        pyxel.mouse(True)                             # マウスの有効化
        pyxel.load("sprite.pyxres")                  # リソースファイルの読み込み
        self.board = [[0 for _ in range(15)] for _ in range(15)]  # 15x15の盤面
        self.turn = True                              # True: 黒, False: 白
        self.winner = None                            # 勝者 (None: ゲーム続行)
        self.forbidden = set()                        # 禁じ手の座標を保存
        pyxel.run(self.update, self.draw)            # 更新と描画の開始

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.winner is not None:
            return  # 勝敗が決まった後は操作を無効化

        # マウス左クリック時にクリック位置を取得
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            x, y = pyxel.mouse_x, pyxel.mouse_y

            # クリック位置を盤面のマスにスナップ
            col = (x - 10) // 16
            row = (y - 10) // 16

            # 盤外クリックを無視
            if col < 0 or col >= 15 or row < 0 or row >= 15:
                return

            # 禁じ手のマスを無視（黒のターンのみ）
            if self.turn and (row, col) in self.forbidden:
                return

            # 既に石が置かれている場合も無視
            if self.board[row][col] != 0:
                return

            # 石を仮配置して禁じ手をチェック（黒のターンのみ）
            self.board[row][col] = 1 if self.turn else 2
            if self.turn and self.is_forbidden(row, col):
                self.board[row][col] = 0  # 禁じ手の場合は元に戻す
                self.forbidden.add((row, col))  # 禁じ手として登録
                return

            # 後手（白）が禁じ手の位置に石を置いた場合、禁じ手を解除
            if not self.turn and (row, col) in self.forbidden:
                self.forbidden.remove((row, col))

            # 勝敗判定
            if self.check_winner(row, col):
                self.winner = "Black" if self.turn else "White"

            # ターンを交代
            self.turn = not self.turn

    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(0, 0, 0, 0, 0, 256, 256)  # 背景タイルマップを描画

        # 盤面を描画
        for row in range(15):
            for col in range(15):
                x = 10 + col * 16
                y = 10 + row * 16
                if self.board[row][col] == 1:  # 黒の石
                    pyxel.blt(x, y, 0, 0, 16, 16, 16, 9)
                elif self.board[row][col] == 2:  # 白の石
                    pyxel.blt(x, y, 0, 16, 16, 16, 16, 9)

        # 禁じ手のマスを描画
        for row, col in self.forbidden:
            x = 10 + col * 16
            y = 10 + row * 16
            pyxel.blt(x, y, 0, 0, 32, 16, 16, 9)

        # 勝者がいる場合、中央に勝利メッセージを表示
        if self.winner is not None:
            pyxel.text(100, 120, f"{self.winner} Win!!", pyxel.frame_count % 16)

    def is_forbidden(self, row, col):
        """禁じ手の判定"""
        if self.is_double_three(row, col) or self.is_double_four(row, col) or self.is_overline(row, col):
            return True
        return False

    def is_double_three(self, row, col):
        """三三の判定"""
        return self.count_open_sequences(row, col, 3) >= 2

    def is_double_four(self, row, col):
        """四四の判定"""
        return self.count_open_sequences(row, col, 4) >= 2

    def is_overline(self, row, col):
        """長連の判定"""
        return self.count_in_line(row, col) >= 6

    def count_open_sequences(self, row, col, length):
        """指定された長さの両端が空いている連の数をカウント"""
        stone = self.board[row][col]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        count = 0

        for dr, dc in directions:
            seq_count = 1
            open_ends = 0

            # 正方向にカウント
            r, c = row + dr, col + dc
            while 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == stone:
                seq_count += 1
                r += dr
                c += dc
            if 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == 0:
                open_ends += 1

            # 逆方向にカウント
            r, c = row - dr, col - dc
            while 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == stone:
                seq_count += 1
                r -= dr
                c -= dc
            if 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == 0:
                open_ends += 1

            # 両端が空いている場合のみカウント
            if seq_count == length and open_ends == 2:
                count += 1

        return count

    def count_in_line(self, row, col):
        """一列に並んだ石の数をカウント"""
        stone = self.board[row][col]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        max_count = 0

        for dr, dc in directions:
            seq_count = 1

            # 正方向にカウント
            r, c = row + dr, col + dc
            while 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == stone:
                seq_count += 1
                r += dr
                c += dc

            # 逆方向にカウント
            r, c = row - dr, col - dc
            while 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == stone:
                seq_count += 1
                r -= dr
                c -= dc

            max_count = max(max_count, seq_count)

        return max_count

    def check_winner(self, row, col):
        """勝敗判定 (縦・横・斜めに5つ並んだかを確認)"""
        return self.count_in_line(row, col) >= 5

App()

# cd game_env
# .\.venv\Scripts\activate
# cd ..\games\mine\Quantum_gomoku
# pyxel edit sprite
# python main.py