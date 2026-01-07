"""
Zolo Parser

Main parser module with public API (load, loads, dump, dumps, tokenize).
"""

import yaml
import json
from pathlib import Path
from typing import Any, Union, Optional, IO, List, Tuple
import re

from zolo.type_hints import process_type_hints, TYPE_HINT_PATTERN
from zolo.constants import FILE_EXT_ZOLO, FILE_EXT_YAML, FILE_EXT_YML, FILE_EXT_JSON
from zolo.exceptions import ZoloParseError, ZoloDumpError
from zolo.lsp_types import SemanticToken, TokenType, Position, Range, ParseResult


def _char_to_utf16_offset(text: str, char_offset: int) -> int:
    """
    Convert a Python character offset to UTF-16 code unit offset.
    
    VSCode's LSP uses UTF-16 code units for positions, but Python uses characters.
    Multi-byte characters like emojis (🤢) count as 1 in Python but 2 in UTF-16.
    
    Args:
        text: The text string
        char_offset: Character offset (Python string indexing)
    
    Returns:
        UTF-16 code unit offset (for LSP)
    """
    # Get the substring up to the character offset
    substring = text[:char_offset]
    # Encode to UTF-16 and count code units (each unit is 2 bytes, skip BOM)
    utf16_bytes = substring.encode('utf-16-le')
    return len(utf16_bytes) // 2


class TokenEmitter:
    """Helper class to track positions and emit semantic tokens during parsing."""
    
    def __init__(self, content: str):
        self.content = content
        self.lines = content.splitlines(keepends=False)  # Keep lines for UTF-16 conversion
        self.tokens: List[SemanticToken] = []
        self.comment_ranges: List[Tuple[int, int, int, int]] = []  # [(start_line, start_col, end_line, end_col), ...]
    
    def add_comment_range(self, start_line: int, start_col: int, end_line: int, end_col: int):
        """Track a comment range to avoid overlapping tokens."""
        self.comment_ranges.append((start_line, start_col, end_line, end_col))
    
    def _overlaps_comment(self, line: int, start: int, end: int) -> bool:
        """Check if a position range overlaps with any comment."""
        for c_start_line, c_start_col, c_end_line, c_end_col in self.comment_ranges:
            if line == c_start_line == c_end_line:
                # Same line comment
                if not (end <= c_start_col or start >= c_end_col):
                    return True
            elif line == c_start_line:
                # Token on comment start line
                if start < c_start_col:
                    continue  # Token is before comment
                return True  # Token starts in or after comment start
            elif c_start_line < line < c_end_line:
                # Token is on a middle line of multi-line comment
                return True
            elif line == c_end_line:
                # Token on comment end line
                if end > c_end_col:
                    continue  # Token is after comment
                return True  # Token ends in or before comment end
        return False
    
    def emit(self, line: int, start_char: int, length: int, token_type: TokenType):
        """
        Emit a semantic token with UTF-16 position conversion.
        
        Args:
            line: Line number (0-based)
            start_char: Character offset in Python string (NOT UTF-16)
            length: Length in Python characters (NOT UTF-16)
            token_type: Token type
        """
        if length <= 0:
            return
        
        # Get the line text for UTF-16 conversion
        if line >= len(self.lines):
            return
        line_text = self.lines[line]
        
        # For non-comment tokens, check if they overlap with comments and truncate if needed
        if token_type != TokenType.COMMENT:
            end_char = start_char + length
            
            # Check if this token overlaps any comment
            for c_start_line, c_start_col, c_end_line, c_end_col in self.comment_ranges:
                if line == c_start_line and start_char < c_start_col < end_char:
                    # Token would extend into a comment - truncate it
                    length = c_start_col - start_char
                    end_char = start_char + length
                    if length <= 0:
                        return  # Token is entirely within comment
                    break
        
        # Convert Python character positions to UTF-16 code unit positions
        utf16_start = _char_to_utf16_offset(line_text, start_char)
        utf16_end = _char_to_utf16_offset(line_text, start_char + length)
        
        token = SemanticToken(
            range=Range(
                start=Position(line=line, character=utf16_start),
                end=Position(line=line, character=utf16_end)
            ),
            token_type=token_type
        )
        self.tokens.append(token)
    
    def emit_range(self, start_line: int, start_char: int, end_line: int, end_char: int, token_type: TokenType):
        """
        Emit a token with explicit start and end positions (UTF-16 converted).
        
        Args:
            start_line: Start line number
            start_char: Start character offset in Python string
            end_line: End line number
            end_char: End character offset in Python string
            token_type: Token type
        """
        # Convert positions to UTF-16
        if start_line >= len(self.lines) or end_line >= len(self.lines):
            return
        
        start_line_text = self.lines[start_line]
        end_line_text = self.lines[end_line]
        
        utf16_start = _char_to_utf16_offset(start_line_text, start_char)
        utf16_end = _char_to_utf16_offset(end_line_text, end_char)
        
        token = SemanticToken(
            range=Range(
                start=Position(line=start_line, character=utf16_start),
                end=Position(line=end_line, character=utf16_end)
            ),
            token_type=token_type
        )
        self.tokens.append(token)
    
    def get_tokens(self) -> List[SemanticToken]:
        """Get all emitted tokens."""
        return sorted(self.tokens, key=lambda t: (t.line, t.start_char))


def tokenize(content: str) -> ParseResult:
    """
    Parse .zolo content and return both parsed data and semantic tokens for LSP.
    
    This is the primary entry point for the Language Server Protocol to get
    semantic highlighting information along with parsed data.
    
    Args:
        content: Raw .zolo file content
    
    Returns:
        ParseResult with data, tokens, and any errors
    
    Examples:
        >>> result = tokenize("port: 8080\\nhost: localhost")
        >>> result.data
        {'port': 8080.0, 'host': 'localhost'}
        >>> result.tokens
        [SemanticToken(...), SemanticToken(...), ...]
    """
    emitter = TokenEmitter(content)
    errors = []
    
    try:
        # Parse with token emission
        data = _parse_zolo_content_with_tokens(content, emitter)
        return ParseResult(data=data, tokens=emitter.get_tokens(), errors=errors)
    except ZoloParseError as e:
        # Still return tokens even if parse failed
        errors.append(str(e))
        return ParseResult(data=None, tokens=emitter.get_tokens(), errors=errors)


def load(fp: Union[str, Path, IO], file_extension: Optional[str] = None) -> Any:
    """
    Load data from a .zolo file (or compatible format).
    
    Args:
        fp: File path (str/Path) or file-like object
        file_extension: Optional file extension override (.zolo, .yaml, .json)
                       If None, will detect from file path or default to .zolo
    
    Returns:
        Parsed data (dict, list, or scalar)
    
    Raises:
        ZoloParseError: If parsing fails
        FileNotFoundError: If file doesn't exist
    
    Examples:
        >>> # Load .zolo file (string-first)
        >>> data = zolo.load('config.zolo')
        
        >>> # Load .yaml file (native types)
        >>> data = zolo.load('config.yaml')
        
        >>> # Load with explicit extension
        >>> data = zolo.load('config.txt', file_extension='.zolo')
    """
    # Handle file path vs file-like object
    if isinstance(fp, (str, Path)):
        file_path = Path(fp)
        
        # Detect file extension if not provided
        if file_extension is None:
            file_extension = file_path.suffix.lower()
            if not file_extension:
                file_extension = FILE_EXT_ZOLO  # Default to .zolo
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise ZoloParseError(f"Error reading file {file_path}: {e}") from e
    else:
        # File-like object
        try:
            content = fp.read()
        except Exception as e:
            raise ZoloParseError(f"Error reading from file object: {e}") from e
        
        # Try to detect extension from file name
        if file_extension is None and hasattr(fp, 'name'):
            file_extension = Path(fp.name).suffix.lower()
        if not file_extension:
            file_extension = FILE_EXT_ZOLO  # Default to .zolo
    
    # Parse content
    return loads(content, file_extension=file_extension)


