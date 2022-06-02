import pulumi
from pulumi_azure_native import storage
from pulumi_azure_native import resources
from pulumi_azure_native import web

# Create an Azure Resource Group
resource_group = resources.ResourceGroup('trips_project')

# Create an Azure resource (Storage Account)
trips_storage = storage.StorageAccount(
    'satrips',
    resource_group_name=resource_group.name,
    sku=storage.SkuArgs(
        name=storage.SkuName.STANDARD_LRS,
    ),
    kind=storage.Kind.STORAGE_V2)

# create a storage account queue
trips_queue = storage.Queue(
    resource_name='trips-entry',
    account_name=trips_storage.name,
    resource_group_name=resource_group.name
)

# create a storage account blob storage
trips_blob_container = storage.BlobContainer(
    resource_name='01-bronze',
    account_name=trips_storage.name,
    resource_group_name=resource_group.name
)

# Create storage account for azure functions
af_storage = storage.StorageAccount('aftrips',
    resource_group_name=resource_group.name,
    sku=storage.SkuArgs(
        name=storage.SkuName.STANDARD_LRS,
    ),
    kind=storage.Kind.STORAGE_V2)

# Export the primary key of the Storage Account
trips_primary_key = pulumi.Output.all(resource_group.name, trips_storage.name) \
    .apply(lambda args: storage.list_storage_account_keys(
        resource_group_name=args[0],
        account_name=args[1]
    )).apply(lambda accountKeys: accountKeys.keys[0].value)

# Export the primary key of the Storage Account
af_primary_key = pulumi.Output.all(resource_group.name, af_storage.name) \
    .apply(lambda args: storage.list_storage_account_keys(
        resource_group_name=args[0],
        account_name=args[1]
    )).apply(lambda accountKeys: accountKeys.keys[0].value)

pulumi.export('trips_primary_storage_key', trips_primary_key)
pulumi.export('af_primary_storage_key', af_primary_key)