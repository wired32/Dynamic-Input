from sys import stdout

def _hideCursor() -> None:
    """Hides the cursor in the console."""
    stdout.write("\033[?25l")
    stdout.flush()

def _showCursor() -> None:
    """Shows the cursor in the console."""
    stdout.write("\033[?25h")
    stdout.flush()