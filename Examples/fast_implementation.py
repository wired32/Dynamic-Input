# This is an example of how you can easily implement dynamic inputs in your code without changing its entire structure
# Note that this is still limited for easier use, for better customization utilize DynamicInput.

# Import input function
from dynamicio import input

# Standart input
ex1 = input("Enter something: ")
print(ex1 + '\n')

# Simple autocompletion example
ex2 = input(
    "Enter something: ",
    call_to=lambda x: x.upper()
)
print(ex2 + '\n')

# Simple raw call example
ex3 = input(
    "Enter something: ",
    call_to=lambda x: print(f"\n{x.upper()}"),
    raw_call=True,
    inactivity_trigger=True
)
print(ex3 + '\n')
