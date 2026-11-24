from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PingRequest(_message.Message):
    __slots__ = ("sender_id", "client_send_time")
    SENDER_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SEND_TIME_FIELD_NUMBER: _ClassVar[int]
    sender_id: str
    client_send_time: float
    def __init__(self, sender_id: _Optional[str] = ..., client_send_time: _Optional[float] = ...) -> None: ...

class PingResponse(_message.Message):
    __slots__ = ("responder_id", "server_time")
    RESPONDER_ID_FIELD_NUMBER: _ClassVar[int]
    SERVER_TIME_FIELD_NUMBER: _ClassVar[int]
    responder_id: str
    server_time: float
    def __init__(self, responder_id: _Optional[str] = ..., server_time: _Optional[float] = ...) -> None: ...

class PlayRequest(_message.Message):
    __slots__ = ("sender_id", "track_path", "start_at_unix")
    SENDER_ID_FIELD_NUMBER: _ClassVar[int]
    TRACK_PATH_FIELD_NUMBER: _ClassVar[int]
    START_AT_UNIX_FIELD_NUMBER: _ClassVar[int]
    sender_id: str
    track_path: str
    start_at_unix: float
    def __init__(self, sender_id: _Optional[str] = ..., track_path: _Optional[str] = ..., start_at_unix: _Optional[float] = ...) -> None: ...

class PlayResponse(_message.Message):
    __slots__ = ("accepted", "message")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    message: str
    def __init__(self, accepted: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...

class HealthRequest(_message.Message):
    __slots__ = ("sender_id",)
    SENDER_ID_FIELD_NUMBER: _ClassVar[int]
    sender_id: str
    def __init__(self, sender_id: _Optional[str] = ...) -> None: ...

class HealthResponse(_message.Message):
    __slots__ = ("node_id", "role", "healthy", "server_time")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    SERVER_TIME_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    role: str
    healthy: bool
    server_time: float
    def __init__(self, node_id: _Optional[str] = ..., role: _Optional[str] = ..., healthy: _Optional[bool] = ..., server_time: _Optional[float] = ...) -> None: ...
