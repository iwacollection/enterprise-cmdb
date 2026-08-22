#!/usr/bin/env bash
set -euo pipefail

REPO="${CMDB_GITHUB_REPO:-iwacollection/enterprise-cmdb}"
GITHUB_ENVIRONMENT="${CMDB_GITHUB_ENVIRONMENT:-production}"
RESOURCE_GROUP="${CMDB_RESOURCE_GROUP:-rg-enterprise-cmdb}"
LOCATION="${CMDB_LOCATION:-eastasia}"
NAME_PREFIX="${CMDB_NAME_PREFIX:-cmdb}"
DEPLOY_APP_NAME="${CMDB_DEPLOY_APP_NAME:-github-enterprise-cmdb-deployer}"
FIC_NAME="github-${GITHUB_ENVIRONMENT}"
GRAPH_APP_ID="00000003-0000-0000-c000-000000000000"

for command in az gh jq openssl; do
  command -v "$command" >/dev/null
done

az account show >/dev/null
gh auth status >/dev/null

SUBSCRIPTION_ID=$(az account show --query id --output tsv)
TENANT_ID=$(az account show --query tenantId --output tsv)
SUBSCRIPTION_SCOPE="/subscriptions/${SUBSCRIPTION_ID}"

mapfile -t DEPLOY_APP_IDS < <(
  az ad app list \
    --display-name "$DEPLOY_APP_NAME" \
    --query '[].appId' \
    --output tsv
)

if [ "${#DEPLOY_APP_IDS[@]}" -eq 0 ]; then
  CLIENT_ID=$(az ad app create \
    --display-name "$DEPLOY_APP_NAME" \
    --sign-in-audience AzureADMyOrg \
    --query appId \
    --output tsv)
elif [ "${#DEPLOY_APP_IDS[@]}" -eq 1 ]; then
  CLIENT_ID="${DEPLOY_APP_IDS[0]}"
else
  echo "Multiple Entra applications named '$DEPLOY_APP_NAME' exist; refusing to choose one." >&2
  exit 1
fi

SP_OBJECT_ID=$(az ad sp list \
  --filter "appId eq '$CLIENT_ID'" \
  --query '[0].id' \
  --output tsv)

if [ -z "$SP_OBJECT_ID" ]; then
  SP_OBJECT_ID=$(az ad sp create \
    --id "$CLIENT_ID" \
    --query id \
    --output tsv)
fi

EXPECTED_SUBJECT="repo:${REPO}:environment:${GITHUB_ENVIRONMENT}"
EXISTING_SUBJECT=$(az ad app federated-credential list \
  --id "$CLIENT_ID" \
  --query "[?name=='${FIC_NAME}'] | [0].subject" \
  --output tsv)

if [ -z "$EXISTING_SUBJECT" ]; then
  az ad app federated-credential create \
    --id "$CLIENT_ID" \
    --parameters "{\"name\":\"${FIC_NAME}\",\"issuer\":\"https://token.actions.githubusercontent.com\",\"subject\":\"${EXPECTED_SUBJECT}\",\"audiences\":[\"api://AzureADTokenExchange\"]}" \
    --output none
elif [ "$EXISTING_SUBJECT" != "$EXPECTED_SUBJECT" ]; then
  echo "Federated credential '$FIC_NAME' exists with unexpected subject '$EXISTING_SUBJECT'." >&2
  exit 1
fi

az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none
RESOURCE_GROUP_ID=$(az group show --name "$RESOURCE_GROUP" --query id --output tsv)

for role in "Contributor" "Role Based Access Control Administrator" "AcrPush"; do
  assignment_count=$(az role assignment list \
    --assignee "$SP_OBJECT_ID" \
    --scope "$RESOURCE_GROUP_ID" \
    --query "[?roleDefinitionName=='${role}'] | length(@)" \
    --output tsv)
  if [ "$assignment_count" = "0" ]; then
    az role assignment create \
      --assignee-object-id "$SP_OBJECT_ID" \
      --assignee-principal-type ServicePrincipal \
      --role "$role" \
      --scope "$RESOURCE_GROUP_ID" \
      --output none
  fi
done

quota_assignment_count=$(az role assignment list \
  --assignee "$SP_OBJECT_ID" \
  --scope "$SUBSCRIPTION_SCOPE" \
  --query "[?roleDefinitionName=='Quota Request Operator'] | length(@)" \
  --output tsv)
if [ "$quota_assignment_count" = "0" ]; then
  az role assignment create \
    --assignee-object-id "$SP_OBJECT_ID" \
    --assignee-principal-type ServicePrincipal \
    --role "Quota Request Operator" \
    --scope "$SUBSCRIPTION_SCOPE" \
    --output none
fi

GRAPH_PERMISSION_ID=$(az ad sp show \
  --id "$GRAPH_APP_ID" \
  --query "appRoles[?value=='Application.ReadWrite.OwnedBy'].id | [0]" \
  --output tsv)

if [ -z "$GRAPH_PERMISSION_ID" ]; then
  echo "Microsoft Graph Application.ReadWrite.OwnedBy permission was not found." >&2
  exit 1
fi

if ! az ad app permission list --id "$CLIENT_ID" --output json | jq -e \
  --arg graph "$GRAPH_APP_ID" \
  --arg permission "$GRAPH_PERMISSION_ID" \
  'any(.[]; .resourceAppId == $graph and any(.resourceAccess[]; .id == $permission and .type == "Role"))' \
  >/dev/null; then
  az ad app permission add \
    --id "$CLIENT_ID" \
    --api "$GRAPH_APP_ID" \
    --api-permissions "${GRAPH_PERMISSION_ID}=Role" \
    --output none
fi

az ad app permission admin-consent --id "$CLIENT_ID" --output none

POSTGRES_PASSWORD="CMDB!$(openssl rand -hex 24)Aa9"

gh secret set AZURE_CLIENT_ID \
  --repo "$REPO" \
  --env "$GITHUB_ENVIRONMENT" \
  --body "$CLIENT_ID"
gh secret set AZURE_TENANT_ID \
  --repo "$REPO" \
  --env "$GITHUB_ENVIRONMENT" \
  --body "$TENANT_ID"
gh secret set AZURE_SUBSCRIPTION_ID \
  --repo "$REPO" \
  --env "$GITHUB_ENVIRONMENT" \
  --body "$SUBSCRIPTION_ID"
gh secret set AZURE_POSTGRES_ADMIN_PASSWORD \
  --repo "$REPO" \
  --env "$GITHUB_ENVIRONMENT" \
  --body "$POSTGRES_PASSWORD"
unset POSTGRES_PASSWORD

gh secret list \
  --repo "$REPO" \
  --env "$GITHUB_ENVIRONMENT"

gh workflow run deploy-azure.yml \
  --repo "$REPO" \
  --ref deploy/azure-production \
  -f resource_group="$RESOURCE_GROUP" \
  -f location="$LOCATION" \
  -f name_prefix="$NAME_PREFIX"

echo "Azure OIDC bootstrap completed and production deployment was triggered."
echo "Deployment application client ID: $CLIENT_ID"
echo "Resource-group deployment roles and subscription-level Quota Request Operator were configured."
echo "Tenant ID and subscription ID were written to GitHub environment secrets and are not printed."
