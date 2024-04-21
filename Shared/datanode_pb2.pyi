from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StoreBlockRequest(_message.Message):
    __slots__ = ("block_id", "data")
    BLOCK_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    block_id: str
    data: bytes
    def __init__(self, block_id: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...

class StoreBlockResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class RetrieveBlockRequest(_message.Message):
    __slots__ = ("block_id",)
    BLOCK_ID_FIELD_NUMBER: _ClassVar[int]
    block_id: str
    def __init__(self, block_id: _Optional[str] = ...) -> None: ...

class RetrieveBlockResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...
