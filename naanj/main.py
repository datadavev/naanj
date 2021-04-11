"""
cli for naanj
"""
import sys
import click
import curses
import logging
import naanj
import threading

# used for progress display
log_lock = threading.Lock()

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "FATAL": logging.CRITICAL,
    "CRITICAL": logging.CRITICAL,
}

def getLogFormatter():
    return logging.Formatter(
        "%(asctime)-8s %(levelname)-6s: %(message)-s", "%H:%M:%S"
    )

class CursesHandler(logging.Handler):
    def __init__(self, screen):
        logging.Handler.__init__(self)
        self.screen = screen

    def emit(self, record):
        try:
            msg = self.format(record)
            screen = self.screen
            fs = "\n%s"
            screen.addstr(fs % msg)
            screen.refresh()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def setupLogWin(scr, logger, begin_y=0):
    formatterDisplay = getLogFormatter()
    maxy, maxx = scr.getmaxyx()
    tlx = 2
    height = 10
    width = maxx - 4
    logwin = curses.newwin(height, width, begin_y, tlx)
    logwin.refresh()
    logwin.scrollok(True)
    logwin.idlok(True)
    logwin.leaveok(True)
    lh = CursesHandler(logwin)
    lh.setFormatter(formatterDisplay)
    logger.addHandler(lh)


status_win = {"win": None, "height": 0, "width": 0}


def idx2yx(i):
    global status_win
    y = int(i / status_win["width"])
    x = i % status_win["width"]
    return (y, x)


def displayCallback(idx, state):
    global status_win
    with log_lock:
        chars = ["▒", "▓", "✔", "X"]
        attrs = [
            curses.color_pair(1),
            curses.color_pair(2),
            curses.color_pair(3),
            curses.color_pair(4),
        ]
        y, x = idx2yx(idx)
        c = chars[state]
        status_win["win"].addch(y, x, c, attrs[state])
        status_win["win"].refresh()


def statusProgress(stdscr, logger, naans):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    stdscr.bkgd(' ', curses.color_pair(0) | curses.A_BOLD)
    stdscr.clear()
    stdscr.refresh()
    setupLogWin(stdscr, logger, begin_y=11)

    global status_win
    maxy, maxx = stdscr.getmaxyx()
    begin_x = 2
    begin_y = 0
    width = maxx - 4
    if width > 76:
        width = 76
    height = int(len(naans.naa) / width) + 1
    status_win["height"] = height
    status_win["width"] = width
    status_win["win"] = curses.newwin(height, width, begin_y, begin_x)

    #Pause just a bit for screen prep
    stdscr.timeout(100)
    naans.checkSources(callback=displayCallback)
    logger.info("COMPLETE. Press a key or wait a bit to continue...")
    stdscr.timeout(5000)
    stdscr.getch()
    return naans


@click.command()
@click.option(
    "-n",
    "--naans",
    "naans_source",
    default=naanj.AUTHORITY_SOURCE,
    help="ANVL Source URL",
)
@click.option(
    "-p", "--progress", is_flag=True, help="Show progress when testing (implies -t)"
)
@click.option("-t", "--test", is_flag=True, help="Test URLs listed as location")
@click.option(
    "--verbosity", default="INFO", help="Specify logging level", show_default=True
)
@click.argument("destination", required=False)
def main(naans_source, progress, test, verbosity, destination=None):
    logger = logging.getLogger("naanj")
    logger.setLevel(LOG_LEVELS.get(verbosity.upper(), logging.INFO))
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(getLogFormatter())
    naans = naanj.Naans()
    naans.load(src=naans_source)
    if progress:
        if sys.stdout.isatty():
            test = False
            naans = curses.wrapper(statusProgress, logger, naans)
        else:
            logger.addHandler(c_handler)
            logger.warning("Progress requested but not on a TTY")
            test = True
    else:
        logger.addHandler(c_handler)
    if test:
        naans.checkSources()
    if destination is None:
        print(naans.asJson())
    else:
        with open(destination, "wt", encoding="utf-8") as outf:
            outf.write(naans.asJson())
    return 0


if __name__ == "__main__":
    sys.exit(main())
