from dataclasses import dataclass
from typing import List

from pulumi_azure_native import storage


@dataclass
class ContainerDef:

    name: str
    obj: storage.BlobContainer

@dataclass
class QueueDef:

    name: str
    obj: storage.Queue

@dataclass
class StorageDef:

    name: str
    obj: storage.StorageAccount
    containers: List[ContainerDef]
    queues: List[QueueDef]