def loads(s: str, file_extension: Optional[str] = None) -> Any:
    """
    Load data from a .zolo string (or compatible format).
    
    Args:
        s: String content to parse
        file_extension: Optional file extension hint (.zolo, .yaml, .json)
                       Defaults to .zolo if not provided
    
    Returns:
        Parsed data (dict, list, or scalar)
    
    Raises:
        ZoloParseError: If parsing fails
    
    Examples:
        >>> # Parse .zolo string (string-first)
        >>> data = zolo.loads('port: 8080')
        {'port': '8080'}  # String by default
        
        >>> # Parse with type hint
        >>> data = zolo.loads('port(int): 8080')
        {'port': 8080}  # Integer via type hint
        
        >>> # Parse .yaml string (native types)
        >>> data = zolo.loads('port: 8080', file_extension='.yaml')
        {'port': 8080}  # Integer via YAML
    """
    if not s or not s.strip():
        return None
    
    # Default to .zolo if not specified
    if file_extension is None:
        file_extension = FILE_EXT_ZOLO
    
    # Normalize extension
    file_extension = file_extension.lower()
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension
    
    # Determine if string-first should be applied
    # .zolo files now use RFC 8259 type detection (like JSON)
    # string_first = False means: respect native types (int, float, bool, null)
    # Only YAML files (.yaml/.yml) would use string_first if we wanted that
    string_first = False
    
    # Parse based on format
    try:
        if file_extension == FILE_EXT_JSON:
            # Parse as JSON
            parsed = json.loads(s)
        elif file_extension == FILE_EXT_ZOLO:
            # Custom .zolo parser (no YAML quirks)
            # TODO: Implement custom parsing logic
            parsed = _parse_zolo_content(s)
        else:
            # Parse as YAML (for .yaml, .yml files)
            parsed = yaml.safe_load(s)
        
        # Process type hints
        parsed = process_type_hints(parsed, string_first=string_first)
        
        return parsed
    
    except yaml.YAMLError as e:
        raise ZoloParseError(f"YAML parsing error: {e}") from e
    except json.JSONDecodeError as e:
        raise ZoloParseError(f"JSON parsing error: {e}") from e
    except Exception as e:
        raise ZoloParseError(f"Parsing error: {e}") from e


def _parse_zolo_content(content: str) -> Any:
    """
    Custom .zolo parser without YAML quirks.
    
    Implementation follows ZOLO_PARSER_IMPLEMENTATION_PLAN.md
    Current: Phase 1-2 Complete (Comments, Types, Arrays, Nested Objects)
    """
    # Step 1.1: Strip comments and prepare lines
    lines = _strip_comments_and_prepare_lines(content)
    
    # Step 4.8: Check indentation consistency (Python-style)
    _check_indentation_consistency(lines)
    
    # Step 2.3: Parse with nested object support
    result = _parse_lines(lines)
    
    return result


def _parse_zolo_content_with_tokens(content: str, emitter: TokenEmitter) -> Any:
    """
    Custom .zolo parser with token emission for LSP.
    
    This version tracks positions and emits semantic tokens during parsing.
    """
    # Step 1: Strip comments and prepare lines (with token emission)
    lines, line_mapping = _strip_comments_and_prepare_lines_with_tokens(content, emitter)
    
    # Step 2: Check indentation consistency
    _check_indentation_consistency(lines)
    
    # Step 3: Parse with token emission
    result = _parse_lines_with_tokens(lines, line_mapping, emitter)
    
    return result


def _check_indentation_consistency(lines: list[str]) -> None:
    """
    Check that indentation is consistent (Python-style).
    
    Allows either tabs OR spaces for indentation, but forbids mixing.
    This is superior to YAML's arbitrary "spaces only" rule because:
    - Tabs are semantic (1 tab = 1 level)
    - Spaces are flexible (user choice)
    - Mixing is chaos (forbidden!)
    
    Args:
        lines: List of lines to check
    
    Raises:
        ZoloParseError: If tabs and spaces are mixed in indentation
    
    Philosophy:
        Like Python, .zolo cares about CONSISTENCY, not character type.
        Choose tabs (semantic) OR spaces (traditional), but be consistent!
    """
    first_indent_type = None  # 'tab' or 'space'
    first_indent_line = None
    
    for line_num, line in enumerate(lines, 1):
        # Skip empty lines and lines with no indentation
        if not line.strip():
            continue
        
        # Get indentation characters
        stripped = line.lstrip()
        if len(stripped) == len(line):
            # No indentation
            continue
        
        indent_chars = line[:len(line) - len(stripped)]
        
        # Check what this line uses
        has_tab = '\t' in indent_chars
        has_space = ' ' in indent_chars
        
        # ERROR: Mixed tabs and spaces in SAME line
        if has_tab and has_space:
            raise ZoloParseError(
                f"Mixed tabs and spaces in indentation at line {line_num}.\n"
                f"Use either tabs OR spaces consistently (Python convention).\n"
                f"Hint: Configure your editor to use one type of indentation."
            )
        
        # Determine this line's indent type
        current_type = 'tab' if has_tab else 'space'
        
        # Track first indent type seen in file
        if first_indent_type is None:
            first_indent_type = current_type
            first_indent_line = line_num
        # ERROR: Different type than rest of file
        elif first_indent_type != current_type:
            indent_word = 'tabs' if first_indent_type == 'tab' else 'spaces'
            current_word = 'tabs' if current_type == 'tab' else 'spaces'
            raise ZoloParseError(
                f"Inconsistent indentation at line {line_num}.\n"
                f"File uses {indent_word} (first seen at line {first_indent_line}),\n"
                f"but this line uses {current_word}.\n"
                f"Use either tabs OR spaces consistently (Python convention)."
            )


