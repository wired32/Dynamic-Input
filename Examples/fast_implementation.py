# This is an example of how you can easily implement dynamic inputs in your code without changing its entire structure
# Note that this is still limited for easier use, for better customization utilize DynamicInput.

# Import input function
from src.dynamicio import input


# Standart input
ex1 = input("Enter something: ")
print(ex1 + '\n')

# Simple autocompletion example
ex2 = input(
    "Enter something: ",
    call_to=lambda x: x.upper() # This is just an example, Feel free to use your own function here
)
print(ex2 + '\n')

# Simple raw call example
ex3 = input(
    "Enter something: ",
    call_to=lambda x: print(f"\n{x.upper()}"), # This is just an example, Feel free to use your own function here
    raw_call=True,
    inactivity_trigger=True
)
print(ex3 + '\n')
