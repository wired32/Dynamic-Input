class CompletionPacket:
    def __init__(self, completion: str, shade: str, bufferLen: int):
        self.content = completion
        self.shade = shade
        self.bufferlenght = bufferLen
