import enum


class CommandType(str, enum.Enum):
    FULL_REFRESH = "fullRefresh"
    NEW_TAG = "newTag"
    PANE = "pane"


class BroadcastMessageType(str, enum.Enum):
    RELOAD = "reload"
