"""A module that adds flexibility to user input."""

import msvcrt
from time import time as timestamp
from typing import Callable, Optional
from threading import Thread
from .packets import CompletionPacket, InputConfigsPacket
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
                key = msvcrt.getch().decode('utf-8')

                # Handle key bound to config_bind
                if key == config_bind and autocomplete and call_to is not None:
                    if output_bind:
                        self.buffer.append(key)
                        print(key, end='', flush=True)

                    Thread(target=self._process_completion, args=(self.buffer, shade, call_to)).start()
                    ts = cts
                    continue
                elif key == config_bind and not autocomplete and call_to is None:
                    if output_bind:
                        self.buffer.append(key)
                        print(key, end='')
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
        import termios, tty
        from sys import stdin
        fd = stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(stdin.fileno())
            stdout.write("\033[6n")
            stdout.flush()

            response = ""
            while True:
                ch = stdin.read(1)
                response += ch
                if ch == "R":
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        # Extract the row and column from the response
        response = response.lstrip("\033[")
        rows, cols = map(int, response[:-1].split(";"))

        return rows, cols

    def _edit(self, returnRange: int, text: str):
        """
        Edits a portion of the current input buffer and replaces it with new text.

        Args:
            returnRange (int): The number of characters to move back and edit.
            text (str): The new text to insert into the buffer.
        """
        self._hideCursor()

        stdout.write(f"\x1b[{returnRange}D\x1b[K")  # Move back and clear
        stdout.flush()

        self.buffer = self.buffer[returnRange:]  # Remove characters from buffer

        print(text, end='', flush=True)
        self.buffer += list(text)  # Append new text to buffer

        self._showCursor()

    def edit(self, returnRange: int, new_text: str) -> None:
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

        Thread(target=self._edit, args=(returnRange, new_text)).start()

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