def _strip_comments_and_prepare_lines(content: str) -> list[str]:
    """
    Phase 1, Step 1.1: Strip comments from .zolo content.
    
    Rules:
    - Full-line comments: # at line start (or after whitespace only)
    - Inline comments: #> ... <# (paired delimiters)
    - Multi-line comments supported with #> ... <#
    - Unpaired #> or <# are treated as literal text
    - # without > is a literal character (hex colors, hashtags, etc.)
    - Skip empty lines after comment removal
    - Preserve indentation
    
    Args:
        content: Raw .zolo file content
    
    Returns:
        List of cleaned lines (no comments, no empty lines)
    
    Examples:
        >>> _strip_comments_and_prepare_lines("# Full line comment\\nkey: value")
        ['key: value']
        
        >>> _strip_comments_and_prepare_lines("key: value #> comment <#")
        ['key: value']
        
        >>> _strip_comments_and_prepare_lines("color: #fffcbf #> nice <#")
        ['color: #fffcbf']
        
        >>> _strip_comments_and_prepare_lines("tag: #python")
        ['tag: #python']
    """
    # First, strip all #> ... <# paired comments (including multi-line)
    result = content
    
    while True:
        # Find opening #>
        start = result.find('#>')
        if start == -1:
            break  # No more arrow comments
        
        # Find matching closing <#
        end = result.find('<#', start + 2)
        if end == -1:
            # No matching <# found, treat #> as literal
            break
        
        # Remove the comment (including markers)
        result = result[:start] + result[end + 2:]
    
    # Now split into lines and handle full-line comments
    cleaned_lines = []
    for line in result.splitlines():
        # Check if this is a full-line comment (# at start after optional whitespace)
        stripped = line.lstrip()
        if stripped.startswith('#'):
            # Full-line comment, skip it
            continue
        
        # Strip trailing whitespace (but preserve leading indentation)
        line = line.rstrip()
        
        # Skip empty lines
        if line:
            cleaned_lines.append(line)
    
    return cleaned_lines


def _strip_comments_and_prepare_lines_with_tokens(content: str, emitter: TokenEmitter) -> Tuple[list[str], dict]:
    """
    Strip comments and prepare lines while emitting comment tokens.
    Handles both full-line comments and multi-line #> ... <# comments.
    
    Returns:
        Tuple of (cleaned_lines, line_mapping)
        line_mapping maps cleaned line index to original line number
    """
    lines = content.splitlines()
    
    # Phase 1: Identify full-line comments (these should be ignored for inline comment processing)
    full_line_comment_lines = set()
    for line_num, line in enumerate(lines):
        stripped = line.lstrip()
        # A line is a full-line comment if it starts with # (but not #>)
        if stripped.startswith('#') and not stripped.startswith('#>'):
            full_line_comment_lines.add(line_num)
            # Emit token for this full-line comment
            indent_len = len(line) - len(stripped)
            emitter.emit(line_num, indent_len, len(stripped), TokenType.COMMENT)
    
    # Phase 2: Find and emit all #> ... <# comments (including multi-line)
    # Only search in content that's NOT part of full-line comments
    comment_char_ranges = []  # Store (char_start, char_end) tuples in original content
    comment_line_ranges = []  # Store (start_line, start_col, end_line, end_col) tuples
    
    search_pos = 0
    while search_pos < len(content):
        # Find opening #>
        start = content.find('#>', search_pos)
        if start == -1:
            break  # No more arrow comments
        
        # Check if this #> is within a full-line comment
        start_line = content[:start].count('\n')
        if start_line in full_line_comment_lines:
            # Skip this #>, it's inside a full-line comment
            search_pos = start + 2
            continue
        
        # Find matching closing <#
        end = content.find('<#', start + 2)
        if end == -1:
            # No matching <# found, skip this #>
            search_pos = start + 2
            continue
        
        # Store this comment range (from #> to <# inclusive)
        comment_char_ranges.append((start, end + 2))
        search_pos = end + 2
    
    # Emit comment tokens for all found ranges
    for char_start, char_end in comment_char_ranges:
        # Convert absolute character positions to line/column
        start_line = content[:char_start].count('\n')
        start_col = char_start - content.rfind('\n', 0, char_start) - 1
        
        end_line = content[:char_end].count('\n')
        end_col = char_end - content.rfind('\n', 0, char_end) - 1
        
        # Track this comment range to avoid overlapping tokens
        emitter.add_comment_range(start_line, start_col, end_line, end_col)
        comment_line_ranges.append((start_line, start_col, end_line, end_col))
        
        if start_line == end_line:
            # Single-line comment
            emitter.emit(start_line, start_col, char_end - char_start, TokenType.COMMENT)
            
            # Check if there's text after <# on the same line - emit as STRING
            line_text = lines[start_line]
            text_after = line_text[end_col:].strip()
            if text_after:
                # Find where the non-whitespace text starts
                after_start = end_col
                while after_start < len(line_text) and line_text[after_start].isspace():
                    after_start += 1
                if after_start < len(line_text):
                    emitter.emit(start_line, after_start, len(line_text) - after_start, TokenType.STRING)
        else:
            # Multi-line comment - emit separate tokens for each line
            # This is more compatible with LSP's semantic token format
            lines_in_comment = content[char_start:char_end].splitlines(keepends=False)
            current_line = start_line
            
            for i, line_text in enumerate(lines_in_comment):
                if i == 0:
                    # First line: from start_col to end of line
                    emitter.emit(current_line, start_col, len(lines[current_line]) - start_col, TokenType.COMMENT)
                elif i == len(lines_in_comment) - 1:
                    # Last line: from start of line to end_col
                    # Get the indentation of this line
                    actual_line = lines[current_line]
                    indent = len(actual_line) - len(actual_line.lstrip())
                    emitter.emit(current_line, indent, end_col - indent, TokenType.COMMENT)
                    
                    # Check if there's text after <# on the last line - emit as STRING
                    text_after = actual_line[end_col:].strip()
                    if text_after:
                        # Find where the non-whitespace text starts
                        after_start = end_col
                        while after_start < len(actual_line) and actual_line[after_start].isspace():
                            after_start += 1
                        if after_start < len(actual_line):
                            emitter.emit(current_line, after_start, len(actual_line) - after_start, TokenType.STRING)
                else:
                    # Middle lines: entire line is comment
                    actual_line = lines[current_line]
                    indent = len(actual_line) - len(actual_line.lstrip())
                    emitter.emit(current_line, indent, len(actual_line) - indent, TokenType.COMMENT)
                current_line += 1
    
    # Phase 3: Build cleaned lines (remove comments, skip full-line comments)
    cleaned_lines = []
    line_mapping = {}  # Maps cleaned index -> original line number
    pending_append = None  # Store text to append to previous cleaned line
    
    # Process each original line individually
    for line_num, line in enumerate(lines):
        # Skip full-line comments
        if line_num in full_line_comment_lines:
            continue
        
        # Remove inline comments from this line
        working_line = line
        for c_start_line, c_start_col, c_end_line, c_end_col in comment_line_ranges:
            if c_start_line == c_end_line == line_num:
                # Single-line comment on this line
                working_line = working_line[:c_start_col] + working_line[c_end_col:]
            elif c_start_line == line_num:
                # This line starts a multi-line comment - remove from comment start to end of line
                working_line = working_line[:c_start_col]
            elif c_start_line < line_num < c_end_line:
                # This line is in the middle of a multi-line comment - skip it entirely
                working_line = ""
                break
            elif c_end_line == line_num:
                # This line ends a multi-line comment - keep text after <#
                text_after = working_line[c_end_col:].strip()
                if text_after:
                    # Append this text to the line that started the comment
                    pending_append = text_after
                working_line = ""
                break
        
        # Handle pending append
        if pending_append and cleaned_lines:
            cleaned_lines[-1] += " " + pending_append
            pending_append = None
        
        # Strip trailing whitespace
        working_line = working_line.rstrip()
        
        # Skip empty lines
        if working_line:
            line_mapping[len(cleaned_lines)] = line_num
            cleaned_lines.append(working_line)
    
    return cleaned_lines, line_mapping


