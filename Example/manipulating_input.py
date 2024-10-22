from dynamicio import DynamicInput

# In this example you will have an idea on how to use binds and raw_calls
#   In overalls, basically binds are special keys (ASCII) that are optional and can be used to trigger a call without time buffing
#   Raw calls are basically functions that are called with no return, so they wont be processed, that way you can process the input content easily

class RTDynamicReplacing:
    def __init__(self):
        self.session = DynamicInput()

    def check(self, text: str) -> None:
        place = text                                       # Snapshot of the original text
        place = place.replace("exit", "EXIT")              # Random replace, you can replace those with your logic
        place = place.replace("continue", "CONTINUE")      # Random replace, you can replace those with your logic

        if place == text:
            return # Abort if no change was made

        # This will delete a specific amount of characters in the input and print the new text
        #   This also automatically updates the input buffer
        #   in case of customization, you can directly manipulate self.session.buffer
        self.session.edit(returnRange=len(text), new_text=place)

    def realtime_check(self, prompt: str = None) -> str:
        # Let's config the input first:
        #   config_bind to " " so that the function is called when the space key is pressed.
        #   call_to to self.check so that the function is called when the space key is pressed.
        #   raw_call to True so that the function is called with no additional steps (like autocomplete).
        self.session.input(prompt, config_bind=" ", call_to=self.check, raw_call=True)

if __name__ == "__main__":
    rt = RTDynamicReplacing()
    print(rt.realtime_check("Type in: "))
