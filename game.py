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

    MIN_SCORE = 0 - 1
    MAX_SCORE = 8 * 8 + 4 * 8 + 4 + 1

    def __init__(self):
        pass


class Drawer:
    def __init__(self, game_state):
        self.game_state = game_state

    def console_print(self):
        for line in self.game_state.grid:
            print(line)

        print()


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
        opponent_disks = [[x, y]]
        for k in range(8):
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

                if self.grid[i][j] == self.current_player and len(lst) == 0:
                    break

                if self.grid[i][j] == self.opponent():
                    lst.append([i, j])
                    continue

                if self.grid[i][j] == self.current_player:
                    current_flag = True
                    break

            if current_flag is True:
                flag = True
                opponent_disks.extend(lst)

        return flag, opponent_disks

    def can_advance(self):
        for i in range(Game.NR_ROW):
            for j in range(Game.NR_COL):
                flag, _ = self.valid_move(i, j)

                if flag is True:
                    return True

        return False

    def is_final_state(self):
        return not self.can_advance()

    def generate_new_state(self, lst):
        grid = cpy(self.grid)
        for el in lst:
            grid[el[0]][el[1]] = self.current_player

        new_state = GameState(self.opponent(), grid)
        return new_state

    def generate_new_states(self):
        new_states = []

        for i in range(Game.NR_ROW):
            for j in range(Game.NR_COL):
                flag, lst = self.valid_move(i, j)
                if flag is False:
                    continue

                new_states.append(self.generate_new_state(lst))

        return new_states

    # calculates score for Game.P_MAX
    def get_score(self):
        score = 0
        for i in range(Game.NR_ROW):
            for j in range(Game.NR_COL):
                if self.grid[i][j] == Game.P_MAX:
                    if (i == 0 or i == Game.NR_ROW - 1) and (j == 0 or j == Game.NR_COL - 1):
                        score += 4  # grid corner
                    elif i == 0 or i == Game.NR_ROW - 1 or j == 0 or j == Game.NR_COL - 1:
                        score += 2  # grid side
                    else:
                        score += 1  # any other cell

        return score

    def count_occurrence(self, ch):
        return sum([line.count(ch) for line in self.grid])

    def get_winner(self):
        if self.is_final_state() is False:
            return None

        player_1_score = self.count_occurrence(Game.P_MAX)
        player_2_score = self.count_occurrence(Game.P_MIN)

        if player_1_score > player_2_score:
            return "Player 1"
        elif player_2_score > player_1_score:
            return "Player 2"
        elif player_1_score == player_2_score:
            return "Tie"

        return None


class AI:
    def __init__(self):
        pass

    def mini_max(self, game_state, depth):
        if depth == 0 or game_state.is_final_state() is True:
            return game_state.get_score(), game_state

        if game_state.current_player == Game.P_MAX:  # we maximize score
            score = Game.MIN_SCORE
            new_states = game_state.generate_new_states()
            for new_state in new_states:
                new_score, _ = self.mini_max(new_state, depth - 1)
                if new_score > score:
                    score = new_score
                    game_state = new_state
        else:  # we minimize score
            score = Game.MAX_SCORE
            new_states = game_state.generate_new_states()
            for new_state in new_states:
                new_score, _ = self.mini_max(new_state, depth - 1)
                if new_score < score:
                    score = new_score
                    game_state = new_state

        return score, game_state

    def alpha_beta(self, game_state, depth, alpha, beta):
        if depth == 0 or game_state.is_final_state():
            return game_state.get_score(), game_state

        if game_state.current_player == Game.P_MAX:  # we maximize score
            score = Game.MIN_SCORE
            new_states = game_state.generate_new_states()
            for new_state in new_states:
                new_score, _ = self.alpha_beta(new_state, depth - 1, alpha, beta)
                if new_score > score:
                    score = new_score
                    game_state = new_state
                alpha = max(alpha, new_score)
                if alpha >= beta:
                    break
        else:  # we minimize score
            score = Game.MAX_SCORE
            new_states = game_state.generate_new_states()
            for new_state in new_states:
                new_score, _ = self.alpha_beta(new_state, depth - 1, alpha, beta)
                if new_score < score:
                    score = new_score
                    game_state = new_state
                beta = min(beta, new_score)
                if alpha >= beta:
                    break

        return score, game_state

    def make_move(self, game_state):
        if Game.ALGORITHM == 0:
            return self.mini_max(game_state, Game.LEVEL)
        elif Game.ALGORITHM == 1:
            return self.alpha_beta(game_state, Game.LEVEL, Game.MIN_SCORE, Game.MAX_SCORE)
        else:
            raise Exception('unknown algorithm')


if __name__ == '__main__':
    # asd = GameState()
    # sc, st = AI().make_move(asd)
    # Drawer(st).console_print()
    pass