def _parse_lines_with_tokens(lines: list[str], line_mapping: dict, emitter: TokenEmitter) -> dict:
    r"""
    Parse lines with token emission for LSP.
    
    Similar to _parse_lines() but emits semantic tokens for all syntax elements.
    """
    if not lines:
        return {}
    
    structured_lines = []
    i = 0
    line_number = 0
    
    while i < len(lines):
        line = lines[i]
        original_line_num = line_mapping.get(i, i)
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        
        if ':' in stripped:
            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip()
            
            # Find key position in original line
            key_start = line.find(key)
            
            # Emit colon token
            colon_pos = line.find(':', key_start)
            emitter.emit(original_line_num, colon_pos, 1, TokenType.COLON)
            
            # Check for type hint
            match = TYPE_HINT_PATTERN.match(key)
            if match:
                clean_key = match.group(1)
                type_hint = match.group(2)
                
                # Emit root or nested key token
                if indent == 0:
                    emitter.emit(original_line_num, key_start, len(clean_key), TokenType.ROOT_KEY)
                else:
                    emitter.emit(original_line_num, key_start, len(clean_key), TokenType.NESTED_KEY)
                
                # Emit type hint token
                hint_start = key_start + len(clean_key) + 1  # +1 for opening paren
                emitter.emit(original_line_num, hint_start, len(type_hint), TokenType.TYPE_HINT)
                
                has_str_hint = type_hint.lower() == 'str'
            else:
                # No type hint
                if indent == 0:
                    emitter.emit(original_line_num, key_start, len(key), TokenType.ROOT_KEY)
                else:
                    emitter.emit(original_line_num, key_start, len(key), TokenType.NESTED_KEY)
                has_str_hint = False
            
            # Emit value tokens if value is present
            if value:
                value_start = colon_pos + 1
                # Skip whitespace after colon
                while value_start < len(line) and line[value_start] == ' ':
                    value_start += 1
                _emit_value_tokens(value, original_line_num, value_start, emitter)
            
            # Store structured line info
            structured_lines.append({
                'indent': indent,
                'key': key,
                'value': value,
                'line': line,
                'line_number': original_line_num,
                'is_multiline': False
            })
            i += 1
            line_number += 1
        else:
            i += 1
            line_number += 1
    
    # Build nested structure (without token emission, as tokens already emitted)
    return _build_nested_dict(structured_lines, 0, 0)


def _parse_lines(lines: list[str]) -> dict:
    r"""
    Phase 2, Step 2.3 + Phase 3: Parse lines with nested object and multi-line string support.
    
    Uses indentation to build nested dictionary structure:
    - Track indent level for each line
    - Build parent-child relationships
    - Support nested objects at any depth
    - Support multi-line strings: pipe, triple-quotes, escape sequences
    
    Args:
        lines: Cleaned lines (from Step 1.1)
    
    Returns:
        Nested dictionary structure
    
    Examples:
        >>> _parse_lines(["name: MyApp", "port: 5000"])
        {'name': 'MyApp', 'port': 5000.0}
        
        >>> _parse_lines(["server:", "  host: localhost", "  port: 5000"])
        {'server': {'host': 'localhost', 'port': 5000.0}}
    """
    if not lines:
        return {}
    
    # Parse lines into structured data with indentation info and multi-line handling
    structured_lines = []
    i = 0
    line_number = 1  # Track line numbers for error messages
    
    while i < len(lines):
        line = lines[i]
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        
        if ':' in stripped:
            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip()
            
            # Validate key is ASCII-only (RFC 8259 compliance)
            _validate_ascii_only(key, line_number)
            
            # Check if key has (str) type hint for multi-line collection
            match = TYPE_HINT_PATTERN.match(key)
            has_str_hint = match and match.group(2).lower() == 'str'
            
            # Multi-line ONLY enabled with (str) hint
            # | and """ are now literal characters (bread and butter!)
            if has_str_hint:
                # (str) type hint: collect YAML-style indented multi-line
                multiline_value, lines_consumed = _collect_str_hint_multiline(lines, i + 1, indent, value)
                structured_lines.append({
                    'indent': indent,
                    'key': key,
                    'value': multiline_value,
                    'line': line,
                    'line_number': line_number,
                    'is_multiline': True
                })
                i += lines_consumed + 1
                line_number += lines_consumed + 1
            else:
                # Regular value - | and """ are literal characters
                structured_lines.append({
                    'indent': indent,
                    'key': key,
                    'value': value,
                    'line': line,
                    'line_number': line_number,
                    'is_multiline': False
                })
                i += 1
                line_number += 1
        else:
            i += 1
            line_number += 1
    
    # Build nested structure
    return _build_nested_dict(structured_lines, 0, 0)


def _collect_str_hint_multiline(lines: list[str], start_idx: int, parent_indent: int, first_value: str) -> tuple[str, int]:
    """
    Collect multi-line string content when (str) type hint is used (YAML-style).
    
    Rule: Collect lines indented MORE than parent, strip base indent, preserve relative.
    
    Args:
        lines: All lines
        start_idx: Index to start collecting from (line after the key)
        parent_indent: Indentation level of the parent key
        first_value: The value on the same line as the key (if any)
    
    Returns:
        Tuple of (multiline_string, lines_consumed)
    
    Examples:
        >>> # Key with inline value
        >>> lines = ["  continues", "  here"]
        >>> _collect_str_hint_multiline(lines, 0, 0, "First")
        ("First\\ncontinues\\nhere", 2)
        
        >>> # Key without inline value
        >>> lines = ["  First", "  Second"]
        >>> _collect_str_hint_multiline(lines, 0, 0, "")
        ("First\\nSecond", 2)
    """
    collected = []
    
    # Add first value if present
    if first_value:
        collected.append(first_value)
    
    base_indent = None
    lines_consumed = 0
    
    for i in range(start_idx, len(lines)):
        line = lines[i]
        line_indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        
        # Stop if line is at same or less indent than parent (unless empty)
        if stripped and line_indent <= parent_indent:
            break
        
        # Stop if this looks like a new key at the same level
        if stripped and ':' in stripped and line_indent <= parent_indent:
            break
        
        # Empty line - preserve it
        if not stripped:
            collected.append('')
            lines_consumed += 1
            continue
        
        # Set base indent from first content line
        if base_indent is None:
            base_indent = line_indent
        
        # Strip base indent, keep relative
        if base_indent is not None:
            if line_indent >= base_indent:
                relative_line = line[base_indent:] if len(line) >= base_indent else line.strip()
                collected.append(relative_line)
            else:
                collected.append(line.strip())
        else:
            collected.append(line.strip())
        
        lines_consumed += 1
    
    return '\n'.join(collected), lines_consumed


def _collect_pipe_multiline(lines: list[str], start_idx: int, parent_indent: int) -> tuple[str, int]:
    """
    Collect multi-line string content after pipe | marker.
    
    Args:
        lines: All lines
        start_idx: Index to start collecting from
        parent_indent: Indentation level of the parent key
    
    Returns:
        Tuple of (multiline_string, lines_consumed)
    """
    collected = []
    base_indent = None
    lines_consumed = 0
    
    for i in range(start_idx, len(lines)):
        line = lines[i]
        line_indent = len(line) - len(line.lstrip())
        
        # If we hit a line at or less than parent indent, we're done
        if line and line_indent <= parent_indent:
            break
        
        # Set base indent from first content line
        if base_indent is None and line.strip():
            base_indent = line_indent
        
        # Collect line, stripping base indentation
        if base_indent is not None:
            if line_indent >= base_indent:
                # Strip base indent, keep relative indent
                relative_line = line[base_indent:] if len(line) >= base_indent else line.strip()
                collected.append(relative_line)
            else:
                collected.append(line.strip())
        else:
            collected.append(line.strip())
        
        lines_consumed += 1
    
    return '\n'.join(collected), lines_consumed


