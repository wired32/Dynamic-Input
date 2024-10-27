# 🚀 Dynamic Inputs for Python

Welcome to the **Dynamic Input** library! This Python library enhances the user input experience in console applications and the control that developers have over the input, providing **Real time wide control** of the input!

## 📦 Features

- **Flexibility**: Dynamic Inputs allow you to control the user input without waiting for them to finish!
   - This allows you to create dynamic auto completers, grammar correctors, and more!
   - It use threads to guarantee that the user's experience won't be interrupted!
   - Instead of the single parameter that the conventional input function accepts, you can actually customize anything with this new input! This includes:
      - end: What will be displayed after the input, this defaults to '\n' like python does but you can set it as an empty string or a space to stay on the same line!
      - allow_empty_input: If false, will block the input flow to make sure that the user will not be able to enter an empty string, set it as True if you don't want this functionality.
      - And more!
   

## 🛠️ Installation

To use this script, ensure you have Python installed on your machine. This script is only compatible with Windows environments yet (might come to linux soon!).

1. Clone the repository or download the script.
2. Make sure you have the `rich` library installed. You can install it using pip:

   ```bash
   pip install rich
   ```

3. Run the script in your terminal!

## 📖 Usage

Here's a quick guide on how to use the **Dynamic Input** class:

```python
from dynamicio import DynamicInput

# Example completion function
def call_to_example(s: str) -> str:
    choices = ["apple", "apricot", "banana", "blueberry", "blackberry", "orange"]
    s = s.split(' ')[-1]  # Get the last word in the buffer
    for choice in choices:
        if choice.startswith(s):
            return choice[len(s):]  # Return the remaining part of the string
    return ""

# Create a DynamicInput session
session = DynamicInput()
answer = session.input("cooltest> ", call_to=call_to_example, autocomplete=True)
print(f"\nAnswer: {answer}")
```

### 🚀 How It Works

- **`DynamicInput` class**: Main class to handle dynamic input.
- **`input` method**: Prompts the user for input and allows for auto-completion based on the provided function.
- **`edit` method**: This will edit the current input content, useful to apply at the call_to function.
- **Keybindings**:
  - **Enter**: Submit the input.
  - **Tab**: Autocomplete the current word.
  - **Backspace**: Delete the last character.
  - **Custom Keybind**: Triggers the given functionm

## 🌐 Example Output

```plaintext
cooltest> app
``` 
This would suggest "apple" if you started typing `app`! 

## 📝 Notes

- Ensure your console supports ANSI escape sequences for optimal display.
- Currently supports Windows systems only due to the use of the `msvcrt` module.

## 🤝 Contributing

Contributions are welcome! If you have suggestions or improvements, feel free to open an issue or submit a pull request. 🙌

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
