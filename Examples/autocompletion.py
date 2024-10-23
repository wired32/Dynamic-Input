from dynamicio import DynamicInput

# In this example we will create a simple auto completer using DynamicInput.

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

if __name__ == '__main__':
    # First we reate the dynamic input object
    session = DynamicInput()

    # Quick example using lambda
    # Start and set the input configurations
    ex1 = session.input(
        prompt="Enter your name: ", # Prompt that will be used, works the same way as input("Enter your name: ")
        call_to=lambda x: f"current text: {x}", # Simple lambda that will show us how the auto completion works
        end="\n", # Let's set an end (defaults as \n, this is useful if you dont want a newline after sending the input)
        time_buffer=0.5, # Time in seconds before fetching autocompletion, defaults to 0.5
        indent=4, # Number of spaces that 'tab' key will add to the input if no completion is avaliable, set as 0 to disable, defaults as 4
        allow_empty_input=False, # If False, blocks the enter key if the input is empty, defaults to False
        shade="grey30", # Color shade for the autocompletion, defaults to grey30 (this uses rich standart colors)
    )

    # Observation: most of these arguments are not required, but they are good to know in case you want customization.

    print(ex1, end='\n\n') # Printing the final input

    # Example using the simple auto completer we made
    # Same thing as the last example but with our function and only using required parameters:
    ex2 = session.input(
        prompt="Enter your name: ",
        call_to=call_to_example, # Call to function
    )

    print(ex2) # Printing the final input


