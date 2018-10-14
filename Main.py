import curses, operator, os

# https://docs.python.org/3/howto/curses.html
# https://docs.python.org/3/library/curses.html
# https://www.ibm.com/developerworks/library/l-python6/

VERSION = 0.4
ALPHABET = "abcdefghijklmnopqrstuvwxyz"

players = {}
# chr: bool (AVAILABLE)
alphabet = {}
word = ""
progress = 0
penalties = 0


def main():
    print("Welcome to hangman!\n"
          "To leave, use ctrl-c\n\n"
          "Please enter all players' names, pressing enter after each.\n"
          "You don't need to enter the leader's name.")

    while True:
        n = input("Enter a name or nothing when finished: ")
        if n == "":
            if len(players) == 0:
                print("There must be at least one player.")
                continue
            break
        elif n in players:
            print("That player already exists!")
            continue
        else:
            players[n] = 0

    global word
    while True:
        word = input("\nEnter a word for players to guess: ")
        if not word_ok(word):
            print(f"That word is invalid: {word}.")
        else:
            break

    curses.wrapper(start_game)
    # Game's over now

    os.system('cls' if os.name == 'nt' else 'clear')  # sorry :c https://stackoverflow.com/a/2084628

    ordered = sorted(players.items(), key=operator.itemgetter(1), reverse=True)
    for p in ordered[:4] if len(ordered) >= 4 else ordered:
        print(f"{p.__getitem__(0)}: {p.__getitem__(1)} points")


def word_ok(s):
    if s == "":
        return False
    for c in s:
        if c not in ALPHABET:
            return False

    return True


# i_hate_snake_case___whoever_made_it_standard_was_insane
def start_game(scr):
    if not curses.has_colors():
        print("Oops, this game requires color support in your terminal.\n"
              "Please upgrade to play.")
        exit()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)

    # record that every letter is available
    for c in ALPHABET:
        alphabet[c] = True

    try:
        finished = 0
        while not finished:
            for p in players.keys():
                finished = move(scr, p)
                if finished:
                    break
    except TermBoundExceeded:
        print(f"Error: terminal is too small!\n\tPlease correct before continuing")

    scr.clear()
    scr.refresh()


def move(scr, p):
    global penalties, progress
    if penalties >= 7:
        return 1
    elif progress >= len(word):
        return 2

    draw(scr, p)

    c = ""

    # char is invalid or char was already picked
    while c not in alphabet or not alphabet[c]:
        c = chr(scr.getch())
    alphabet[c] = False

    exists = False
    for c_w in word:
        if c_w == c:
            progress += 1
            exists = True
    if exists:
        players[p] += 1
    else:
        players[p] -= 1
        penalties += 1

    return 0


def draw(scr, player):
    scr.clear()

    max_y, max_x = scr.getmaxyx()

    y, x = 0, 0
    for c in alphabet:
        addstr_boundcheck(scr, y, x, c, curses.color_pair(2) if not alphabet[c] else curses.color_pair(1))
        if y >= 13:
            y = 0
            x += 2

            # this is a dumb place to check but I don't see a better way
            if max_x <= x + 4:
                raise TermBoundExceeded
        else:
            y += 1

    # Make blue border for the alphabet list
    scr.vline(0, x + 2, '|', max_y, curses.color_pair(3))

    # Window title
    addstr_boundcheck(scr, 0, x + 6, f"Hangman v{VERSION}")

    addstr_boundcheck(scr, 2, x + 8, "-------")
    addstr_boundcheck(scr, 3, x + 8, "|     |")
    addstr_boundcheck(scr, 4, x + 8, "|")
    addstr_boundcheck(scr, 5, x + 8, "|")
    addstr_boundcheck(scr, 6, x + 8, "|")
    addstr_boundcheck(scr, 7, x + 8, "|")
    addstr_boundcheck(scr, 8, x + 8, "|")
    addstr_boundcheck(scr, 9, x + 6, "__|__")

    draw_penalty(scr, x + 14)

    p_ = []
    for c in word:
        p_.append(c if not alphabet[c] else '_')
        p_.append(' ')
    addstr_boundcheck(scr, 11, x + 6, "".join(p_))

    # Make blue border for input section
    scr.hline(13, x + 4, "-", max_x, curses.color_pair(3))

    addstr_boundcheck(scr, 14, x + 6, f"<{player}>  Input your guess! ", curses.color_pair(1))

    scr.refresh()


# param x is the hook on the pole's x coord
def draw_penalty(scr, x):
    # WHY IS THERE NO SWITCH STATEMENT IN PYTHON?!
    if penalties >= 1:
        addstr_boundcheck(scr, 4, x - 2, "('-')")
    if penalties >= 2:
        addstr_boundcheck(scr, 5, x, "|")
    if penalties >= 3:
        addstr_boundcheck(scr, 6, x - 1, "/|")
        addstr_boundcheck(scr, 4, x - 2, "(;-;)")
    if penalties >= 4:
        addstr_boundcheck(scr, 6, x + 1, "\\")
    if penalties >= 5:
        addstr_boundcheck(scr, 7, x, "|")
        addstr_boundcheck(scr, 4, x - 2, "(;n;)")
    if penalties >= 6:
        addstr_boundcheck(scr, 8, x - 1, "/")
        addstr_boundcheck(scr, 4, x - 2, "(x-x)")
    if penalties >= 7:
        addstr_boundcheck(scr, 8, x + 1, "\\")
        addstr_boundcheck(scr, 4, x - 2, "(:c)")


# Cause function overloading is too difficult for Python...
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~v
def addstr_boundcheck(scr, y, x, s, fmt=None):
    # Yes, I could pass in the bounds, but I'll take the
    # stupid performance hit over more parameters or some
    # more global variables
    max_y, max_x = scr.getmaxyx()
    if x + len(s) >= max_x or y > max_y:
        raise TermBoundExceeded

    scr.addstr(y, x, s, 0 if fmt is None else fmt)


class TermBoundExceeded(Exception):
    pass


try:
    main()
except KeyboardInterrupt:
    print("\n\nOk, ^Cya.")
