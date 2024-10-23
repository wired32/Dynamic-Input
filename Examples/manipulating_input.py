from dynamicio import DynamicInput

# In this example you will have an idea on how to use binds and raw_calls
#   In overalls, basically binds are special keys (ASCII) that are optional and can be used to trigger a call without time buffing
#   Raw calls are basically functions that are called with no return, so they won't be processed, that way you can process the input content easily

class RTDynamicReplacing:
    def __init__(self) -> None:
        self.session = DynamicInput()
        # Dictionary for keyword replacements
        self.replacements = {
            "exit": "EXIT",
            "continue": "CONTINUE"
        }

    def check(self, text: str) -> None:
        """Replaces specific keywords in the input text with designated values."""
        original_text = text  # Snapshot of the original text
        
        # Use dictionary to apply all replacements
        for key, value in self.replacements.items():
            text = text.replace(key, value)

        if text == original_text:
            return  # Abort if no change was made

        # This will delete a specific amount of characters in the input and print the new text
        #   This also automatically updates the input buffer
        #   in case of customization, you can directly manipulate self.session.buffer
        self.session.edit(returnRange=len(original_text), new_text=text)

    def realtime_check(self, prompt: str = None) -> str:
        """Configures the input settings for real-time checking."""
        # Let's config the input first:
        #   config_bind to " " so that the function is called when the space key is pressed.
        #   call_to to self.check so that the function is called when the space key is pressed.
        #   raw_call to True so that the function is called with no additional steps (like autocomplete).
        self.session.input(
            prompt, 
            config_bind=" ", 
            call_to=self.check, 
            raw_call=True
        )

if __name__ == "__main__":
    rt = RTDynamicReplacing()
    print(rt.realtime_check("Type in: "))
