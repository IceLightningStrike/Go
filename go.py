from __future__ import annotations
from itertools import product
from copy import deepcopy


def near_heap_of_stones(board: list, player: str, i: int, j: int) -> tuple:
    queue = [(i, j)]

    dots_near_me = set()
    only_my_color = {(i, j)}

    while queue:
        dot = queue.pop(0)

        for delta_i, delta_j in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
            new_dot = dot[0] + delta_i, dot[1] + delta_j

            if not (0 <= new_dot[0] < len(board) and 0 <= new_dot[1] < len(board[0])):
                continue
            
            if new_dot in dots_near_me | only_my_color:
                continue

            if board[new_dot[0]][new_dot[1]] == player:
                queue.append(new_dot)
                only_my_color.add(new_dot)
            else:
                dots_near_me.add(new_dot)
    
    return dots_near_me, only_my_color


class Go:
    def __init__(self: Go, *size: int) -> None:
        if len(size) == 1:
            self.height, self.width = size[0], size[0]
        else:
            self.height, self.width = size[0], size[1]
        
        if self.height > 25 or self.width > 25:
            raise Exception
        
        self.size = {'height': self.height, 'width': self.width}
        self.board = [["."] * self.width for _ in range(self.height)]
        self.global_boards_history = [deepcopy(self.board)]

        self.alphabet = "ABCDEFGHJKLMNOPQRSTUVWXYZ"

        self.move_change_dict = {"x": "o", "o": "x"}
        self.current_move = "x"

        self.turn_change_dict = {"black": "white", "white": "black"}
        self.turn = "black"

        self.handicap_placed = False

    def get_position(self: Go, pos: str) -> str:
        line, column = -int(pos[:-1]), self.alphabet.find(pos[-1])

        try:
            assert (1 <= -line <= self.height) and (0 <= column < self.width)
        except AssertionError:
            raise Exception
        
        return self.board[line][column]
    
    def rollback(self, n: int) -> None:
        self.global_boards_history = self.global_boards_history[:-n]
        self.board = deepcopy(self.global_boards_history[-1])

        if n % 2 == 1:
            self.current_move = self.move_change_dict[self.current_move]
            self.turn = self.turn_change_dict[self.turn]
    
    def move(self: Go, *player_moves: str) -> None:
        self.handicap_placed = True

        for player_move in player_moves:
            self.single_move(player_move)
    
    def single_move(self: Go, player_move: str) -> None:
        board, current_move = deepcopy(self.board), self.current_move
        line, column = -int(player_move[:-1]), self.alphabet.find(player_move[-1])

        try:
            assert (1 <= -line <= self.height) and (0 <= column < self.width)
            assert board[line][column] == '.'
            board[line][column] = current_move
            current_move = self.move_change_dict[current_move]
        except AssertionError:
            raise Exception("Incorrect coordinates!")

        if board in self.global_boards_history:
            raise Exception("This field has already been!")

        killing = False

        for i, j in product(range(self.size["height"]), range(self.size["width"])):
            if board[i][j] == current_move:
                ans = near_heap_of_stones(board, current_move, i, j)

                if all(map(lambda dot: board[dot[0]][dot[1]] == self.current_move, ans[0])):
                    killing = True

                    for dot in ans[1]:
                        board[dot[0]][dot[1]] = "."
        
        if killing is True:
            if board in self.global_boards_history:
                raise Exception("This field has already been!")
            
            self.board, self.current_move = deepcopy(board), current_move
            self.turn = self.turn_change_dict[self.turn]
            self.global_boards_history.append(deepcopy(self.board))
            return
        
        for i, j in product(range(self.size["height"]), range(self.size["width"])):
            if board[i][j] == self.move_change_dict[current_move]:
                ans = near_heap_of_stones(board, self.move_change_dict[current_move], i, j)
                if all(map(lambda dot: board[dot[0]][dot[1]] == current_move, ans[0])):
                    raise Exception("You can't make a suicidal move!")

        if board in self.global_boards_history:
            raise Exception("This field has already been!")
        
        self.board, self.current_move = deepcopy(board), current_move
        self.turn = self.turn_change_dict[self.turn]
        self.global_boards_history.append(deepcopy(self.board))

    def pass_turn(self: Go) -> None:
        self.global_boards_history.append(self.board)
        self.turn = self.turn_change_dict[self.turn]
        self.current_move = self.move_change_dict[self.current_move]

    def handicap_stones(self: Go, n: int) -> None:
        if (self.width, self.height) not in handicap_sizes:
            raise Exception("Size of current field is incorrect for handicap stones!")

        max_handicap_stones = len(handicap_sequence[handicap_sizes.index((self.width, self.height)) + 1])
        if not (1 <= n <= max_handicap_stones):
            raise Exception(
                f"You can't put more than {max_handicap_stones} handicap stones on this field"
            )
        
        if len(self.global_boards_history) > 1:
            raise Exception("You have already done another move!")
        
        if self.handicap_placed is True:
            raise Exception("You have already laid the stones!")
        
        self.handicap_placed = True

        for i, j in handicap_sequence[handicap_sizes.index((self.width, self.height)) + 1][:n]:
            self.board[i][j] = self.current_move

    def is_end(self) -> bool:
        return False
    
    def reset(self: Go) -> None:
        self.board = [["."] * self.width for _ in range(self.height)]
        self.global_boards_history = [deepcopy(self.board)]

        self.alphabet = "ABCDEFGHJKLMNOPQRSTUVWXYZ"

        self.move_change_dict = {"x": "o", "o": "x"}
        self.current_move = "x"

        self.turn_change_dict = {"black": "white", "white": "black"}
        self.turn = "black"

        self.handicap_placed = False


handicap_sizes = [(9, 9), (13, 13), (19, 19)]
handicap_sequence = {
    1: [(2, 6), (6, 2), (6, 6), (2, 2), (4, 4)],
    2: [(3, 9), (9, 3), (9, 9), (3, 3), (6, 6), (6, 3), (6, 9), (3, 6), (9, 6)],
    3: [(3, 15), (15, 3), (15, 15), (3, 3), (9, 9), (9, 3), (9, 15), (3, 9), (15, 9)]
}
