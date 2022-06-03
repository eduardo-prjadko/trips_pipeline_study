from dataclasses import dataclass
from dataclasses import field
from typing import List

from pulumi_azure_native import storage


@dataclass
class ContainerDef:

    name: str
    obj: storage.BlobContainer = None

@dataclass
class QueueDef:

    name: str
    obj: storage.Queue = None

@dataclass
class StorageDef:

    name: str
    obj: storage.StorageAccount = None
    containers: List[ContainerDef] = field(default_factory=list)
    queues: List[QueueDef] = field(default_factory=list)
