# zDisplay Shared Constants

# Subsystem Configuration
SUBSYSTEM_NAME = "zDisplay"
READY_MESSAGE = "ZDISPLAY Ready"
DEFAULT_COLOR = "ZDISPLAY"
DEFAULT_MODE = "Terminal"

# Display Modes
MODE_TERMINAL = "Terminal"
MODE_WALKER = "Walker"
MODE_EMPTY = ""

# Event Names - Output Events
EVENT_TEXT = "text"
EVENT_RICH_TEXT = "rich_text"
EVENT_HEADER = "header"
EVENT_LINE = "line"

# Event Names - Signal Events
EVENT_ERROR = "error"
EVENT_WARNING = "warning"
EVENT_SUCCESS = "success"
EVENT_INFO = "info"
EVENT_ZMARKER = "zMarker"

# Event Names - Data Events
EVENT_LIST = "list"
EVENT_OUTLINE = "outline"
EVENT_JSON = "json"
EVENT_JSON_DATA = "json_data"
EVENT_ZTABLE = "zTable"

# Event Names - Media Events
EVENT_IMAGE = "image"
EVENT_VIDEO = "video"
EVENT_AUDIO = "audio"
EVENT_PICTURE = "picture"

# Event Names - System Events
EVENT_ZDECLARE = "zDeclare"
EVENT_ZSESSION = "zSession"
EVENT_ZCONFIG = "zConfig"
EVENT_ZCRUMBS = "zCrumbs"
EVENT_ZMENU = "zMenu"
EVENT_ZDASH = "zDash"
EVENT_ZDIALOG = "zDialog"

# Event Names - Widget Events
EVENT_PROGRESS_BAR = "progress_bar"
EVENT_SPINNER = "spinner"
EVENT_PROGRESS_ITERATOR = "progress_iterator"
EVENT_INDETERMINATE_PROGRESS = "indeterminate_progress"

# Event Names - Input Events
EVENT_SELECTION = "selection"
EVENT_READ_STRING = "read_string"
EVENT_READ_PASSWORD = "read_password"
EVENT_BUTTON = "button"
EVENT_LINK = "link"

# Event Names - Primitive Events
EVENT_WRITE_RAW = "write_raw"
EVENT_WRITE_LINE = "write_line"
EVENT_WRITE_BLOCK = "write_block"

# Event Type Constants (WebSocket/Bifrost)
EVENT_TYPE_OUTPUT = "output"
EVENT_TYPE_INPUT_REQUEST = "input_request"
EVENT_TYPE_ZDISPLAY = "zdisplay"

# Write Type Constants
WRITE_TYPE_RAW = "raw"
WRITE_TYPE_LINE = "line"
WRITE_TYPE_BLOCK = "block"

# Input Type Constants
INPUT_TYPE_STRING = "string"
INPUT_TYPE_PASSWORD = "password"

# JSON Key Constants (Internal)
_KEY_EVENT = "event"
_KEY_TYPE = "type"
_KEY_CONTENT = "content"
_KEY_TIMESTAMP = "timestamp"
_KEY_REQUEST_ID = "requestId"
_KEY_PROMPT = "prompt"
_KEY_DISPLAY_EVENT = "display_event"
_KEY_DATA = "data"
_KEY_MASKED = "masked"

# Default Values (Internal)
_DEFAULT_PROMPT = ""
_DEFAULT_FLUSH = True

# Terminal Sizing (Internal)
_TERMINAL_COLS_DEFAULT = 80
_TERMINAL_COLS_MIN = 60
_TERMINAL_COLS_MAX = 120

# Error Messages (Internal)
_ERR_INVALID_OBJ = "zDisplay.handle() requires dict, got %s"
_ERR_MISSING_EVENT = "zDisplay event missing 'event' key"
_ERR_UNKNOWN_EVENT = "Unknown zDisplay event: %s"
_ERR_INVALID_PARAMS = "Invalid parameters for event '%s': %s"

