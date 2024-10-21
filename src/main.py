import msvcrt
from time import time as timestamp
from rich import print
from requests import post
from typing import Callable, Optional
from threading import Thread

class DynamicInput:
    def __init__(self):
        """
        Initializes the DynamicInput class.

        Attributes:
            completion (str): The completion string that is written to the console.
            bufferLen (int): The length of the current buffer.
            completionLen (int): The length of the completion string.
            exit (bool): A flag that indicates whether the user has pressed enter.
            fetchInProgress (bool): A flag that indicates whether a fetch for completion is in progress.
        """
        self.completion = ""
        self.bufferLen = 0
        self.completionLen = 0
        self.exit = False
        self.fetchInProgress = False

    def complete(self, s: str, shade: str) -> None:
        """Prints the completion string to the console with the given shade.

        Args:
            s (str): The completion string to display.
            shade (str): The shade string to style the completion output.
        """
        from sys import stdout
        stdout.write("\033[s")  # Save cursor position
        stdout.write("\033[K")  # Clear the line
        stdout.flush()
        
        print(f"[{shade}]{s}", end='', flush=True)  # Print completion

        stdout.write("\033[u")  # Restore cursor position
        stdout.flush()

    def _process_completion(self, buffer: list, shade: str, call_to: Optional[Callable[[str], str]] = None) -> None:
        """
        Processes the completion string in a separate thread.

        Args:
            buffer (list): The list of characters that have been typed so far.
            shade (str): The shade string for completion.
            call_to (Optional[Callable[[str], str]], optional): The function to call for getting the completion string. Defaults to None.
        """
        if self.fetchInProgress:
            return
        self.fetchInProgress = True

        self.bufferLen = len(buffer)
        self.completion = call_to(''.join(buffer))  # Call the function to get completion
        self.completionLen = len(self.completion)

        if not self.exit:
            self.complete(self.completion, shade)  # Display the completion
        self.fetchInProgress = False

    def input(self, prompt: str = None, call_to: Optional[Callable[[str], str]] = None, end: str = '\n',
              allow_empty_input: bool = True, shade: str = 'grey30', time_buffer: float = 0.5,
              indent: int = 4) -> str:
        """Gets a line of input from the user and returns the input string.

        The user can use the tab key for autocomplete predictions, backspace to delete characters,
        and enter to submit the input.

        Args:
            prompt (str): The prompt string to display before the input.
            end (str): The string to print after the input.
            allow_empty_input (bool): Flag to allow submitting an empty string.
            shade (str): The shade string for the completion output.
            time_buffer (float): Time in seconds to wait before fetching completion after the last character typed.
            call_to (Callable[[str], str]): The function to call for the prediction string.
            indent (int): The number of spaces added if no completion is available.

        Returns:
            str: The user input string.
        """
        ts = timestamp()
        called = False
        buffer = []

        if call_to is None:
            raise ValueError("Please provide a call_to function.")

        if prompt is not None:
            print(prompt, end='', flush=True)

        while True:
            cts = timestamp()
            if cts - ts > time_buffer and called:
                complete_thread = Thread(target=self._process_completion, args=(buffer, shade, call_to))
                complete_thread.start()
                called = False

            if msvcrt.kbhit():
                if not called:
                    called = True

                key = msvcrt.getwch()

                if key == '\b':  # Handle backspace
                    if buffer:
                        from sys import stdout
                        buffer.pop()
                        stdout.write('\x1b[D\x1b[P')  # Move cursor back and replace character
                        stdout.flush()
                elif key == '\r':  # Handle enter key
                    from sys import stdout
                    if not allow_empty_input and not buffer:
                        called = False
                        continue
                    self.exit = True
                    stdout.write("\033[K")  # Clear line
                    print(end=end)
                    break
                elif key == '\t':  # Handle tab key
                    if self.completion:
                        print(self.completion, end='')  # Show completion
                        called = False
                    else:
                        print(" " * indent, end='')  # Print spaces if no completion
                else:  # Handle regular character input
                    buffer.append(key)
                    print(f"{key}", end='', flush=True)
                    if len(buffer) - self.bufferLen > self.completionLen:
                        self.completion = ""  # Clear completion if new input exceeds previous

                ts = cts

        return ''.join(buffer)

if __name__ == "__main__":
    def call_to_example(s: str) -> str:
        """Example completion function that returns suggestions based on user input.

        Args:
            s (str): The current input string.

        Returns:
            str: The suggested completion string.
        """
        from difflib import get_close_matches  # type: ignore
        choices = ["apple", "apricot", "banana", "blueberry", "blackberry", "orange"]
        approximated_string = get_close_matches(s, choices, n=1, cutoff=0.5)
        
        return approximated_string[0] if approximated_string else ""

    session = DynamicInput()
    session.input("cooltest> ", call_to=call_to_example)
