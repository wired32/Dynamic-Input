import msvcrt
from time import time as timestamp
from typing import Callable, Optional
from threading import Thread
from packets import CompletionPacket, InputConfigsPacket
from sys import stdout

class DynamicInput:
    def __init__(self):
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

    def _hideCursor(self):
        """Hides the cursor in the console."""
        stdout.write("\033[?25l")
        stdout.flush()

    def _showCursor(self):
        """Shows the cursor in the console."""
        stdout.write("\033[?25h")
        stdout.flush()

    def complete(self, s: CompletionPacket) -> None:
        """
        Displays the autocompletion suggestion on the console.

        Args:
            s (CompletionPacket): The packet containing the completion string to display.
        """
        if len(self.buffer) > s.bufferlenght:
            return  # If the buffer length has changed, abort to avoid glitches.

        from rich import print
        stdout.write("\033[s")  # Save cursor position
        stdout.write("\033[K")  # Clear the line
        stdout.flush()

        self._hideCursor()  # Hide cursor for smoother changes

        # Print the completion content using rich colors
        print(f"[{s.shade}]{s.content}", end='', flush=True)

        stdout.write("\033[u")  # Restore cursor position
        stdout.flush()

        self._showCursor()  # Show the cursor again

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
            self.complete(self.completion)
        self.fetchInProgress = False

    def input(self, prompt: str = None, call_to: Optional[Callable[[str], str]] = None, end: str = '\n',
              allow_empty_input: bool = True, shade: str = 'grey30', time_buffer: float = 0.5,
              indent: int = 4, config_bind: str = None, raw_call: bool = False, output_bind: bool = True) -> str:
        """
        Receives input from the user, supporting autocompletion and key handlers.

        Args:
            prompt (str, optional): The string prompt shown to the user before input.
            call_to (Callable[[str], str], optional): The function to call for the autocompletion logic.
            end (str, optional): The character to print after the input. Default is newline.
            allow_empty_input (bool, optional): If False, prevents submitting an empty input. Default is True.
            shade (str, optional): The color shade for autocompletion. Uses rich color codes. Default is 'grey30'.
            time_buffer (float, optional): Time in seconds before fetching autocompletion after typing. Default is 0.5 seconds.
            indent (int, optional): The number of spaces inserted for indentation when no completion is available.
            config_bind (str, optional): A keybind for triggering the autocompletion logic on certain keys.
            raw_call (bool, optional): If True, the call_to function is triggered immediately without autocompletion display. Default is False.
            output_bind (bool, optional): If True, the bound key is shown in the output buffer. Default is True.

        Returns:
            str: The final input string after the user presses enter.
        """
        from rich import print

        ts = timestamp()
        called = False
        self.exit = False # Reset the exit flag
        self.buffer = []

        # Ensure a single character is bound if config_bind is provided
        if config_bind is not None and len(config_bind) > 1:
            raise KeyError("config_bind must be a single character.")

        if call_to is None:
            raise ValueError("Please provide a call_to function for autocompletion.")

        # Display the prompt
        if prompt is not None:
            print(prompt, end='', flush=True)

        while True:
            cts = timestamp()

            # Check if enough time has passed for autocompletion
            if cts - ts > time_buffer and called and config_bind is None:
                if raw_call:
                    Thread(target=call_to, args=(''.join(self.buffer),)).start()
                else:
                    Thread(target=self._process_completion, args=(self.buffer, shade, call_to)).start()
                called = False

            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8')

                # Handle key bound to config_bind
                if key == config_bind and not raw_call:
                    if output_bind:
                        self.buffer.append(key)
                        print(key, end='', flush=True)

                    Thread(target=self._process_completion, args=(self.buffer, shade, call_to)).start()
                    ts = cts
                    continue
                elif key == config_bind and raw_call:
                    if output_bind:
                        self.buffer.append(key)
                        print(key, end='', flush=True)
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

        return ''.join(self.buffer)

    def _handle_enter(self, args: InputConfigsPacket):
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

    def _handle_backspace(self, args: InputConfigsPacket):
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

    def _handle_tab(self, args: InputConfigsPacket):
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
        else:
            print(" " * args.indent, end='', flush=True)  # Insert spaces if no completion
        return False

    def _handle_regular(self, args: InputConfigsPacket):
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
