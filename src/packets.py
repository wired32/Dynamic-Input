class CompletionPacket:
    def __init__(self, completion: str, shade: str, bufferLen: int):
        self.content = completion
        self.shade = shade
        self.bufferlenght = bufferLen

class InputConfigsPacket:
    def __init__(self, buffer = None, indent = None, end = None, allow_empty_input = None, key = None):
        self.buffer = buffer
        self.end = end
        self.indent = indent
        self.allow_empty_input = allow_empty_input
        self.key = key