def _collect_triple_quote_multiline(lines: list[str], start_idx: int, initial_value: str) -> tuple[str, int]:
    '''
    Collect multi-line string content between triple quotes.
    
    Args:
        lines: All lines
        start_idx: Index of the line with opening triple-quotes
        initial_value: The value part (might contain opening and/or closing triple-quotes)
    
    Returns:
        Tuple of (multiline_string, lines_consumed)
    '''
    # Check if it's all on one line: """content"""
    if initial_value.count('"""') >= 2:
        # Extract content between quotes
        content = initial_value.split('"""', 2)[1]
        return content, 0
    
    # Multi-line case: collect until closing """
    collected = []
    lines_consumed = 0
    
    # First line might have content after opening """
    first_line_content = initial_value[3:].strip()  # Remove opening """
    if first_line_content:
        collected.append(first_line_content)
    
    # Collect subsequent lines
    base_indent = None
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        lines_consumed += 1
        
        # Check for closing """
        if '"""' in line:
            # Get content before closing """
            closing_content = line.split('"""')[0]
            if base_indent is None and closing_content.strip():
                base_indent = len(line) - len(line.lstrip())
            if closing_content.strip():
                if base_indent is not None:
                    relative_line = closing_content[base_indent:] if len(closing_content) >= base_indent else closing_content.strip()
                    collected.append(relative_line.rstrip())
                else:
                    collected.append(closing_content.strip())
            break
        
        # Set base indent from first content line
        if base_indent is None and line.strip():
            base_indent = len(line) - len(line.lstrip())
        
        # Collect line, stripping base indentation
        if base_indent is not None:
            line_indent = len(line) - len(line.lstrip())
            if line_indent >= base_indent:
                relative_line = line[base_indent:] if len(line) >= base_indent else line.strip()
                collected.append(relative_line.rstrip())
            else:
                collected.append(line.strip())
        else:
            collected.append(line.rstrip())
    
    return '\n'.join(collected), lines_consumed


def _build_nested_dict(structured_lines: list[dict], start_idx: int, current_indent: int) -> dict:
    """
    Recursively build nested dictionary from structured lines.
    
    Args:
        structured_lines: List of parsed line dictionaries
        start_idx: Index to start parsing from
        current_indent: Current indentation level we're parsing at
    
    Returns:
        Nested dictionary
    
    Raises:
        ZoloParseError: If duplicate keys are found at the same nesting level
    """
    result = {}
    seen_keys = {}  # Track: {clean_key: (line_number, original_key)}
    i = start_idx
    
    while i < len(structured_lines):
        line_info = structured_lines[i]
        indent = line_info['indent']
        key = line_info['key']
        value = line_info['value']
        line_number = line_info.get('line_number', '?')
        
        # If we've moved to a different indent level, stop
        if indent != current_indent:
            break
        
        # Strip type hint from key for duplicate checking
        # Example: "port(int)" → "port"
        match = TYPE_HINT_PATTERN.match(key)
        clean_key = match.group(1) if match else key
        
        # Check for duplicate keys (STRICT MODE - Phase 4.7)
        if clean_key in seen_keys:
            first_line, first_key = seen_keys[clean_key]
            raise ZoloParseError(
                f"Duplicate key '{clean_key}' found at line {line_number}.\n"
                f"First occurrence: '{first_key}' at line {first_line}.\n"
                f"Keys must be unique within the same level.\n"
                f"Hint: Did you mean to use a different key name?"
            )
        
        seen_keys[clean_key] = (line_number, key)
        
        # Check if next line is a child (more indented)
        has_children = False
        child_indent = None
        if i + 1 < len(structured_lines):
            next_indent = structured_lines[i + 1]['indent']
            if next_indent > indent:
                has_children = True
                child_indent = next_indent
        
        if has_children:
            # Recursively parse children
            child_dict = _build_nested_dict(structured_lines, i + 1, child_indent)
            result[key] = child_dict
            
            # Skip all child lines (find next line at current indent or less)
            i += 1
            while i < len(structured_lines) and structured_lines[i]['indent'] > indent:
                i += 1
        else:
            # Leaf node - detect value type or use multi-line string
            if line_info.get('is_multiline', False):
                # Multi-line string is already processed, use as-is
                result[key] = value
            else:
                # Detect value type (including \n escape sequences)
                typed_value = _detect_value_type(value) if value else ''
                result[key] = typed_value
            i += 1
    
    return result


def _parse_root_key_value_pairs(lines: list[str]) -> dict:
    """
    Phase 1, Steps 1.2-1.3: Parse basic key-value pairs with type detection.
    
    Rules:
    - Only parse lines at root level (no leading whitespace)
    - Split on first `:` occurrence
    - Trim whitespace from key and value
    - Apply RFC 8259 type detection (Step 1.3)
    - Skip nested lines (will be handled in Phase 2)
    
    Args:
        lines: Cleaned lines (from Step 1.1)
    
    Returns:
        Dictionary with root-level key-value pairs (typed values)
    
    Examples:
        >>> _parse_root_key_value_pairs(["name: MyApp", "port: 5000"])
        {'name': 'MyApp', 'port': 5000.0}
        
        >>> _parse_root_key_value_pairs(["debug: true", "db: null"])
        {'debug': True, 'db': None}
    """
    result = {}
    
    for line in lines:
        # Check if this is a root-level line (no leading whitespace)
        if line and line[0] not in (' ', '\t'):
            # Check if line contains a colon (key: value pattern)
            if ':' in line:
                # Split on first colon only
                key, _, value = line.partition(':')
                
                # Trim whitespace
                key = key.strip()
                value = value.strip()
                
                # Step 1.3: Detect and convert value type
                typed_value = _detect_value_type(value)
                
                result[key] = typed_value
    
    return result


def _emit_value_tokens(value: str, line: int, start_pos: int, emitter: TokenEmitter):
    """
    Emit semantic tokens for a value based on its detected type.
    
    Args:
        value: The value string
        line: Line number
        start_pos: Starting character position
        emitter: Token emitter
    """
    if not value:
        return
    
    # Array (bracket syntax)
    if value.startswith('[') and value.endswith(']'):
        _emit_array_tokens(value, line, start_pos, emitter)
        return
    
    # Object (brace syntax)
    if value.startswith('{') and value.endswith('}'):
        _emit_object_tokens(value, line, start_pos, emitter)
        return
    
    # Boolean
    if value.lower() in ('true', 'false'):
        emitter.emit(line, start_pos, len(value), TokenType.BOOLEAN)
        return
    
    # Number
    if _is_valid_number(value):
        emitter.emit(line, start_pos, len(value), TokenType.NUMBER)
        return
    
    # Null
    if value == 'null':
        emitter.emit(line, start_pos, len(value), TokenType.NULL)
        return
    
    # Check for specific string types
    # Timestamp
    if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
        emitter.emit(line, start_pos, len(value), TokenType.TIMESTAMP_STRING)
        return
    
    # Time
    if re.match(r'^\d{2}:\d{2}(?::\d{2})?$', value):
        emitter.emit(line, start_pos, len(value), TokenType.TIME_STRING)
        return
    
    # Version
    if re.match(r'^\d+\.\d+(?:\.\d+|\.\*)+$', value):
        emitter.emit(line, start_pos, len(value), TokenType.VERSION_STRING)
        return
    
    # Ratio
    if re.match(r'^\d{1,3}:\d{1,3}$', value) and value != 'null':
        emitter.emit(line, start_pos, len(value), TokenType.RATIO_STRING)
        return
    
    # String (default)
    # Check for escape sequences or brackets within the string
    if '\\' in value or '[' in value or ']' in value or '{' in value or '}' in value:
        _emit_string_with_escapes(value, line, start_pos, emitter)
    else:
        emitter.emit(line, start_pos, len(value), TokenType.STRING)


