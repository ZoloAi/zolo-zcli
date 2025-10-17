# zCLI/subsystems/zDisplay/zDisplay_modules/output/output_terminal.py

"""Terminal output adapter - stdout rendering."""

from .output_adapter import OutputAdapter

class TerminalOutput(OutputAdapter):
    """Terminal output via print() to stdout."""

    def write_raw(self, content):
        """Write raw content with no formatting or newline."""
        print(content, end='', flush=True)

    def write_line(self, content):
        """Write single line, ensuring newline."""
        if not content.endswith('\n'):
            content = content + '\n'
        self.write_raw(content)

    def write_block(self, content):
        """Write multi-line block, ensuring final newline."""
        if content and not content.endswith('\n'):
            content = content + '\n'
        self.write_raw(content)
