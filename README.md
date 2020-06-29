# WHAT I LEARNED IN THIS PROJECT:
1- Building GUIs with tkinter
  - Buttons, labels, option menus

2- Threading

3- OS directory operations

4- Writing and reading Json files

# Game Features:
1- Four different levels:
  - beginner: 12x12
  - intermediate: 16x16
  - expert: 25x25
  - boss: 40x40
  
2- Left-mouse click on emoji icon restart the game it its current level.

3- File option menu allows for choosing game level
  
4- Game begins with an open cluster to minimize luck on first try.

5- Right-mouse click on a button toggles the button from normal mode to flagged mode to question-mark mode.

6- Flagged buttons are unpressable, but question-marked buttons are not. 

7- Left-mouse click on an open button opens the non-mine buttons around it only if the neighboring mines of the open button are correctly satisfied. 
  - If the neghboring mines are not correctly satisfied, game ends. 
  - If number of flagged buttons around a clicked open button are less than the open button's value, nothing happens.
  
8- Number of mines is shown in the top-left corner; time elapsed is shown in the top-right corner.

9- When player wins, elapsed time is stopped and saved in in a Json file in the user directory under a "Minesweeper" folder.
  
10- If player achieves a new score, the output Json file is updated accordingly, and the player gets notified of their new score, in addition to the time differnce between their old score and new score.
