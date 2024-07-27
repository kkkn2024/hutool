class ToolExecption(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return f"exception msg={self.msg}"

