# ................................................Imports...............................................................

from copy import deepcopy
import tkinter as tk
import csv
from collections import Counter
import pprint
import time

# .............................................Global Variables.........................................................

side_cell = 50  # dimension of cell
boundary_margin = 20  # margin pixels around the board
frame_width = frame_height = boundary_margin * 2 + side_cell * 9  # dimensions of frame
file = ""  # input file name
st_board = []  # to maintain an unaltered copy of initial values from input file
st_board2 = []
iterations = 0
# ......................................................................................................................


class custom_error(Exception):  # generate custom exception messages while reading from input file
    pass


# ......................................................................................................................


class Sudoku_mainclass(object):

    def __init__(self, board_file):  # constructor
        self.board_file = board_file
        self.initial_board = self.__read_values(board_file)
        global st_board
        global st_board2
        st_board = deepcopy(self.initial_board)
        st_board2 = deepcopy(self.initial_board)
        self.game_start()

    # ..................................................................................................................

    def __read_values(self, board_file):  # take input from file

        board = []
        for line in csv.reader(boards_file, delimiter=','):
            if len(line) != 9:
                raise custom_error(
                    "Lines in the input file should be 9 character long."
                )
            board.append([])

            for x in line:
                if not x.isdigit():
                    raise custom_error(
                        "Invalid characters in input file. Only 0-9 allowed."
                    )
                board[-1].append(int(x))

        if len(board) != 9:
            raise custom_error("There should be 9 lines in the input file.")
        return board

    # ..................................................................................................................

    def check_for_duplicates(self, l):
        cou = Counter()
        for c in l:
            if c != 0:
                cou[c] += 1
            if c > 9 or cou[c] > 1:
                return False
        return True

    # ..................................................................................................................

    def check_valid_sudoku(self, board):
        if len(board) != 9:
            return False
        if sum(len(r) == 9 for r in board) != 9:
            return False
        for r in board:
            if not self.check_for_duplicates(r):
                return False
        return True

    # ................................Main solving algo begins from here................................................

    def search_nextblock(self, sudoku_board, m, n):
        for p in range(m, 9):
            for q in range(n, 9):
                if sudoku_board[p][q] == 0:
                    return p, q
        for p in range(9):
            for q in range(9):
                if sudoku_board[p][q] == 0:
                    return p, q
        return -1, -1

    # ..................................................................................................................

    def check_ifvalid(self, sudoku_board, m, n, z):
        row_valid = all([z != sudoku_board[m][X_cord] for X_cord in range(0,9)])  # if all of them are true
        if row_valid:
            column_valid = all([z != sudoku_board[X_cord][n] for X_cord in range(0,9)])  # if all of them are true
            if column_valid: # search for the X_cord, Y_cord co-ordinates the area that has the the m,n block
                Area_X, Area_Y = 3 * (m // 3), 3 * (n // 3)
                for X_cord in range(Area_X, Area_X + 3):
                    for Y_cord in range(Area_Y, Area_Y + 3):
                        if sudoku_board[X_cord][Y_cord] == z:
                            return False
                return True
        return False

    # ..................................................................................................................

    def Sudoku_solver_backtracking(self, sudoku_board, m=0, n=0):
        m, n = self.search_nextblock(sudoku_board, m, n)
        if m == -1:
            return True
        for z in range(1, 10):
            if self.check_ifvalid(sudoku_board, m, n, z):
                sudoku_board[m][n] = z
                if self.Sudoku_solver_backtracking(sudoku_board, m, n):
                    return True
                sudoku_board[m][n] = 0  # Revert the current block
        return False

    # ..................................................................................................................

    def game_start(self):
        self.BOARD = []
        for p in range(0, 9):
            self.BOARD.append([])
            for q in range(0, 9):
                self.BOARD[p].append(self.initial_board[p][q])
        self.game_flag = False

    # ..................................................................................................................

    def change(self, board):  # put the set of possible values
        current = deepcopy(board)
        for i in range(0, 9):
            for q in range(0, 9):
                block = current[i][q]
                if block == 0:
                    current[i][q] = set(range(1, 10))

        return current


# ......................................................................................................................


class Sudoku_GUIclass(tk.Frame):

    def __init__(self, parent_master, sudoku_game):  # constructor
        self.sudoku_game = sudoku_game
        tk.Frame.__init__(self, parent_master)
        self.parent_master = parent_master
        self.config(bg="gray27")
        self.r, self.c = -1, -1
        self.__buildGUI()

    # ..................................................................................................................

    def __buildGUI(self):
        self.parent_master.title("Sudoku Solver")
        self.pack(fill=tk.BOTH)
        self.canv = tk.Canvas(self,
                              width=frame_width,
                              height=frame_height, background="#F0DB4F")
        self.canv.pack(fill=tk.BOTH, side=tk.TOP)
        reset_button = tk.Button(self,
                                 text="Reset Board", font=("Sabo", 16, "bold"),
                                 command=self.__reset_board, activebackground="aquamarine", background="orange red",
                                 foreground="white")
        reset_button.pack(side=tk.LEFT, expand=True)

        solve_button = tk.Button(self,
                                 text="Solve Sudoku", font=("Sabo", 16, "bold"),
                                 command=self.__solve_board, activebackground="aquamarine", background="orange red",
                                 foreground="white")
        solve_button.pack(side=tk.RIGHT, expand=True)

        self.__draw_lines()
        self.__draw_numbers()

        self.canv.bind("<Button-1>", self.__block_click)
        self.canv.bind("<Key>", self.__keyboard_press)

    # ..................................................................................................................

    def __solve_board(self):
        if not self.sudoku_game.check_valid_sudoku(self.sudoku_game.BOARD):
            self.__show_message("No Solution")
            #print("No solution")
        else:
            current = self.sudoku_game.change(self.sudoku_game.BOARD)
            t = time.time()
            result = self.sudoku_game.Sudoku_solver_backtracking(self.sudoku_game.BOARD)
            print("Solving time = " + str(time.time()-t) + " seconds")
            #print("\nNumber of iterations = " + str(iterations))

            if not result:
                self.__show_message("No Solution")
            else:
                self.canv.delete("values")
                #print(self.sudoku_game.BOARD)
                for p in range(0, 9):   # initial values
                    for q in range(0, 9):
                        value = st_board[p][q]
                        if value != 0:
                            x = boundary_margin + q * side_cell + side_cell / 2
                            y = boundary_margin + p * side_cell + side_cell / 2
                            color = "#000000"
                            self.canv.create_text(
                                x, y, text=value, font=("Arial", 16, "bold"), tags="values", fill=color
                            )

                for i in range(0, 9):
                    for q in range(0, 9):
                        if st_board[i][q] == 0:
                            ele = self.sudoku_game.BOARD[i][q]
                            x = boundary_margin + q * side_cell + side_cell / 2
                            y = boundary_margin + i * side_cell + side_cell / 2
                            original = self.sudoku_game.initial_board[i][q]
                            color = "#1F262A" if ele == original else "#E10F7C"
                            self.parent_master.after(80, self.animate(x, y, ele, color))

                self.__show_message("Sudoku Solved!")
                # print(result)

    def animate(self, x, y, ele, color):
        self.canv.create_text(
            x, y, text=ele, font=("Arial", 16), tags="values", fill=color
        )
        self.canv.update()

    # ..................................................................................................................

    def __draw_lines(self):  # make the game board lines
        for p in range(10):
            colour = "green" if p % 3 == 0 else "alice blue"

            X1 = boundary_margin + p * side_cell
            Y1 = boundary_margin
            X2 = boundary_margin + p * side_cell
            Y2 = frame_height - boundary_margin
            self.canv.create_line(X1, Y1, X2, Y2, fill=colour)

            X1 = boundary_margin
            Y1 = boundary_margin + p * side_cell
            X2 = frame_width - boundary_margin
            Y2 = boundary_margin + p * side_cell
            self.canv.create_line(X1, Y1, X2, Y2, fill=colour)

    # ..................................................................................................................

    def __draw_numbers(self):  # draw numbers on the canvas
        self.canv.delete("values")
        for p in range(0, 9):
            for q in range(0, 9):
                value = self.sudoku_game.BOARD[p][q]
                if value != 0:
                    x = boundary_margin + q * side_cell + side_cell / 2
                    y = boundary_margin + p * side_cell + side_cell / 2
                    org_value = self.sudoku_game.initial_board[p][q]
                    color = "#000000" if value == org_value else "#41B883"
                    self.canv.create_text(
                        x, y, text=value, font=("Arial", 16, "bold"), tags="values", fill=color
                    )

    # ..................................................................................................................

    def __reset_board(self):  # reset the board to the initial values taken from the input file
        self.sudoku_game.game_start()
        self.sudoku_game.initial_board = st_board
        self.__draw_numbers()

    # ..................................................................................................................

    def __block_click(self, event):  # when a block on the game grid is clicked
        if self.sudoku_game.game_flag:
            return
        x, y = event.x, event.y  # x and y coordinates of click
        if (boundary_margin < x < frame_width - boundary_margin and
                boundary_margin < y < frame_height - boundary_margin):
            self.canv.focus_set()  # set focus on canvas

            # use the coordinates from event to calculate the block indexes
            r, c = int((y - boundary_margin) / side_cell), int((x - boundary_margin) / side_cell)

            # deselect the cell if it was pre-selected
            if (r, c) == (self.r, self.c):
                self.r, self.c = -1, -1
            elif self.sudoku_game.BOARD[r][c] == 0:
                self.r, self.c = r, c

        self.__draw_block_boundary()

    # ..................................................................................................................

    def __draw_block_boundary(self):  # highlights the particular block that the user has clicked on
        self.canv.delete("block_boundary")
        if self.r >= 0 and self.c >= 0:
            X1 = boundary_margin + self.c * side_cell + 1
            Y1 = boundary_margin + self.r * side_cell + 1
            X2 = boundary_margin + (self.c + 1) * side_cell - 1
            Y2 = boundary_margin + (self.r + 1) * side_cell - 1
            self.canv.create_rectangle(
                X1, Y1, X2, Y2,
                outline="blue", tags="block_boundary"
            )

    # ..................................................................................................................

    def __keyboard_press(self, event):
        if self.sudoku_game.game_flag:
            return
        if self.r >= 0 and self.c >= 0 and event.char in "1234567890":  # only digits pressed will be shown
            self.sudoku_game.BOARD[self.r][self.c] = int(event.char)  # update BOARD
            self.c, self.r = -1, -1
            self.__draw_numbers()
            self.__draw_block_boundary()  # remove boundary around block

    # ..................................................................................................................

    def __show_message(self, msg):
        tl = tk.Toplevel()
        tl.geometry("400x200+400+200")
        tl.wm_attributes('-topmost', True)  # window to stay above all other windows
        lb = tk.Label(tl, text=msg, font=('Arial', 16))
        lb.pack(fill='both', expand=True)
        tl.lift()  # window to stay above all other application windows
        tl.wait_window()  # waits until the given window is destroyed


# ......................................................................................................................

def get_input():  # to select which file to take input from
    tl = tk.Toplevel()
    tl.geometry("400x200+500+200")
    tl.config(background="#FFF15A")
    tl.title("Input")
    tl.wm_attributes('-topmost', True)  # window to stay above all other windows

    lb = tk.Label(tl, text="Select input file", font=('Arial', 16, "bold"), background="#FFF15A")
    lb.grid(row=0, column=1, sticky=tk.NSEW)
    p1 = tk.StringVar()
    p1.set("sudoku.csv")  # default radiobutton selected
    p1_rb1 = tk.Radiobutton(tl, text='sudoku.csv', variable=p1, value="sudoku.csv", background="#FFF15A")
    p1_rb1.grid(row=1, column=2, sticky=tk.W)
    p1_rb2 = tk.Radiobutton(tl, text='sudoku_empty.csv', variable=p1, value="sudoku_empty.csv", background="#FFF15A")
    p1_rb2.grid(row=2, column=2, sticky=tk.W)
    ok = tk.Button(tl, text='Ok', font=('Arial', 15),
                   command=tl.destroy, background="#DAF4FE")
    # using partial function to be able to pass argument to driver
    ok.grid(row=3, column=2, columnspan=3, sticky=tk.S, pady=10)
    tl.lift()  # window to stay above all other application windows
    tl.wait_window()  # waits until the given window is destroyed
    global file
    file = p1.get()
    return p1.get()


with open(get_input(), 'r') as boards_file:
    sudoku_game = Sudoku_mainclass(boards_file)
    root = tk.Tk()
    Sudoku_GUIclass(root, sudoku_game)
    root.geometry("%dx%d+%d+%d" % (frame_width, frame_height + 40, 550, 150))
    root.mainloop()

# ......................................................................................................................

