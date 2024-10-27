from src.packets import CompletionPacket
from sys import stdout
from .cursor import _hideCursor, _showCursor

def complete(s: CompletionPacket, buffer: list) -> None:
    """
    Displays the autocompletion suggestion on the console.

    Args:
        s (CompletionPacket): The packet containing the completion string to display.
    """
    if len(buffer) > s.bufferlenght:
        return  # If the buffer length has changed, abort to avoid glitches.

    stdout.write("\033[s")  # Save cursor position
    stdout.write("\033[K")  # Clear the line
    stdout.flush()

    _hideCursor()  # Hide cursor for smoother changes

    # Print the completion content using rich colors
    from rich import print
    print(f"[{s.shade}]{s.content}[/]", end='')

    stdout.write("\033[u")  # Restore cursor position
    stdout.flush()

    _showCursor()  # Show the cursor again