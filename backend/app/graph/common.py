from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CallEdge:
    file_path: str
    caller_name: str
    caller_parent_class: Optional[str]
    callee_name: str
    call_type: str          # plain, self_method, attribute
    resolved: bool
    target_name: Optional[str]
    target_parent_class: Optional[str]
    object_name: Optional[str] = None   
    target_file: Optional[str] = None 