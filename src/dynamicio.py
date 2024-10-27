"""A module that adds flexibility to user input."""

import msvcrt
from time import time as timestamp
from typing import Callable, Optional
from threading import Thread
from .packets import CompletionPacket, InputConfigsPacket, SnapshotCache
from sys import stdout

from .utils.cursor import _hideCursor, _showCursor

class DynamicInput:
    """A class that adds flexibility to user input"""
    def __init__(self) -> None:
        """
        Initializes the DynamicInput class.

        Attributes:
            completion (CompletionPacket): The packet containing the completion string and its metadata.
            exit (bool): A flag that indicates whether the user has pressed enter to end input.
            fetchInProgress (bool): A flag that indicates whether a fetch for completion is in progress.
            handlers (dict): A dictionary that maps keys (like tab or enter) to their handler methods.
        """
        self.completion = CompletionPacket('', '', 0)  # Initialize with an empty packet
        self.exit = False
        self.fetchInProgress = False

        # Key handlers for tab, enter, and backspace
        self.handlers = {
            '\t': self._handle_tab,
            '\r': self._handle_enter,
            '\b': self._handle_backspace
        }

    def _hideCursor(self) -> None:
        """Hides the cursor in the console."""
        _hideCursor()

    def _showCursor(self) -> None:
        """Shows the cursor in the console."""
        _showCursor()

    def _process_completion(self, buffer: list, shade: str, call_to: Optional[Callable[[str], str]] = None) -> None:
        """
        Processes the autocompletion in a separate thread.

        Args:
            buffer (list): The characters typed so far.
            shade (str): The color shade for displaying the completion.
            call_to (Optional[Callable[[str], str]], optional): The function to call to get the completion string.
        """
        if self.fetchInProgress:
            return
        self.fetchInProgress = True

        # Get the completion from the callable
        self.completion = CompletionPacket(call_to(''.join(buffer)), shade, len(buffer))

        if not self.exit:
            from .utils.completer import complete
            complete(self.completion, self.buffer)
        self.fetchInProgress = False

    def input(self, prompt: str = None, call_to: Optional[Callable[[str], str]] = None, end: str = '\n',
              allow_empty_input: bool = True, shade: str = 'grey30',
              indent: int = 4, config_bind: str = None, autocomplete: bool = False, 
              output_bind: bool = True,
              inactivity_trigger: bool = True, monitor_delay: int = None) -> str:
        
        if monitor_delay is not None:
            import time

        ts = timestamp()
        called = False
        self.exit = False # Reset the exit flag
        delay_buffer = [] # Initialize delay buffer
        self.buffer = []  # Initialize input buffer
        time_buffer = 0

        # Ensure a single character is bound if config_bind is provided
        if config_bind is not None and len(config_bind) > 1:
            raise KeyError("config_bind must be a single character.")

        # Display the prompt
        if prompt is not None:
            print(prompt, end='', flush=True)
        

        while True:
            cts = timestamp()
            difference = cts - ts

            if len(delay_buffer) > 5 and called and call_to is not None and inactivity_trigger and difference > time_buffer:
                time_buffer = sum(delay_buffer) / len(delay_buffer) # Get average delay

                if autocomplete:
                    Thread(target=self._process_completion, args=(self.buffer, shade, call_to)).start()
                else:
                    Thread(target=call_to, args=(''.join(self.buffer),)).start()
                called = False

            if msvcrt.kbhit():
                delay_buffer.append(difference) # Add delay to buffer
                try: 
                    key = msvcrt.getch().decode('utf-8')
                except UnicodeDecodeError: 
                    try: 
                        key = msvcrt.getwch()
                    except:
                        continue

                # Handle key bound to config_bind
                if key == config_bind and autocomplete and call_to is not None:
                    if output_bind:
                        self.buffer.append(key)
                        print(key, end='', flush=True)

                    Thread(target=self._process_completion, args=(self.buffer, shade, call_to)).start()
                    ts = cts
                    continue
                elif key == config_bind and not autocomplete and call_to is not None:
                    if output_bind:
                        print(key, end='', flush=True)
                        self.buffer.append(key)
                    Thread(target=call_to, args=(''.join(self.buffer),)).start()
                    ts = cts
                    continue

                # Handle special keys like enter, tab, or backspace
                if key in self.handlers:
                    handler = self.handlers.get(key)
                    response = handler(InputConfigsPacket(buffer=self.buffer, indent=indent, end=end,
                                                          allow_empty_input=allow_empty_input, key=key))
                    if response == 'EXIT':
                        break
                    elif response == 'CONTINUE':
                        continue
                    called = response
                else:
                    called = self._handle_regular(InputConfigsPacket(key=key))

                ts = cts

            if monitor_delay is not None:
                time.sleep(monitor_delay)

        return ''.join(self.buffer)

    def _handle_enter(self, args: InputConfigsPacket) -> str:
        """
        Handles the enter key press to finalize the input.

        Args:
            args (InputConfigsPacket): The input configuration packet.

        Returns:
            str: 'EXIT' to signal input completion, 'CONTINUE' if input should continue.
        """
        if not args.allow_empty_input and not self.buffer:
            return 'CONTINUE'  # Prevent empty submission if not allowed
        self.exit = True

        stdout.write("\033[K")  # Clear completion
        stdout.flush()

        print(end=args.end)
        return 'EXIT'

    def _handle_backspace(self, args: InputConfigsPacket = None) -> bool:
        """
        Handles the backspace key to remove the last character in the input.

        Args:
            args (InputConfigsPacket): The input configuration packet.

        Returns:
            bool: True if the buffer changed, otherwise False.
        """
        if self.buffer:
            stdout.write('\x1b[D\x1b[P')  # Move cursor back and delete the character
            stdout.flush()
            self.buffer.pop()  # Remove the last character from the buffer
            return True

    def _handle_tab(self, args: InputConfigsPacket) -> bool:
        """
        Handles the tab key for autocompletion or inserts spaces if no completion is available.

        Args:
            args (InputConfigsPacket): The input configuration packet.

        Returns:
            bool: False to continue input.
        """
        if self.completion.content:
            print(self.completion.content, end='', flush=True)  # Show the completion
            self.buffer.extend(self.completion.content)  # Append the completion to the buffer
            self.completion.content = ''
        else:
            print(" " * args.indent, end='', flush=True)  # Insert spaces if no completion
        return False

    def _handle_regular(self, args: InputConfigsPacket) -> bool:
        """
        Handles regular alphanumeric characters during input.

        Args:
            args (InputConfigsPacket): The input configuration packet.

        Returns:
            bool: True if the input changed.
        """
        self.buffer.append(args.key)
        print(f"{args.key}", end='', flush=True)
        return True

    def get_cursor_position(self):
        """
        Retrieves the current cursor position in the console.

        Returns:
            tuple: A tuple containing the current row and column of the cursor.
        """
        # Use ctypes to access Windows API for cursor position
        import ctypes
        from ctypes import wintypes

        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
            _fields_ = [
                ("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", ctypes.c_short),
                ("srWindow", wintypes.RECT),
                ("dwMaximumWindowSize", COORD),
            ]

        kernel32 = ctypes.windll.kernel32
        hConsole = kernel32.GetStdHandle(-11)  # -11 = STD_OUTPUT_HANDLE

        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        kernel32.GetConsoleScreenBufferInfo(hConsole, ctypes.byref(csbi))

        # Get cursor position from the structure
        cursor_x = csbi.dwCursorPosition.X
        cursor_y = csbi.dwCursorPosition.Y

        # In Windows, cursor position is 0-based.
        return (cursor_y + 1, cursor_x + 1)    # Convert to 1-based indexing
    
    def snapshot(self) -> SnapshotCache:
        cache = SnapshotCache(self.get_cursor_position())

        return cache

    def _edit(self, returnRange: int, text: str, cache: SnapshotCache) -> None:
        """
        Edits a portion of the current input buffer and replaces it with new text.

        Args:
            returnRange (int): The number of characters to move back and edit.
            text (str): The new text to insert into the buffer.
        """
        self._hideCursor()

        x, y = cache.coords
        stdout.write(f"\033[{x};{y}H") # Move cursor to saved position
        stdout.flush()

        stdout.write(f"\x1b[{returnRange}D\x1b[K")  # Move back and clear
        stdout.flush()

        self.buffer = self.buffer[returnRange:]  # Remove characters from buffer

        print(text, end='', flush=True)
        self.buffer += list(text)  # Append new text to buffer

        self._showCursor()

    def edit(self, returnRange: int, new_text: str, cache: SnapshotCache) -> None:
        """
        Public method to trigger the edit operation.

        Args:
            returnRange (int): The number of characters to move back.
            new_text (str): The text to replace the existing input with.

        Raises:
            ValueError: If new_text is empty.
        """
        if not new_text:
            raise ValueError("Cannot edit with an empty string.")

        Thread(target=self._edit, args=(returnRange, new_text, cache)).start()

def input(prompt: str = None, call_to: Optional[Callable[[str], str]] = None, end: str = '\n', raw_call: bool = False, inactivity_trigger: bool = True) -> str:
    """
    A simple wrapper around DynamicInput.input() to provide a more Pythonic experience.

    Args:
        prompt (str, optional): The string prompt shown to the user before input.
        call_to (Callable[[str], str], optional): The function to call after a trigger.
        end (str, optional): The character to print after the input. Default is newline.
        raw_call (bool, optional): If True, the call logic is triggered immediately without autocompletion display. Default is False.

    Returns:
        str: The final input string after the user presses enter.
    """
    return DynamicInput().input(prompt, call_to, end=end, raw_call=raw_call, inactivity_trigger=inactivity_trigger)
