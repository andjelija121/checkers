import pygame
from constants import ROWS, COLS, SQUARE_SIZE, BROWN, BEIGE, WHITE, BLACK, GREEN
from piece import Piece


class Board:
    def __init__(self):
        self.board = []
        self.selected_piece = None
        self.create_board()

    def draw_squares(self, win):
        win.fill(BEIGE)

        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    pygame.draw.rect(
                        win,
                        BROWN,
                        (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                    )

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])

            for col in range(COLS):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row].append(Piece(row, col, BLACK))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, WHITE))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)

    def draw(self, win):
        self.draw_squares(win)

        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece is not None:
                    piece.draw(win)

    def get_piece(self, row, col):
        return self.board[row][col]

    def move_piece(self, piece, row, col):
        self.board[piece.row][piece.col] = None
        self.board[row][col] = piece

        piece.row = row
        piece.col = col

        if row == 0 or row == ROWS - 1:
            piece.make_king()

    def select(self, row, col):
        piece = self.get_piece(row, col)

        if piece is not None:
            self.selected_piece = piece
            return True

        if self.selected_piece is not None:
            self.move_piece(self.selected_piece, row, col)
            self.selected_piece = None
            return True

        return False