from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import traceback

from data_analysis import (
    get_avg_protein_bar,
    get_macros_heatmap,
    get_top_protein_scatter,
    get_recipe_distribution_pie,
    get_recipes,
    get_recipe_list,
    get_recipe_clusters,
)

import time
from datetime import datetime, timezone

from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient
from auth_routes import router as auth_router
import os


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "fc5ffb10-fce9-45fc-907a-b5304c376a49")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "nutrition-app-rg")
STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT", "nutritionapp2025")

PROTECTED_GROUPS = [RESOURCE_GROUP]

START_TIME = time.time()


# ─────────────────────────────────────────────
# AZURE CLIENT HELPER
# ─────────────────────────────────────────────

def get_credential():
    return DefaultAzureCredential()

def get_resource_client():
    return ResourceManagementClient(get_credential(), SUBSCRIPTION_ID)

def get_storage_client():
    return StorageManagementClient(get_credential(), SUBSCRIPTION_ID)


# ─────────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────────

app = FastAPI()
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# DATA ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/api/data/nutritional-insights")
def nutritional_insights(diet: str = None, search: str = None, limit: int = 20):
    return {"data": get_recipes(diet=diet, search=search, limit=limit)}


@app.get("/api/data/recipes")
def recipes(diet: str = None, search: str = None, limit: int = 20):
    return {"data": get_recipe_list(diet=diet, search=search, limit=limit)}


@app.get("/api/data/clusters")
def clusters(diet: str = None, search: str = None, limit: int = 50):
    return {"data": get_recipe_clusters(diet=diet, search=search, limit=limit)}


# ─────────────────────────────────────────────
# CHART ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/api/chart/protein-bar")
def protein_bar():
    return {"image": get_avg_protein_bar()}


@app.get("/api/chart/macros-heatmap")
def macros_heatmap():
    return {"image": get_macros_heatmap()}


@app.get("/api/chart/top-protein-scatter")
def top_protein_scatter():
    return {"image": get_top_protein_scatter()}


@app.get("/api/chart/recipe-distribution")
def recipe_distribution():
    return {"image": get_recipe_distribution_pie()}


# ─────────────────────────────────────────────
# SECURITY STATUS
# ─────────────────────────────────────────────

@app.get("/api/security/status")
def security_status():
    uptime_seconds = int(time.time() - START_TIME)
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60

    try:
        storage_client = get_storage_client()
        account = storage_client.storage_accounts.get_properties(
            RESOURCE_GROUP,
            STORAGE_ACCOUNT
        )

        encryption = account.encryption

        is_blob_encrypted = encryption.services.blob.enabled
        is_file_encrypted = encryption.services.file.enabled

        key_type = (
            "CMK"
            if encryption.key_source == "Microsoft.Keyvault"
            else "Microsoft-managed"
        )

        https_only = account.enable_https_traffic_only

        key_vault_uri = (
            encryption.key_vault_properties.key_vault_uri
            if encryption.key_vault_properties
            else None
        )

        access_control = {
            "status": "secure" if account.allow_blob_public_access is False else "warning",
            "checks": {
                "public_access_disabled": not account.allow_blob_public_access,
                "network_restricted": account.network_rule_set.default_action == "Deny",
                "secure_tls": account.minimum_tls_version in ["TLS1_2", "TLS1_3"],
            }
        }

        encryption_status = {
            "status": "secure" if all([
                is_blob_encrypted,
                is_file_encrypted,
                https_only
            ]) else "warning",
            "checks": {
                "blob_encrypted": is_blob_encrypted,
                "file_encrypted": is_file_encrypted,
                "https_only": https_only,
                "key_vault": key_vault_uri is not None
            }
        }

        gdpr = {
            "status": "secure",
            "message": "Infrastructure checks completed"
        }

    except Exception as e:
        encryption_status = {"status": "error", "message": str(e)}
        access_control = {"status": "error", "message": str(e)}
        gdpr = {"status": "error", "message": str(e)}

    return {
        "encryption": encryption_status,
        "access_control": access_control,
        "compliance": gdpr,
        "uptime": {
            "status": "secure",
            "message": f"{uptime_hours}h {uptime_minutes % 60}m {uptime_seconds % 60}s"
        },
        "last_checked": datetime.now(timezone.utc).isoformat()
    }


# ─────────────────────────────────────────────
# CLOUD RESOURCE ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/api/cloud/resource-groups")
def list_resource_groups():
    client = get_resource_client()

    groups = list(client.resource_groups.list())

    return {
        "debug_count": len(groups),
        "resource_groups": [
            {
                "name": g.name,
                "location": g.location,
                "status": g.properties.provisioning_state
            }
            for g in groups
        ]
    }


@app.get("/api/cloud/resources/{resource_group}")
def list_resources(resource_group: str):

    if resource_group in PROTECTED_GROUPS:
        return {
            "status": "error",
            "message": "This resource group is protected",
            "resources": []
        }

    try:
        client = get_resource_client()

        resources = list(
            client.resources.list_by_resource_group(resource_group)
        )

        return {
            "resource_group": resource_group,
            "count": len(resources),
            "resources": [
                {
                    "name": r.name,
                    "type": r.type,
                    "location": r.location
                }
                for r in resources
            ]
        }

    except Exception as e:
        return {"status": "error", "message": str(e), "resources": []}

@app.get("/debug/azure-check")
def azure_check():
    try:
        from importlib import import_module
        from azure.identity import AzureCliCredential

        # Handle SDK layout differences across azure-mgmt-resource/subscription packages.
        SubscriptionClient = None

        resource_mod = import_module("azure.mgmt.resource")
        SubscriptionClient = getattr(resource_mod, "SubscriptionClient", None)

        if SubscriptionClient is None:
            try:
                SubscriptionClient = getattr(
                    import_module("azure.mgmt.resource.subscriptions"),
                    "SubscriptionClient"
                )
            except ModuleNotFoundError:
                SubscriptionClient = getattr(
                    import_module("azure.mgmt.subscription"),
                    "SubscriptionClient"
                )

        credential = AzureCliCredential()
        client = SubscriptionClient(credential)

        subs = list(client.subscriptions.list())

        return {
            "status": "success",
            "subscriptions_found": len(subs),
            "first_sub": subs[0].subscription_id if subs else None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
# ─────────────────────────────────────────────
# 🔥 CLEANUP (DELETE RESOURCE GROUP)
# ─────────────────────────────────────────────

@app.delete("/api/cloud/cleanup/{resource_group}")
def cleanup_resources(resource_group: str):

    if resource_group in PROTECTED_GROUPS:
        return {
            "status": "error",
            "message": "This resource group is protected"
        }

    try:
        client = get_resource_client()

        poller = client.resource_groups.begin_delete(resource_group)
        return {
            "status": "success",
            "message": f"Deletion started for '{resource_group}'",
        }
    
    except Exception as e:
        print(traceback.format_exc())
        return {
            "status": "error",
            "message": str(e)
        }