def _emit_string_with_escapes(value: str, line: int, start_pos: int, emitter: TokenEmitter):
    """
    Emit string token with escape sequence tokens.
    Also emits individual tokens for brackets/braces to prevent TextMate from coloring them as structural.
    """
    pos = 0
    last_emit = 0
    
    while pos < len(value):
        # Handle escape sequences
        if value[pos] == '\\' and pos + 1 < len(value):
            # Emit string before escape
            if pos > last_emit:
                emitter.emit(line, start_pos + last_emit, pos - last_emit, TokenType.STRING)
            
            # Check what kind of escape
            next_char = value[pos + 1]
            if next_char in 'ntr\\\'"':
                # Known escape
                emitter.emit(line, start_pos + pos, 2, TokenType.ESCAPE_SEQUENCE)
                pos += 2
                last_emit = pos
            elif next_char == 'u' and pos + 5 < len(value):
                # Unicode escape \uXXXX
                emitter.emit(line, start_pos + pos, 6, TokenType.ESCAPE_SEQUENCE)
                pos += 6
                last_emit = pos
            else:
                # Unknown escape, treat as string
                pos += 1
        # Handle brackets/braces - emit them individually with specific types
        elif value[pos] in '[]{}':
            # Emit string before bracket/brace
            if pos > last_emit:
                emitter.emit(line, start_pos + last_emit, pos - last_emit, TokenType.STRING)
            
            # Emit the bracket/brace with a specific token type to override VSCode's bracket matcher
            if value[pos] in '[]':
                emitter.emit(line, start_pos + pos, 1, TokenType.STRING_BRACKET)
            else:  # '{' or '}'
                emitter.emit(line, start_pos + pos, 1, TokenType.STRING_BRACE)
            pos += 1
            last_emit = pos
        else:
            pos += 1
    
    # Emit remaining string
    if last_emit < len(value):
        emitter.emit(line, start_pos + last_emit, len(value) - last_emit, TokenType.STRING)


def _emit_array_tokens(value: str, line: int, start_pos: int, emitter: TokenEmitter):
    """Emit tokens for array syntax [...]."""
    # Opening bracket
    emitter.emit(line, start_pos, 1, TokenType.BRACKET_STRUCTURAL)
    
    # Parse inner content
    inner = value[1:-1].strip()
    if inner:
        # Split array items at top-level commas (respecting nesting)
        items = []
        depth = 0
        item_start = 0
        
        for i, char in enumerate(inner):
            if char in '[{':
                depth += 1
            elif char in ']}':
                depth -= 1
            elif char == ',' and depth == 0:
                # Found item boundary
                item = inner[item_start:i].strip()
                if item:
                    items.append((item, start_pos + 1 + item_start + (len(inner[item_start:i]) - len(item))))
                # Emit comma
                emitter.emit(line, start_pos + 1 + i, 1, TokenType.COMMA)
                item_start = i + 1
        
        # Last item
        item = inner[item_start:].strip()
        if item:
            items.append((item, start_pos + 1 + item_start + (len(inner[item_start:]) - len(item))))
        
        # Recursively emit tokens for each item
        for item, item_pos in items:
            _emit_value_tokens(item, line, item_pos, emitter)
    
    # Closing bracket
    emitter.emit(line, start_pos + len(value) - 1, 1, TokenType.BRACKET_STRUCTURAL)


def _emit_object_tokens(value: str, line: int, start_pos: int, emitter: TokenEmitter):
    """Emit tokens for object syntax {...}."""
    # Opening brace
    emitter.emit(line, start_pos, 1, TokenType.BRACE_STRUCTURAL)
    
    # Parse inner content
    inner = value[1:-1].strip()
    if inner:
        # Split object pairs at top-level commas (respecting nesting)
        pairs = []
        depth = 0
        pair_start = 0
        
        for i, char in enumerate(inner):
            if char in '[{':
                depth += 1
            elif char in ']}':
                depth -= 1
            elif char == ',' and depth == 0:
                # Found pair boundary
                pair = inner[pair_start:i].strip()
                if pair and ':' in pair:
                    pairs.append((pair, start_pos + 1 + pair_start + (len(inner[pair_start:i]) - len(pair))))
                # Emit comma
                emitter.emit(line, start_pos + 1 + i, 1, TokenType.COMMA)
                pair_start = i + 1
        
        # Last pair
        pair = inner[pair_start:].strip()
        if pair and ':' in pair:
            pairs.append((pair, start_pos + 1 + pair_start + (len(inner[pair_start:]) - len(pair))))
        
        # Emit tokens for each key-value pair
        for pair, pair_pos in pairs:
            # Split on first colon (respecting nesting)
            depth = 0
            colon_idx = -1
            for i, char in enumerate(pair):
                if char in '[{':
                    depth += 1
                elif char in ']}':
                    depth -= 1
                elif char == ':' and depth == 0:
                    colon_idx = i
                    break
            
            if colon_idx >= 0:
                key = pair[:colon_idx].strip()
                val = pair[colon_idx + 1:].strip()
                
                # Calculate key position
                key_offset = len(pair[:colon_idx]) - len(key)
                key_pos = pair_pos + key_offset
                
                # Emit key token (nested key in flow-style objects)
                emitter.emit(line, key_pos, len(key), TokenType.NESTED_KEY)
                
                # Emit colon
                emitter.emit(line, pair_pos + colon_idx, 1, TokenType.COLON)
                
                # Emit value token (recursively)
                if val:
                    val_offset = len(pair[:colon_idx + 1]) + (len(pair[colon_idx + 1:]) - len(val))
                    val_pos = pair_pos + val_offset
                    _emit_value_tokens(val, line, val_pos, emitter)
    
    # Closing brace
    emitter.emit(line, start_pos + len(value) - 1, 1, TokenType.BRACE_STRUCTURAL)


