extension microsoftGraphV1

@description('Stable unique name prefix for the CMDB Entra application.')
param namePrefix string

@description('Public HTTPS endpoint of the Container App.')
param webEndpoint string

@description('Principal ID of the Container App authentication managed identity.')
param authIdentityPrincipalId string

var readerRoleId = guid('enterprise-cmdb', 'CMDB.Reader')
var adminRoleId = guid('enterprise-cmdb', 'CMDB.Admin')
var issuer = '${environment().authentication.loginEndpoint}${tenant().tenantId}/v2.0'

resource clientApp 'Microsoft.Graph/applications@v1.0' = {
  uniqueName: '${namePrefix}-enterprise-cmdb'
  displayName: '${namePrefix} Enterprise CMDB'
  signInAudience: 'AzureADMyOrg'
  appRoles: [
    {
      allowedMemberTypes: [
        'User'
      ]
      description: 'Read CMDB environments, teams, services, assets, relations, and audit records.'
      displayName: 'CMDB Reader'
      id: readerRoleId
      isEnabled: true
      value: 'CMDB.Reader'
    }
    {
      allowedMemberTypes: [
        'User'
      ]
      description: 'Read and change CMDB configuration through audited APIs.'
      displayName: 'CMDB Admin'
      id: adminRoleId
      isEnabled: true
      value: 'CMDB.Admin'
    }
  ]
  web: {
    redirectUris: [
      '${webEndpoint}/.auth/login/aad/callback'
    ]
    implicitGrantSettings: {
      enableIdTokenIssuance: true
    }
  }

  resource managedIdentityFederation 'federatedIdentityCredentials@v1.0' = {
    name: '${clientApp.uniqueName}/container-app-auth'
    audiences: [
      'api://AzureADTokenExchange'
    ]
    issuer: issuer
    subject: authIdentityPrincipalId
  }
}

resource clientServicePrincipal 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: clientApp.appId
  appRoleAssignmentRequired: true
}

output clientAppId string = clientApp.appId
output servicePrincipalId string = clientServicePrincipal.id
output readerRoleId string = readerRoleId
output adminRoleId string = adminRoleId
output openIdIssuer string = issuer
