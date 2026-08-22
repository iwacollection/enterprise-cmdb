targetScope = 'resourceGroup'

@description('Short alphanumeric prefix used for Azure resource names.')
param namePrefix string = 'cmdb'

@description('Azure region for all regional resources.')
param location string = resourceGroup().location

@description('Container image to run. Required only when deployContainerApp is true.')
param containerImage string = ''

@description('Create or update the Container App after its image has been pushed to ACR.')
param deployContainerApp bool = false

@description('Expose the Container App outside the Container Apps environment. Keep false until an authentication policy is configured.')
param externalIngressEnabled bool = false

@description('PostgreSQL administrator login.')
param postgresAdministratorLogin string = 'cmdbadmin'

@secure()
@description('PostgreSQL administrator password.')
param postgresAdministratorPassword string

@description('PostgreSQL backup retention in days.')
@minValue(7)
@maxValue(35)
param backupRetentionDays int = 7

@description('Minimum application replicas.')
@minValue(1)
param minReplicas int = 1

@description('Maximum application replicas.')
@minValue(1)
param maxReplicas int = 3

var suffix = uniqueString(resourceGroup().id)
var acrName = toLower('${namePrefix}${suffix}')
var postgresServerName = toLower('${namePrefix}-pg-${suffix}')
var appResourceName = '${namePrefix}-app'
var databaseName = 'cmdb'
var privateDnsZoneName = 'privatelink.postgres.database.azure.com'
var acrPullRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '7f951dda-4ed3-4680-a7ca-43fe172d538d'
)

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: '${namePrefix}-vnet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.42.0.0/16'
      ]
    }
  }
}

resource containerAppsSubnet 'Microsoft.Network/virtualNetworks/subnets@2024-05-01' = {
  parent: vnet
  name: 'container-apps'
  properties: {
    addressPrefix: '10.42.0.0/23'
    delegations: [
      {
        name: 'container-apps-environment'
        properties: {
          serviceName: 'Microsoft.App/environments'
        }
      }
    ]
  }
}

resource postgresSubnet 'Microsoft.Network/virtualNetworks/subnets@2024-05-01' = {
  parent: vnet
  name: 'postgresql'
  properties: {
    addressPrefix: '10.42.4.0/24'
    delegations: [
      {
        name: 'postgresql-flexible-server'
        properties: {
          serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
        }
      }
    ]
  }
}

resource postgresPrivateDns 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: privateDnsZoneName
  location: 'global'
}

resource postgresPrivateDnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: postgresPrivateDns
  name: '${namePrefix}-postgres-link'
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnet.id
    }
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${namePrefix}-logs-${suffix}'
  location: location
  properties: {
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2026-01-01' = {
  name: '${namePrefix}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
    vnetConfiguration: {
      infrastructureSubnetId: containerAppsSubnet.id
      internal: false
    }
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
        minimumCount: 0
        maximumCount: 0
      }
    ]
  }
}

resource acr 'Microsoft.ContainerRegistry/registries@2025-11-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    anonymousPullEnabled: false
    dataEndpointEnabled: false
    publicNetworkAccess: 'Enabled'
    roleAssignmentMode: 'LegacyRegistryPermissions'
    zoneRedundancy: 'Disabled'
  }
}

resource containerPullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: '${namePrefix}-pull-identity'
  location: location
}

resource acrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, containerPullIdentity.id, 'acrpull')
  scope: acr
  properties: {
    roleDefinitionId: acrPullRoleDefinitionId
    principalId: containerPullIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2025-08-01' = {
  name: postgresServerName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: postgresAdministratorLogin
    administratorLoginPassword: postgresAdministratorPassword
    version: '16'
    backup: {
      backupRetentionDays: backupRetentionDays
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    network: {
      delegatedSubnetResourceId: postgresSubnet.id
      privateDnsZoneArmResourceId: postgresPrivateDns.id
      publicNetworkAccess: 'Disabled'
    }
    storage: {
      autoGrow: 'Enabled'
      storageSizeGB: 32
    }
  }
  dependsOn: [
    postgresPrivateDnsLink
  ]
}

resource postgresDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2025-08-01' = {
  parent: postgresServer
  name: databaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

var databaseEnvironment = [
  {
    name: 'CMDB_DB_HOST'
    value: postgresServer.properties.fullyQualifiedDomainName
  }
  {
    name: 'CMDB_DB_PORT'
    value: '5432'
  }
  {
    name: 'CMDB_DB_USER'
    value: postgresAdministratorLogin
  }
  {
    name: 'CMDB_DB_PASSWORD'
    secretRef: 'postgres-password'
  }
  {
    name: 'CMDB_DB_NAME'
    value: databaseName
  }
]

resource containerApp 'Microsoft.App/containerApps@2026-01-01' = if (deployContainerApp) {
  name: appResourceName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${containerPullIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: externalIngressEnabled
        allowInsecure: false
        targetPort: 8000
        transport: 'http'
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: acr.properties.loginServer
          identity: containerPullIdentity.id
        }
      ]
      secrets: [
        {
          name: 'postgres-password'
          value: postgresAdministratorPassword
        }
      ]
    }
    template: {
      initContainers: [
        {
          name: 'migrate'
          image: containerImage
          command: [
            'uv'
            'run'
            'alembic'
            'upgrade'
            'head'
          ]
          env: databaseEnvironment
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
      containers: [
        {
          name: 'cmdb'
          image: containerImage
          env: databaseEnvironment
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/ready'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 5
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
      }
    }
  }
  dependsOn: [
    acrPullAssignment
    postgresDatabase
  ]
}

output acrName string = acr.name
output acrLoginServer string = acr.properties.loginServer
output postgresHost string = postgresServer.properties.fullyQualifiedDomainName
output containerAppName string = appResourceName