def _validate_ascii_only(value: str, line_num: int = None) -> None:
    """
    Validate that value contains only ASCII characters (RFC 8259 compliance).
    
    Non-ASCII characters (emojis, accented letters, etc.) are detected and
    a helpful error message suggests the proper Unicode escape format.
    
    This provides error-driven education:
    - User can naturally type/paste emojis: icon: ♥️
    - Parser catches it and suggests: icon: \\u2764\\uFE0F
    - User learns the RFC 8259 compliant format
    - No IDE integration needed!
    
    Args:
        value: String value to validate
        line_num: Optional line number for error messages
    
    Raises:
        ZoloParseError: If non-ASCII characters are detected
    
    Examples:
        >>> _validate_ascii_only("hello")  # OK
        >>> _validate_ascii_only("♥️")  # Raises error with suggestion
    """
    for i, char in enumerate(value):
        if ord(char) > 127:  # Non-ASCII detected
            # Convert character to Unicode escape sequence
            codepoint = ord(char)
            
            if codepoint <= 0xFFFF:
                # Basic Multilingual Plane (most characters)
                escape = f"\\u{codepoint:04X}"
            else:
                # Supplementary plane (emojis, etc.) - use surrogate pair
                # Formula: U+10000 to U+10FFFF
                high_surrogate = ((codepoint - 0x10000) >> 10) + 0xD800
                low_surrogate = ((codepoint - 0x10000) & 0x3FF) + 0xDC00
                escape = f"\\u{high_surrogate:04X}\\u{low_surrogate:04X}"
            
            # Get character name for better error message
            char_name = None
            try:
                import unicodedata
                char_name = unicodedata.name(char, None)
            except:
                pass
            
            # Build helpful error message
            line_info = f" at line {line_num}" if line_num else ""
            char_desc = f" ({char_name})" if char_name else ""
            
            error_msg = (
                f"Non-ASCII character '{char}' detected{line_info}.\n"
                f"Unicode: U+{codepoint:04X}{char_desc}\n"
                f"\n"
                f"RFC 8259 requires ASCII-only. Use Unicode escape instead:\n"
                f"  {escape}\n"
                f"\n"
                f"Hint: Copy the escape sequence above and replace the character.\n"
                f"      This teaches you the RFC 8259 compliant format!"
            )
            
            raise ZoloParseError(error_msg)


def _detect_value_type(value: str) -> Any:
    r"""
    .zolo String-First Type Detection.
    
    Philosophy: Safe by default, explicit when needed.
    
    Auto-Detection (RFC 8259 Primitives):
    1. Array (bracket syntax): '[...]' → list
    2. Number: Valid numeric format → float (RFC 8259 default)
    3. Null: 'null' (standalone) → None (RFC 8259 primitive)
    
    Everything Else → String (including 'true', 'false'):
    - Use type hints for explicit conversion: (bool), (int), (str)
    - Booleans need hints (they're ambiguous words in natural language)
    - This prevents YAML-style surprises (NO → False, yes → True)
    - Values are predictable and safe
    
    Edge Cases:
    - Empty value (no value after colon) → '' (empty string)
    - 'null value' (null with other text) → 'null value' (string)
    
    Multi-line Support:
    - \n escape sequences are converted to actual newlines
    
    Anti-Quirk Rules:
    - '00123' (leading zero) → string (NOT octal)
    - '1.0.0' → string (NOT number)
    - 'NO', 'YES', 'true', 'false' → strings (use type hints!)
    
    Args:
        value: String value to detect and convert
    
    Returns:
        Typed value (list, float, None, or str)
    
    Examples:
        >>> _detect_value_type('5000')
        5000.0
        >>> _detect_value_type('null')
        None
        >>> _detect_value_type('true')
        'true'
        >>> _detect_value_type('')
        ''
    """
    # Validate ASCII-only BEFORE any processing (RFC 8259 compliance)
    # This catches emojis/non-ASCII and provides helpful error with \uXXXX suggestion
    _validate_ascii_only(value)
    
    # Empty value (key: with nothing after) → empty string
    if not value:
        return ''
    
    # Array (bracket syntax)
    if value.startswith('[') and value.endswith(']'):
        return _parse_bracket_array(value)
    
    # Object (brace syntax - flow-style)
    if value.startswith('{') and value.endswith('}'):
        return _parse_brace_object(value)
    
    # Number (RFC 8259: all numbers → float)
    if _is_valid_number(value):
        return float(value)
    
    # Null (RFC 8259 primitive) - standalone only!
    if value == 'null':
        return None
    
    # String (DEFAULT - everything else!)
    # This includes: 'true', 'false', 'yes', 'no', 'null value', etc.
    
    # Step 1: Decode Unicode escapes (\uXXXX) - RFC 8259 compliance
    if '\\u' in value:
        value = _decode_unicode_escapes(value)
    
    # Step 2: Process other escape sequences (\n, \t, etc.)
    value = _process_escape_sequences(value)
    
    return value


def _parse_brace_object(value: str) -> dict:
    """
    Parse object with brace syntax {key: value, key2: value2}.
    
    Rules:
    - Strip outer braces { and }
    - Split on commas (top-level only)
    - Each item is key: value
    - Apply type detection recursively
    - Handle empty objects {}
    
    Args:
        value: String like '{x: 10, y: 20}' or '{}'
    
    Returns:
        Dictionary with typed values
    
    Examples:
        >>> _parse_brace_object('{x: 10, y: 20}')
        {'x': 10.0, 'y': 20.0}
        
        >>> _parse_brace_object('{name: Alice, active: true}')
        {'name': 'Alice', 'active': 'true'}
        
        >>> _parse_brace_object('{}')
        {}
    """
    # Strip outer braces
    inner = value[1:-1].strip()
    
    # Empty object
    if not inner:
        return {}
    
    # Parse key-value pairs
    result = {}
    seen_keys = {}  # Track duplicates: {clean_key: original_key}
    
    # Split on commas, but respect nested brackets/braces
    pairs = _split_on_comma(inner)
    
    for pair in pairs:
        pair = pair.strip()
        if ':' in pair:
            # Split on first colon
            key, _, val = pair.partition(':')
            key = key.strip()
            val = val.strip()
            
            # Strip type hint from key for duplicate checking
            match = TYPE_HINT_PATTERN.match(key)
            clean_key = match.group(1) if match else key
            
            # Check for duplicate keys (STRICT MODE - Phase 4.7)
            if clean_key in seen_keys:
                first_key = seen_keys[clean_key]
                raise ZoloParseError(
                    f"Duplicate key '{clean_key}' in flow-style object: {value}\n"
                    f"First occurrence: '{first_key}', duplicate: '{key}'.\n"
                    f"Keys must be unique within the same object."
                )
            
            seen_keys[clean_key] = key
            
            # Recursively detect type for value
            typed_value = _detect_value_type(val)
            result[key] = typed_value
    
    return result


def _split_on_comma(text: str) -> list[str]:
    """
    Split text on commas, but respect nested brackets/braces.
    
    Args:
        text: Text to split
    
    Returns:
        List of parts split on top-level commas
    
    Examples:
        >>> _split_on_comma('a, b, c')
        ['a', 'b', 'c']
        
        >>> _split_on_comma('a: [1, 2], b: 3')
        ['a: [1, 2]', 'b: 3']
    """
    parts = []
    current = []
    depth = 0  # Track nesting depth
    
    for char in text:
        if char in '[{':
            depth += 1
            current.append(char)
        elif char in ']}':
            depth -= 1
            current.append(char)
        elif char == ',' and depth == 0:
            # Top-level comma - split here
            parts.append(''.join(current))
            current = []
        else:
            current.append(char)
    
    # Add final part
    if current:
        parts.append(''.join(current))
    
    return parts


