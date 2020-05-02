from argparse import ArgumentParser
from copy import deepcopy as cpy
from timeit import default_timer as timer
import pygame
import time

dx = [-1, -1, -1, 0, 0, 1, 1, 1]
dy = [-1, 0, 1, -1, 1, -1, 0, 1]


class Game:
    NR_ROW = 8
    NR_COL = 8

    P_MAX = 1
    P_MIN = 2
    EMPTY = 0

    LEVEL = 1

    ALGORITHM = 0  # 0 for mini max, 1 for alpha-beta

    MIN_SCORE = -101
    MAX_SCORE = 101

    def __init__(self):
        pass


class Drawer:
    CELL_WIDTH = 70
    CELL_HEIGHT = 70
    CIRCLE_RADIUS = 30

    BLUE = (102, 153, 255)
    RED = (255, 102, 102)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (200, 220, 200)

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('REVERSI GAME')
        self.X_Min = 0
        self.X_Max = Game.NR_COL * Drawer.CELL_WIDTH - 1
        self.Y_Min = 0
        self.Y_Max = Game.NR_ROW * Drawer.CELL_HEIGHT - 1
        self.screen = pygame.display.set_mode(size=(self.X_Max + 1, self.Y_Max + 1))
        self.clear_screen()

    def clear_screen(self):
        self.screen.fill(Drawer.WHITE)
        pygame.display.update()

    def console_print(self, game_state):
        print()
        print("Player", game_state.current_player)
        print()
        print("", end=" ")
        for i in range(Game.NR_COL):
            print("|", i, end="")
        print()
        for idx, line in enumerate(game_state.grid):
            print(idx, line)

        print()

    def draw_circle(self, color, center):
        pygame.draw.circle(self.screen, color, center, Drawer.CIRCLE_RADIUS)

    def draw_line(self, color, a, b, width):
        pygame.draw.line(self.screen, color, a, b, width)

    def draw(self, game_state):
        self.screen.fill(Drawer.WHITE)

        for i in range(Game.NR_ROW):
            for j in range(Game.NR_COL):
                if game_state.grid[i][j] == Game.P_MAX:
                    self.draw_circle(Drawer.BLUE, (j * Drawer.CELL_WIDTH + Drawer.CELL_WIDTH // 2, i * Drawer.CELL_HEIGHT + Drawer.CELL_HEIGHT // 2))
                elif game_state.grid[i][j] == Game.P_MIN:
                    self.draw_circle(Drawer.RED, (j * Drawer.CELL_WIDTH + Drawer.CELL_WIDTH // 2, i * Drawer.CELL_HEIGHT + Drawer.CELL_HEIGHT // 2))

        # valid moves
        for i in range(Game.NR_ROW):
            for j in range(Game.NR_COL):
                fl, _ = game_state.valid_move(i, j, game_state.current_player)
                if fl is True:
                    self.draw_circle(Drawer.GREY, (j * Drawer.CELL_WIDTH + Drawer.CELL_WIDTH // 2, i * Drawer.CELL_HEIGHT + Drawer.CELL_HEIGHT // 2))

        for i in range(Game.NR_COL):
            self.draw_line(Drawer.BLACK, (i * Drawer.CELL_WIDTH, 0), (i * Drawer.CELL_WIDTH, self.Y_Max), 3)

        for i in range(Game.NR_ROW):
            self.draw_line(Drawer.BLACK, (0, i * Drawer.CELL_HEIGHT), (self.X_Max, i * Drawer.CELL_HEIGHT), 3)

        pygame.display.update()


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

    def opponent_player(self, player):
        if player == Game.P_MAX:
            return Game.P_MIN
        else:
            return Game.P_MAX

    def switch_player(self):
        self.current_player = self.opponent()

    def valid_move(self, x, y, player):
        if x < 0 or y < 0 or x >= Game.NR_ROW or y >= Game.NR_COL:
            return False, []

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

                if self.grid[i][j] == player and len(lst) == 0:
                    break

                if self.grid[i][j] == self.opponent_player(player):
                    lst.append([i, j])
                    continue

                if self.grid[i][j] == player:
                    current_flag = True
                    break

            if current_flag is True:
                flag = True
                opponent_disks.extend(lst)

        return flag, opponent_disks

    def count_moves(self, player):
        cnt = 0
        for i in range(Game.NR_ROW):
            for j in range(Game.NR_COL):
                flag, _ = self.valid_move(i, j, player)
                if flag is True:
                    cnt += 1

        return cnt

    def can_advance(self):
        for i in range(Game.NR_ROW):
            for j in range(Game.NR_COL):
                flag, _ = self.valid_move(i, j, self.current_player)

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
                flag, lst = self.valid_move(i, j, self.current_player)
                if flag is False:
                    continue

                new_states.append(self.generate_new_state(lst))

        return new_states

    def make_move(self, x, y):
        fl, lst = self.valid_move(x, y, self.current_player)
        if fl is False:
            return False, self

        return True, self.generate_new_state(lst)

    # calculates score for Game.P_MAX
    def get_score(self):
        return self.get_score_1()

    def get_score_1(self):
        p_max_score = 0
        p_min_score = 0
        for i in range(Game.NR_ROW):
            for j in range(Game.NR_COL):
                if self.grid[i][j] == Game.P_MAX:
                    if (i == 0 or i == Game.NR_ROW - 1) and (j == 0 or j == Game.NR_COL - 1):
                        p_max_score += 4  # grid corner
                    elif i == 0 or i == Game.NR_ROW - 1 or j == 0 or j == Game.NR_COL - 1:
                        p_max_score += 2  # grid side
                    else:
                        p_max_score += 1  # any other cell
                elif self.grid[i][j] == Game.P_MIN:
                    if (i == 0 or i == Game.NR_ROW - 1) and (j == 0 or j == Game.NR_COL - 1):
                        p_min_score += 4  # grid corner
                    elif i == 0 or i == Game.NR_ROW - 1 or j == 0 or j == Game.NR_COL - 1:
                        p_min_score += 2  # grid side
                    else:
                        p_min_score += 1  # any other cell

        return 100 * (p_max_score - p_min_score) / (p_max_score + p_min_score)

    def get_score_2(self):
        return 0.4 * self.get_parity_score() + 0.3 * self.get_corners_score() + 0.3 * self.get_mobility_score()

    # between -100 and 100
    def get_parity_score(self):
        p_max_occ = self.count_occurrence(Game.P_MAX)
        p_min_occ = self.count_occurrence(Game.P_MIN)
        return 100 * (p_max_occ - p_min_occ) / (p_max_occ + p_min_occ)

    # between -100 and 100
    def get_mobility_score(self):
        p_max_mobility = self.count_moves(Game.P_MAX)
        p_min_mobility = self.count_moves(Game.P_MIN)
        if (p_max_mobility + p_min_mobility) > 0:
            return 100 * (p_max_mobility - p_min_mobility) / (p_max_mobility + p_min_mobility)
        else:
            return 0

    # between -100 and 100
    def get_corners_score(self):
        p_max_corners_cnt = 0
        p_min_corners_cnt = 0
        for i in range(Game.NR_ROW):
            for j in range(Game.NR_COL):
                if (i == 0 or i == Game.NR_ROW - 1) and (j == 0 or j == Game.NR_COL - 1):
                    if self.grid[i][j] == Game.P_MAX:
                        p_max_corners_cnt += 1
                    else:
                        p_min_corners_cnt += 1

        if (p_max_corners_cnt + p_min_corners_cnt) > 0:
            return 100 * (p_max_corners_cnt - p_min_corners_cnt) / (p_max_corners_cnt + p_min_corners_cnt)
        else:
            return 0

    def count_occurrence(self, ch):
        return sum([line.count(ch) for line in self.grid])

    def get_winner(self):
        if self.is_final_state() is False:
            return None

        player_1_score = self.count_occurrence(Game.P_MAX)
        player_2_score = self.count_occurrence(Game.P_MIN)

        if player_1_score > player_2_score:
            return Game.P_MAX
        elif player_2_score > player_1_score:
            return Game.P_MIN
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


class Engine:
    def __init__(self, player=0):
        self.game_state = GameState()
        self.drawer = Drawer()
        self.AI = AI()
        self.player = player

    def get_grid_coordinates(self, mouse_coord):
        x = mouse_coord[0] // self.drawer.CELL_WIDTH
        y = mouse_coord[1] // self.drawer.CELL_HEIGHT

        return y, x

    def game_menu(self):
        nr = 1
        while True:
            try:
                nr = int(input("Algorithm type:\n  1) Press 1 for mini-max.\n  2) Press 2 for alpha_beta.\n"))
                if nr != 1 and nr != 2:
                    print("Invalid algorithm choice. Please try again.")
                    continue
            except Exception as e:
                print("Bad input format ({}). Please try again.".format(e))
                continue
            break
        Game.ALGORITHM = nr - 1

        while True:
            try:
                nr = int(input("Choose your color.\n  1) Press 1 for blue (you move first).\n  2) Press 2 for blue (AI moves first).\n"))
                if nr != 1 and nr != 2:
                    print("Invalid color choice. Please try again.")
                    continue
            except Exception as e:
                print("Bad input format ({}). Please try again.".format(e))
                continue
            break
        self.player = nr
        turn = self.player - 1

        while True:
            try:
                nr = int(input("Choose your difficulty level\n  1) Press 1 for easy.\n  2) Press 2 for medium.\n  3) Press 3 for difficult.\n"))
                if nr != 1 and nr != 2 and nr != 3:
                    print("Invalid difficulty choice. Please try again.")
                    continue
            except Exception as e:
                print("Bad input format ({}). Please try again.".format(e))
                continue
            break
        Game.LEVEL = nr + 1

        return turn

    def run_with_gui(self):
        game_start_time = timer()
        turn = self.game_menu()
        your_moves_cnt = 0
        ai_moves_cnt = 0

        game_over = False
        while not game_over:
            # self.drawer.console_print(self.game_state)
            self.drawer.draw(self.game_state)

            if self.game_state.is_final_state():
                game_over = True
                continue

            if turn == 0:
                move_start_time = timer()
                print("Your turn.")
                made_move = False
                while not made_move:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            print("You did {} moves".format(your_moves_cnt))
                            print("AI did {} moves".format(ai_moves_cnt))
                            your_score = self.game_state.count_occurrence(self.player)
                            ai_score = self.game_state.count_occurrence(self.game_state.opponent_player(self.player))
                            print("Your score is {}.".format(your_score))
                            print("AI's score is {}.\n".format(ai_score))
                            print("Game total time was {} seconds.\n".format(timer() - game_start_time))
                            print("You quited game.\nBye.\n")
                            return
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_coord = pygame.mouse.get_pos()
                            x, y = self.get_grid_coordinates(mouse_coord)
                            # print(x, y)

                            fl, self.game_state = self.game_state.make_move(x, y)
                            if fl is False:
                                print("Invalid move. Please try again\n")
                                continue

                            made_move = True
                            turn = 1 - turn
                            your_moves_cnt += 1
                            print("Your think time was {} seconds.\n".format(timer() - move_start_time))
                            break
            else:
                print("AI's turn.")
                time.sleep(0.5)
                move_start_time = timer()
                _, self.game_state = self.AI.make_move(self.game_state)
                ai_moves_cnt += 1
                turn = 1 - turn
                print("AI's think time was {} seconds.\n".format(timer() - move_start_time))
            pass

        print("Game over.")
        print("You did {} moves".format(your_moves_cnt))
        print("AI did {} moves".format(ai_moves_cnt))
        winner = self.game_state.get_winner()
        your_score = self.game_state.count_occurrence(self.player)
        ai_score = self.game_state.count_occurrence(self.game_state.opponent_player(self.player))

        if winner == "Tie":
            print("Game over.\nTie.\n")
        elif self.player == winner:
            print("You won with the score {}-{}.\n".format(your_score, ai_score))
        else:
            print("AI won with the score {}-{}.\n".format(ai_score, your_score))

        exit_game = False
        while not exit_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                    break

        pygame.quit()
        print("Game total time was {} seconds.\n".format(timer() - game_start_time))
        print("You quited game.\nBye.\n")

    def run(self):
        game_start_time = timer()
        turn = self.game_menu()
        your_moves_cnt = 0
        ai_moves_cnt = 0

        game_over = False
        while not game_over:
            self.drawer.console_print(self.game_state)

            if self.game_state.is_final_state():
                game_over = True
                continue

            if turn == 0:
                move_start_time = timer()
                print("Your turn.")
                made_move = False
                while not made_move:
                    line = input("Give i and j\n\n")
                    if line == "exit":
                        pygame.quit()
                        print("You did {} moves".format(your_moves_cnt))
                        print("AI did {} moves".format(ai_moves_cnt))
                        your_score = self.game_state.count_occurrence(self.player)
                        ai_score = self.game_state.count_occurrence(self.game_state.opponent_player(self.player))
                        print("Your score is {}.".format(your_score))
                        print("AI's score is {}.\n".format(ai_score))
                        print("Game total time was {} seconds.\n".format(timer() - game_start_time))
                        print("You quited game.\nBye.\n")
                        return

                    try:
                        x, y = map(int, line.split(' '))
                    except Exception as e:
                        print("invalid input format, please try again")
                        continue

                    # print(x, y)

                    fl, self.game_state = self.game_state.make_move(x, y)
                    if fl is False:
                        print("Invalid move. Please try again\n")
                        continue

                    made_move = True
                    turn = 1 - turn
                    your_moves_cnt += 1
                    print("Your think time was {} seconds.\n".format(timer() - move_start_time))
            else:
                print("AI's turn.")
                time.sleep(0.5)
                move_start_time = timer()
                _, self.game_state = self.AI.make_move(self.game_state)
                ai_moves_cnt += 1
                turn = 1 - turn
                print("AI's think time was {} seconds.\n".format(timer() - move_start_time))
            pass

        print("Game over.")
        print("You did {} moves".format(your_moves_cnt))
        print("AI did {} moves".format(ai_moves_cnt))
        winner = self.game_state.get_winner()
        your_score = self.game_state.count_occurrence(self.player)
        ai_score = self.game_state.count_occurrence(self.game_state.opponent_player(self.player))

        if winner == "Tie":
            print("Game over.\nTie.\n")
        elif self.player == winner:
            print("You won with the score {}-{}.\n".format(your_score, ai_score))
        else:
            print("AI won with the score {}-{}.\n".format(ai_score, your_score))

        pygame.quit()
        print("Game total time was {} seconds.\n".format(timer() - game_start_time))
        print("You quited game.\nBye.\n")


if __name__ == '__main__':
    parser = ArgumentParser(usage=__file__ + ' '
                                             '--gui GUI',
                            description='Reversi game')

    parser.add_argument('--gui',
                        dest='gui',
                        default='0',
                        help='Flag for gui usage')

    # Parse arguments
    args = vars(parser.parse_args())
    gui = args['gui']

    game_engine = Engine()

    if gui == '1':
        game_engine.run_with_gui()
    else:
        game_engine.run()

    pass
