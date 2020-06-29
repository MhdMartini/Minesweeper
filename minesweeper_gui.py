from tkinter import *
import time
from PIL import Image, ImageTk
import threading
from minesweeper import *


class MineSweeperGui:
    # Main GUI class
    FONT = "Courier"
    FONT_SIZE = 12
    BUTTON_COLOR = "darkgray"
    MOUSE_1 = '<Button-1>'
    MOUSE_2 = '<Button-3>'
    switcher = {
        # Choose a number's color based on its value
        "0": "snow",
        "1": "blue",
        "2": "green",
        "3": "red",
        "4": "darkviolet",
        "5": "maroon",
        "6": "turquoise",
        "7": "black",
        "8": "black"
    }

    def __init__(self, master, minesweeper_grid):
        self.master = master
        self.master.resizable(width=False, height=False)
        self.GAME = False

        self.minesweeper_grid = minesweeper_grid                    # Making the grid a global attribute
        self.side_length = minesweeper_grid.side_length             # Side length of grid
        self.flags_count = len(self.minesweeper_grid.mine_tiles)    # mine_count - number of flags
        self.mine_count = len(self.minesweeper_grid.mine_tiles)     # Total number of mines in grid

        # Define images
        self.mine = ImageTk.PhotoImage(Image.open('mine.png'))
        self.clicked_mine = ImageTk.PhotoImage(Image.open('b_mine.png'))
        self.flag = ImageTk.PhotoImage(Image.open('flag.png'))
        self.question_mark = ImageTk.PhotoImage(Image.open('q.png'))
        self.neutral = ImageTk.PhotoImage(Image.open("neutral.png"))
        self.happy = ImageTk.PhotoImage(Image.open("happy.png"))
        self.sad = ImageTk.PhotoImage(Image.open("sad.png"))

        # Fill menu bar
        self.fill_menu_bar()

        # Create and pack frames
        self.main_frame = Frame(self.master, bg="snow")     # Grid frame
        self.main_frame.pack()
        self.status_frame = Frame(self.master, bg="snow")   # Status frame above the grid
        self.fill_status_frame()

        # create buttons
        self.buttons = self.create_buttons()

        # Initialize the grid:
        # Randomly choose one of the empty clusters and flip its tiles
        cluster_count = len(self.minesweeper_grid.empty_tile_clusters)
        rand = random.choice(range(cluster_count))
        chosen_cluster = f"cluster{rand}"
        for empty_tile in self.minesweeper_grid.empty_tile_clusters[chosen_cluster]:
            self.flip_number(empty_tile)
            # All neighbors of an empty tile do not have a mine in them
            empty_neighbors_ = self.minesweeper_grid.neighbors(empty_tile)
            for neighbor in empty_neighbors_:
                self.flip_number(neighbor)
        self.GAME = True

        # Start timer
        self.ctr = threading.Thread(target=self.counter)
        self.ctr.setDaemon(True)
        self.ctr.start()

    def fill_menu_bar(self):
        menu_bar = Menu(self.master)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Beginner", command=lambda: self.reset("Beginner"))
        file_menu.add_command(label="Intermediate", command=lambda: self.reset("Intermediate"))
        file_menu.add_command(label="Expert", command=lambda: self.reset("Expert"))
        file_menu.add_command(label="Boss", command=lambda: self.reset("Boss"))

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        self.master.config(menu=menu_bar)

    def fill_status_frame(self):
        # create and configure widgets
        self.counter_entry = Label(self.main_frame,
                                   bg="snow", fg="red", text=str(self.mine_count).zfill(3))
        self.counter_entry.config(font=(self.FONT, 20, "bold"))

        self.emoji_label = Label(self.main_frame,
                                 bg="snow", image=self.neutral, cursor="exchange")

        self.time_entry = Label(self.main_frame,
                                bg="snow", fg="black", text='000')
        self.time_entry.config(font=(self.FONT, 20, "bold"))

        # Bind pressing the emoji label to restarting the game
        self.binder(widget=self.emoji_label, event_=self.MOUSE_1, function=self.reset, argument=self.side_length)

        # Grid widgets
        self.counter_entry.grid(row=0, column=0, columnspan=3,
                                ipady=4, ipadx=2, sticky=W)
        self.emoji_label.grid(row=0, column=self.side_length // 2 - 2, columnspan=4)
        self.time_entry.grid(row=0, column=self.side_length - 3, columnspan=3,
                             ipady=4, ipadx=2, sticky=E)

        self.status_frame.pack()

    def create_buttons(self):
        # Create buttons dictionary from tile dictionary, e.g.
        # {"tile,0,0" : <Button object>, "tile,0,1" : <Button object>, etc.}
        buttons = {}
        self.tiles = self.minesweeper_grid.tiles
        for tile_name, tile in self.tiles.items():
            # Create
            buttons[tile_name] = Button(self.main_frame, text=" ", fg=self.BUTTON_COLOR, bg=self.BUTTON_COLOR)
            buttons[tile_name].config(font=(self.FONT, self.FONT_SIZE, "bold"))
            buttons[tile_name].mine = tile.mine  # copy the mine attribute

            # Bind buttons: mouse1: display tile; mouse2: toggle between flag, "?" mark, and normal state
            self.binder(widget=buttons[tile_name], event_=self.MOUSE_1, function=self.display, argument=tile_name)
            self.binder(widget=buttons[tile_name], event_=self.MOUSE_2, function=self.toggle, argument=tile_name)

            # Grid buttons
            # Get coordinates from the tile name
            x, y = tile_name.split(',')[-2:]
            y = int(y) + 1  # To account for the status frame being in row 0
            buttons[tile_name].grid(row=y, column=x, ipadx=2)
            buttons[tile_name].visible = False
            buttons[tile_name].flag = False
            buttons[tile_name].question_mark = False
        return buttons

    def binder(self, widget, event_, function, argument):
        # Binds buttons to function with arguments
        def executor(event):
            function(argument)
        widget.bind(event_, executor)

    def display(self, tile_name):
        # Make a decision about what happens in the game based on the tile's value
        if self.buttons[tile_name].flag:
            # If button is flagged, don't display tile
            return
        if self.buttons[tile_name].mine:
            # End game if it's a mine
            self.end_game(tile_name)

        if repr(self.tiles[tile_name]) == "0":
            # if an empty tile is flipped,
            # all empty tiles and their neighbors flip as well, in the respective cluster
            # TODO: Consider making the flip number method take an iterative argument
            self.clusters = self.minesweeper_grid.empty_tile_clusters
            for _, cluster in self.clusters.items():
                if tile_name in cluster:
                    for empty_tile in cluster:
                        self.flip_number(empty_tile)
                        empty_neighbors_ = self.minesweeper_grid.neighbors(empty_tile)
                        for neighbor in empty_neighbors_:
                            self.flip_number(neighbor)
        else:
            self.flip_number(tile_name)

    def update_count(self, n):
        # Counts the number of flags used
        self.flags_count += n
        self.counter_entry['text'] = str(self.flags_count).zfill(3)
        if self.flags_count == 0:
            # If #flags = #mines, validate solution
            self.validate_grid()

    def validate_grid(self):
        check = True
        flipped_tiles_count = 0
        for tile_name, tile in self.minesweeper_grid.tiles.items():
            check = check and (tile.mine == self.buttons[tile_name].flag)
            if not check:
                return
            if self.buttons[tile_name].visible:
                flipped_tiles_count += 1
        if check and (
                flipped_tiles_count == (self.minesweeper_grid.tile_count - self.mine_count)):
            self.emoji_label.configure(image=self.happy)
            self.GAME = False

    def toggle(self, tile_name):
        # Change button image only if button is not flipped
        button = self.buttons[tile_name]
        if not button.visible:
            if not button['image']:
                button.configure(image=self.flag)
                button.flag, button.question_mark = (True, False)
                self.update_count(-1)
            elif button.flag:
                button.configure(image=self.question_mark)
                button.flag, button.question_mark = (False, True)
                self.update_count(1)
            elif button.question_mark:
                button.configure(image="")
                button.flag, button.question_mark = (False, False)

    def end_game(self, tile_name=None):
        original = tile_name
        for tile_name, tile in self.tiles.items():
            x, y = tile_name.split(',')[-2:]
            if tile.mine:
                self.flip_mine(tile_name)
            else:
                self.flip_number(tile_name)
        if original:
            self.flip_mine(original, clicked=True)

    def flip_mine(self, tile_name, clicked=False):
        # Display the value of a mine tile
        self.emoji_label.configure(image=self.sad)
        self.GAME = False

        if clicked:
            image = self.clicked_mine
        else:
            image = self.mine

        x, y = tile_name.split(',')[-2:]
        y = str(int(y) + 1)
        label = Label(self.main_frame, image=image, bg='snow')
        label.grid(row=y, column=x)

    def flip_number(self, tile_name):
        # Display the value of a regular  tile
        button = self.buttons[tile_name]
        if button.question_mark:
            button.configure(image="")
            button.flag, button.question_mark = (False, False)

        # If button is flagged but no mine underneath (only executes when game is over)
        if button.flag and not self.tiles[tile_name].mine:
            button.configure(image="")
            # button.flag, button.question_mark = (False, False)

        button_text = repr(self.tiles[tile_name])
        button.configure(bg="snow", text=button_text, disabledforeground=self.switcher[button_text],
                         state=DISABLED)
        button.config(font=(self.FONT, self.FONT_SIZE, "bold"))
        button.visible = True
        self.binder(widget=self.buttons[tile_name], event_=self.MOUSE_1, function=self.solve_neighbors,
                    argument=tile_name)
        if self.GAME:
            self.validate_grid()

    def solve_neighbors(self, tile_name):
        button = self.buttons[tile_name]
        neighbors = self.minesweeper_grid.neighbors(tile_name)
        flagged_neighbors = {neighbor for neighbor in neighbors if self.buttons[neighbor].flag}
        mine_neighbors = {neighbor for neighbor in neighbors if self.tiles[neighbor].mine}
        button_value = button['text']

        flipped_tiles = []
        if len(flagged_neighbors) == len(mine_neighbors):
            if flagged_neighbors == mine_neighbors:
                for neighbor in neighbors:
                    if (not self.buttons[neighbor].visible) and (not self.tiles[neighbor].mine):
                        self.flip_number(neighbor)
                        flipped_tiles.append(neighbor)
            else:
                self.end_game()

        for flipped_tile in flipped_tiles:
            if self.buttons[flipped_tile]['text'] == '0':
                self.clusters = self.minesweeper_grid.empty_tile_clusters
                for _, cluster in self.clusters.items():
                    if flipped_tile in cluster:
                        for empty_tile in cluster:
                            self.flip_number(empty_tile)
                            empty_neighbors_ = self.minesweeper_grid.neighbors(empty_tile)
                            for neighbor in empty_neighbors_:
                                self.flip_number(neighbor)

    def reset(self, level):
        switcher = {
            12: "Beginner",
            16: "Intermediate",
            25: "Expert",
            40: "Boss"
        }
        if type(level) == int:
            level = switcher[level].lower()
        self.master.destroy()
        main(level.lower())

    def counter(self    ):
        t = 0
        while True:
            if t == 999:
                break
            try:
                self.time_entry["text"] = str(t).zfill(3)
            except:
                pass
            time.sleep(1)
            if self.GAME:
                t += 1
                continue
            return t

def main(level):
    t = MineSweeper(level)
    root = Tk()
    # ctr.start()
    root.title('Minesweeper')
    MineSweeperGui(root, t)
    root.mainloop()


if __name__ == '__main__':
    main("Beginner")
