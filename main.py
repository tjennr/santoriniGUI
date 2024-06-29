import sys
from gui import SantoriniGUI

if __name__ == '__main__':
    if len(sys.argv) < 1 or len(sys.argv) > 5:
        print("Usage: python main.py [argv1] [argv2] [argv3] [argv4]")
        sys.exit(1)

    # Set default values
    playerWhite = 'human'
    playerBlue = 'human'
    memento = False
    score_display = False

    # Parse command-line arguments
    if len(sys.argv) >= 2:
        if sys.argv[1] in ['human', 'random', 'heuristic']:
            playerWhite = sys.argv[1]

    if len(sys.argv) >= 3:
        if sys.argv[2] in ['human', 'random', 'heuristic']:
            playerBlue = sys.argv[2]

    if len(sys.argv) >= 4:
        if sys.argv[3] == 'on':
            memento = True

    if len(sys.argv) >= 5:
        if sys.argv[4] == 'on':
            score_display = True

    # Run the game
    SantoriniGUI(playerWhite, playerBlue, memento, score_display)