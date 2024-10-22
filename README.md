# 🌟 Dynamic Input for Python 🐍

Welcome to the **Dynamic Input** library! This Python script enhances the user input experience in console applications, providing features like auto-completion, customizable prompts, and more! 🚀

## 📦 Features

- **Auto-completion**: Suggests completions as you type! ✨
- **Customizable Prompt**: Change the prompt message to fit your needs! 💬
- **Real-time Input Handling**: Responds to writing in real-time! ⏱️
- **Flexible API**: Easily integrate with your functions for completion logic! 🔌

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
answer = session.input("cooltest> ", call_to=call_to_example)
print(f"\nAnswer: {answer}")
```

### 🚀 How It Works

- **`DynamicInput` class**: Main class to handle dynamic input.
- **`input` method**: Prompts the user for input and allows for auto-completion based on the provided function.
- **Keybindings**:
  - **Enter**: Submit the input.
  - **Tab**: Autocomplete the current word.
  - **Backspace**: Delete the last character.

## 📜 Function Reference

- **`complete(s: str, shade: str)`**: Displays the completion string.
- **`_process_completion(buffer: list, shade: str, call_to: Optional[Callable[[str], str]])`**: Processes the completion string in a separate thread.
- **`input(prompt: str, call_to: Optional[Callable[[str], str]], ...)`**: Gets user input with auto-completion functionality.

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
