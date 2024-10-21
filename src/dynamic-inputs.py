import msvcrt
from time import time as timestamp
from typing import Callable, Optional
from threading import Thread
from packets import CompletionPacket, InputConfigsPacket

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
        self.completion = CompletionPacket('', '', 0) # Empty packet
        self.completionLen = 0
        self.exit = False
        self.fetchInProgress = False

        self.handlers = {
            '\t': self._handle_tab,
            '\r': self._handle_enter,
            '\b': self._handle_backspace
        }

    def complete(self, s: CompletionPacket) -> None:
        """Prints the completion string to the console with the given shade.

        Args:
            s (str): The completion string to display.
            shade (str): The shade string to style the completion output.
        """
        if len(self.buffer) > s.bufferlenght:
            return # Buffer change, completion might glitch so return early

        from sys import stdout
        from rich import print
        stdout.write("\033[s")  # Save cursor position
        stdout.write("\033[K")  # Clear the line
        stdout.flush()

        # Hide the cursor for UX
        stdout.write("\033[?25l")
        stdout.flush()

        print(f"[{s.shade}]{s.content}", end='', flush=True)  # Print completion

        stdout.write("\033[u")    # Restore cursor position
        stdout.flush()
        
        stdout.write("\033[?25h") # Show the cursor again
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

        self.completion = CompletionPacket(call_to(''.join(buffer)), shade, len(buffer))

        if not self.exit:
            self.complete(self.completion)
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
            shade (str): The shade string for the completion output. (uses rich standart colors)
            time_buffer (float): Time in seconds to wait before fetching completion after the last character typed.
            call_to (Callable[[str], str]): The function to call for the prediction string.
            indent (int): The number of spaces added if no completion is available.

        Returns:
            str: The user input string.
        """
        from rich import print

        ts = timestamp()
        called = False
        self.buffer = []

        if call_to is None:
            raise ValueError("Please provide a call_to function.")

        if prompt is not None:
            print(prompt, end='', flush=True)

        while True:
            cts = timestamp()
            
            # Check if enough time has passed since the last character was typed
            if cts - ts > time_buffer and called:
                complete_thread = Thread(target=self._process_completion, args=(self.buffer, shade, call_to))
                complete_thread.start()
                called = False  # Reset called after processing completion

            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8')

                if key in self.handlers:
                    handler = self.handlers.get(key)
                    response = handler(InputConfigsPacket(buffer=self.buffer, indent=indent, end=end, allow_empty_input=allow_empty_input, key=key))
                    if response == 'EXIT': break # End of input
                    elif response == 'CONTINUE': continue # Ignore input
                    called = response
                else:
                    called = self._handle_regular(InputConfigsPacket(key=key))

                ts = cts  # Update the timestamp

        return ''.join(self.buffer)
    
    def _handle_enter(self, args: InputConfigsPacket):
        """Handles the enter key press event to end the input and print a newline.
        
        Args:
            args (InputConfigsPacket): Contains the input configuration settings, including the buffer, indentation level, 
                                    end character, allow_empty_input flag, and the key pressed.
        
        Returns:
            str: 'EXIT' to indicate that the input has ended, 'CONTINUE' if the input should continue.
        """
        from sys import stdout
        if not args.allow_empty_input and not self.buffer:
            return 'CONTINUE' # Code to sinalize end of input
        self.exit = True
        stdout.write("\033[K")  # Clear any completion
        stdout.flush()

        print(end=args.end)
        return 'EXIT'

    def _handle_backspace(self, args: InputConfigsPacket):
        """
        Handles the backspace key press event to delete the last character in the buffer and move the cursor back.

        Args:
            args (InputConfigsPacket): Contains the input configuration settings, including the buffer, indentation level, 
                                    end character, allow_empty_input flag, and the key pressed.

        Returns:
            bool: True if the input has changed, False otherwise.
        """
        if self.buffer:
            from sys import stdout
            self.buffer.pop()
            stdout.write('\x1b[D\x1b[P')  # Move cursor back and replace character
            stdout.flush()
            return True  # Indicate input has changed

    def _handle_tab(self, args: InputConfigsPacket):
        """
        Handles the tab key press event to either complete the current input or insert spaces.

        Args:
            args (InputConfigsPacket): Contains the input configuration settings, including the buffer, indentation level, 
                                    end character, allow_empty_input flag, and the key pressed.

        Returns:
            bool: Returns False to indicate that the input handling should continue.
        """
        if self.completion.content:
            print(self.completion.content, end='', flush=True)  # Show completion
            self.buffer.extend(self.completion.content)  # Append the completion to the buffer
            return False
        else:
            print(" " * args.indent, end='', flush=True)  # Print spaces if no completion
            return False

    def _handle_regular(self, args: InputConfigsPacket):
        """Handles regular input characters.

        Args:
            args (InputConfigsPacket): The input configuration packet with the input character.

        Returns:
            bool: True if the input has changed, False otherwise.
        """
        self.buffer.append(args.key)
        print(f"{args.key}", end='', flush=True)
        return True  # Indicate input has changed

if __name__ == "__main__":
    def call_to_example(s: str) -> str:
        """Auto-completion function that returns the remaining part of the best matching word based on user input.

        Args:
            s (str): The current input string.

        Returns:
            str: The remaining part of the completed string or an empty string if no match is found.
        """
        choices = ["apple", "apricot", "banana", "blueberry", "blackberry", "orange"]
        
        s = s.split(' ')[::-1][0] # Gets the last word in the buffer
        for choice in choices:
            if choice.startswith(s):
                return choice[len(s):]  # Return the remaining part of the string
        
        return ""  # Return an empty string if no match is found

    session = DynamicInput()
    answer = session.input("cooltest> ", call_to=call_to_example)
    print(f"\nAnswer: {answer}")