def _decode_unicode_escapes(value: str) -> str:
    r"""
    Decode Unicode escape sequences to actual characters.
    
    Supports:
    - Basic Unicode: copyright symbol, accented characters
    - Emoji (surrogate pairs): multi-byte emoji
    - Multiple escapes in one string
    
    This is the RFC 8259 compliant way to represent Unicode in .zolo files.
    The VSCode extension provides a zEmoji helper to make writing these easier.
    
    Args:
        value: String that may contain Unicode escape sequences
    
    Returns:
        String with Unicode escapes decoded to actual characters
    
    Examples:
        Copyright: escape code to symbol
        Café: escape code to accented e
        Emoji: surrogate pair to emoji character
    """
    # Use Python's unicode_escape codec to decode
    # This handles both basic Unicode and surrogate pairs correctly
    try:
        # Encode as bytes, then decode using unicode_escape codec
        # This properly handles surrogate pairs for emoji
        result = value.encode('utf-8').decode('unicode_escape')
        # Re-encode and decode to handle any remaining issues
        result = result.encode('utf-16', 'surrogatepass').decode('utf-16')
        return result
    except Exception:
        # If decoding fails, return original value
        return value


def _process_escape_sequences(value: str) -> str:
    r"""
    Process escape sequences in strings - PERMISSIVE approach.
    
    Known escapes (processed):
    - \n → newline
    - \t → tab
    - \r → carriage return (zDisplay terminal control!)
    - \\ → backslash
    - \" → double quote
    - \' → single quote
    
    Unknown escapes (preserved as-is):
    - \d, \w, \x → Kept literal for regex, Windows paths
    - Example: "C:\Windows" → "C:\\Windows" (works!)
    
    Args:
        value: String that may contain escape sequences
    
    Returns:
        String with escape sequences processed
    
    Note:
        \uXXXX Unicode escapes are handled by _decode_unicode_escapes()
        before this function is called.
    """
    # Replace escape sequences (order matters - \\ must be after others)
    value = value.replace('\\n', '\n')
    value = value.replace('\\t', '\t')
    value = value.replace('\\r', '\r')
    value = value.replace('\\\\', '\\')
    value = value.replace('\\"', '"')
    value = value.replace("\\'", "'")
    
    # Unknown escapes already preserved as-is (string-first!)
    return value


def _is_valid_number(value: str) -> bool:
    r"""
    Check if value is a valid RFC 8259 number.
    
    Rules:
    - Must match: -?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?
    - Anti-quirk: NO leading zeros (except '0' or '0.x')
    
    Valid:
        5000, -42, 0, 30.5, 1.5e10, 2E-3, 0.5
    
    Invalid (Anti-Quirk):
        00123 (leading zero), 01 (leading zero), 1.0.0 (multiple dots)
    
    Args:
        value: String to check
    
    Returns:
        True if valid number, False otherwise
    """
    if not value:
        return False
    
    # Anti-quirk: Check for leading zeros (except '0' or '0.something')
    if len(value) > 1 and value[0] == '0' and value[1].isdigit():
        # This is like '00123' or '01' - NOT a valid number
        return False
    
    # Try to parse as float
    try:
        float(value)
        return True
    except ValueError:
        return False


def _parse_bracket_array(value: str) -> list:
    """
    Phase 2, Step 2.1: Parse array with bracket syntax [item1, item2, item3].
    
    Rules:
    - Strip outer brackets [ and ]
    - Split on top-level commas (respect nested brackets/braces)
    - Trim whitespace from each item
    - Apply type detection to each item recursively
    - Handle empty arrays []
    
    Args:
        value: String like '[1, 2, 3]' or '[[1, 2], [3, 4]]'
    
    Returns:
        List with typed items
    
    Examples:
        >>> _parse_bracket_array('[1, 2, 3]')
        [1.0, 2.0, 3.0]
        
        >>> _parse_bracket_array('[python, yaml, test]')
        ['python', 'yaml', 'test']
        
        >>> _parse_bracket_array('[[1, 2], [3, 4]]')
        [[1.0, 2.0], [3.0, 4.0]]
        
        >>> _parse_bracket_array('[]')
        []
    """
    # Strip outer brackets
    inner = value[1:-1].strip()
    
    # Empty array
    if not inner:
        return []
    
    # Split on top-level commas (respect nesting)
    items = []
    for item in _split_on_comma(inner):
        item = item.strip()
        # Recursively detect type for each item
        typed_item = _detect_value_type(item)
        items.append(typed_item)
    
    return items


def dump(data: Any, fp: Union[str, Path, IO], file_extension: Optional[str] = None, **kwargs) -> None:
    """
    Dump data to a .zolo file (or compatible format).
    
    Args:
        data: Data to dump (dict, list, or scalar)
        fp: File path (str/Path) or file-like object
        file_extension: Optional file extension override (.zolo, .yaml, .json)
                       If None, will detect from file path or default to .zolo
        **kwargs: Additional arguments passed to YAML/JSON dumper
                 For YAML: default_flow_style=False, allow_unicode=True
                 For JSON: indent=2, ensure_ascii=False
    
    Raises:
        ZoloDumpError: If dumping fails
    
    Examples:
        >>> data = {'port': 8080, 'enabled': True}
        >>> zolo.dump(data, 'config.zolo')
        
        >>> # Dump as JSON
        >>> zolo.dump(data, 'config.json')
        
        >>> # Dump with custom kwargs
        >>> zolo.dump(data, 'config.yaml', default_flow_style=True)
    """
    # Convert to string
    content = dumps(data, file_extension=file_extension, **kwargs)
    
    # Handle file path vs file-like object
    if isinstance(fp, (str, Path)):
        file_path = Path(fp)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise ZoloDumpError(f"Error writing file {file_path}: {e}") from e
    else:
        # File-like object
        try:
            fp.write(content)
        except Exception as e:
            raise ZoloDumpError(f"Error writing to file object: {e}") from e


def dumps(data: Any, file_extension: Optional[str] = None, **kwargs) -> str:
    """
    Dump data to a .zolo string (or compatible format).
    
    Args:
        data: Data to dump (dict, list, or scalar)
        file_extension: Optional file extension hint (.zolo, .yaml, .json)
                       Defaults to .zolo if not provided
        **kwargs: Additional arguments passed to YAML/JSON dumper
    
    Returns:
        Formatted string
    
    Raises:
        ZoloDumpError: If dumping fails
    
    Examples:
        >>> data = {'port': 8080, 'enabled': True}
        >>> print(zolo.dumps(data))
        port: 8080
        enabled: true
        
        >>> # Dump as JSON
        >>> print(zolo.dumps(data, file_extension='.json'))
        {
          "port": 8080,
          "enabled": true
        }
    """
    # Default to .zolo if not specified
    if file_extension is None:
        file_extension = FILE_EXT_ZOLO
    
    # Normalize extension
    file_extension = file_extension.lower()
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension
    
    # Dump based on format
    try:
        if file_extension == FILE_EXT_JSON:
            # Dump as JSON
            json_kwargs = {
                'indent': 2,
                'ensure_ascii': False,
            }
            json_kwargs.update(kwargs)
            return json.dumps(data, **json_kwargs)
        else:
            # Dump as YAML (default for .zolo, .yaml, .yml)
            yaml_kwargs = {
                'default_flow_style': False,
                'allow_unicode': True,
                'sort_keys': False,
            }
            yaml_kwargs.update(kwargs)
            return yaml.dump(data, **yaml_kwargs)
    
    except Exception as e:
        raise ZoloDumpError(f"Dumping error: {e}") from e
