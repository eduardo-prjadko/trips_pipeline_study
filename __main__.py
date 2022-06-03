from collections import namedtuple

import pulumi
from pulumi_azure_native import storage
from pulumi_azure_native import resources
from pulumi_azure_native import web

from helper import (
    ContainerDef,
    QueueDef,
    StorageDef
)

# Create an Azure Resource Group
resource_group = resources.ResourceGroup('trips_project')

# create storages
apps_container = ContainerDef('00-apps')
bronze_container = ContainerDef('01-bronze')
silver_container = ContainerDef('02-silver')
gold_container = ContainerDef('03-gold')
trips_queue = QueueDef('trips-entry')
storage_trips = StorageDef(
    'satrips', 
    containers=[apps_container, bronze_container, 
        silver_container, gold_container],
    queues=[trips_queue]
)
storage_af = StorageDef('aftrips')

for stg in [storage_trips, storage_af]:
    stg.obj = storage.StorageAccount(stg.name,
        resource_group_name=resource_group.name,
        sku=storage.SkuArgs(
            name=storage.SkuName.STANDARD_LRS,
        ),
        kind=storage.Kind.STORAGE_V2)
    
    for container in stg.containers:
        container.obj = storage.BlobContainer(
            resource_name=container.name,
            account_name=stg.obj.name,
            resource_group_name=resource_group.name
        )
    
    for queue in stg.queues:
        queue.obj = storage.Queue(
            resource_name=queue.name,
            account_name=stg.obj.name,
            resource_group_name=resource_group.name
        )
    
    primary_key = pulumi.Output.all(resource_group.name, stg.obj.name) \
        .apply(lambda args: storage.list_storage_account_keys(
            resource_group_name=args[0],
            account_name=args[1]
        )).apply(lambda accountKeys: accountKeys.keys[0].value)
    stg.connection_string = pulumi.Output.all(stg.obj.name, primary_key) \
    .apply(lambda args: f'DefaultEndpointsProtocol=https;AccountName={args[0]};AccountKey={args[1]};EndpointSuffix=core.windows.net')

# upload azure functions code to blob storage
ingestion_function = storage.Blob(
    resource_name="ingestion/app.zip",
    resource_group_name=resource_group.name,
    account_name=storage_trips.obj.name,
    container_name=apps_container.obj.name,
    source=pulumi.asset.FileArchive('./ingestion-bronze')
)

# ingestion app plan
ingestion_app_plan = web.AppServicePlan(
    resource_name='plan',
    resource_group_name=resource_group.name,
    sku={'name': 'Y1', 'tier': 'dynamic'})

# ingestion function
ingestion_app = web.WebApp(
    resource_name='tripsingestion',
    resource_group_name=resource_group.name,
    server_farm_id=ingestion_app_plan.id,
    kind='functionapp',
    site_config={
        'app_settings': [
            {'name': 'AzureWebJobsStorage', 'value': storage_trips.connection_string},
            {'name': 'AzureWebJobsDATA_LAKE', 'value': storage_af.connection_string},
            {'name': 'INGESTION_CONTAINER', 'value': bronze_container.obj.name},
            {'name': 'FUNCTIONS_EXTENSION_VERSION', 'value': '~3'},
            {'name': 'FUNCTIONS_WORKER_RUNTIME', 'value': 'python'},
            {'name': 'WEBSITE_PYTHON_DEFAULT_VERSION', 'value': '~3'}
        ]
    }
)

pulumi.export('trips_connection_string', storage_trips.connection_string)
pulumi.export('af_connection_string', storage_af.connection_string)