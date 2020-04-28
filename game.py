from copy import deepcopy as cpy


dx = [-1, -1, -1, 0, 0, 1, 1, 1]
dy = [-1, 0, 1, -1, 1, -1, 0, 1]


class Game:
    NR_ROW = 8
    NR_COL = 8

    P_MAX = "1"
    P_MIN = "2"
    EMPTY = "#"

    LEVEL = 1  # 1, 2, or 3

    ALGORITHM = 0  # 0 for mini max, 1 for alpha-beta

    def __init__(self):
        pass


class Drawer:
    def __init__(self, game_state):
        self.game_state = game_state

    def console_print(self):
        pass


class GameState:
    def __init__(self, current_player=Game.P_MAX, grid=None):
        self.current_player = current_player

        if grid is None:
            self.grid = [[Game.EMPTY for i in range(Game.NR_COL)] for i in range(Game.NR_ROW)]
            self.grid[3][3] = self.grid[4][4] = Game.P_MAX
            self.grid[3][4] = self.grid[4][3] = Game.P_MIN
        else:
            self.grid = grid

    def opponent(self):
        if self.current_player == Game.P_MAX:
            return Game.P_MIN
        else:
            return Game.P_MAX

    def switch_player(self):
        self.current_player = self.opponent()

    def valid_move(self, x, y):
        if self.grid[x][y] != Game.EMPTY:
            return False, []

        flag = False
        opponent_disks = []
        for k in range(8):
            cnt = 0
            i = x
            j = y
            current_flag = False
            lst = []
            while True:
                i += dx[k]
                j += dy[k]

                if i < 0 or j < 0 or i >= Game.NR_ROW or j >= Game.NR_COL:
                    break

                if self.grid[i][j] == Game.EMPTY:
                    break

                if self.grid[i][j] == self.current_player and cnt == 0:
                    break

                if self.grid[i][j] == self.opponent():
                    cnt += 1
                    lst.append([i, j])
                    continue

                if self.grid[i][j] == self.current_player:
                    current_flag = True
                    break

            if current_flag is True:
                flag = True
                opponent_disks.extend(lst)

        return flag, opponent_disks

    def generate_new_state(self, lst):
        grid = cpy(self.grid)
        for el in lst:
            grid[el[0]][el[1]] = self.current_player

        new_state = GameState(self.opponent(), grid)
        return new_state

    def is_final_state(self):
        pass

    def generate_new_states(self):
        new_states = []

        for i in range(Game.NR_ROW):
            for j in range(Game.NR_COL):
                flag, lst = self.valid_move(i, j)
                if flag is False:
                    continue

                new_states.append(self.generate_new_state(lst))

        return new_states


if __name__ == '__main__':
    pass
