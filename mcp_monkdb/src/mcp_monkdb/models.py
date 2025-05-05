from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Column:
    table_schema: str
    table_name: str
    column_name: str
    data_type: str
    is_nullable: str
    column_default: Optional[str] = None


@dataclass
class Table:
    table_schema: str
    table_name: str
    table_type: str
    number_of_shards: Optional[int] = None
    number_of_replicas: Optional[str] = None
    clustered_by: Optional[str] = None
    created: Optional[str] = None
    columns: List[Column] = field(default_factory=list)
