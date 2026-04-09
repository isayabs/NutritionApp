from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_analysis import (
    get_avg_protein_bar,
    get_macros_heatmap,
    get_top_protein_scatter,
    get_recipe_distribution_pie,
    get_highest_protein_diet,
    get_most_common_cuisine,
    get_recipes,
    get_recipe_list,
    get_recipe_clusters,
)
import time
import psutil
from datetime import datetime, timezone
from azure.identity import ManagedIdentityCredential
from azure.mgmt.storage import StorageManagementClient
from auth_routes import router as auth_router

#Helper functions-------------------------------------------------
def evaluate_encryption(is_blob_encrypted, is_file_encrypted, key_type, https_only, key_vault_uri):
    checks = {
        "blob_encrypted": is_blob_encrypted,
        "files_encrypted": is_file_encrypted,
        "customer_managed_keys": key_type == "CMK",
        "https_enforced": https_only,
        "key_vault_configured": key_vault_uri is not None
    }

    passed = sum(checks.values())
    total = len(checks)

    if passed == total:
        status = "secure"
    elif passed >= 3:
        status = "warning"
    else:
        status = "error"

    return {
        "status": status,
        "score": f"{passed}/{total}",
        "checks": checks,
        "message": generate_encryption_message(checks)
    }

def generate_encryption_message(checks):
    issues = []

    if not checks["blob_encrypted"]:
        issues.append("Blob encryption not enabled")
    if not checks["files_encrypted"]:
        issues.append("File encryption not enabled")
    if not checks["customer_managed_keys"]:
        issues.append("Using Microsoft-managed keys")
    if not checks["https_enforced"]:
        issues.append("HTTPS not enforced")
    if not checks["key_vault_configured"]:
        issues.append("No Key Vault configured")

    if not issues:
        return "Azure Blob SSE enabled · CMK · HTTPS enforced · Key Vault configured"

    return " · ".join(issues)

def generate_access_message(checks):
    issues = []

    if not checks["public_access_disabled"]:
        issues.append("Public blob access enabled")

    if not checks["network_restricted"]:
        issues.append("Storage allows all networks")

    if not checks["secure_tls"]:
        issues.append("Outdated TLS version")

    if not issues:
        return "Access control is properly configured"

    return " · ".join(issues)


def evaluate_access_control(public_access, default_action, min_tls):
    checks = {
        "public_access_disabled": not public_access,
        "network_restricted": default_action == "Deny",
        "secure_tls": min_tls in ["TLS1_2", "TLS1_3"]
    }

    passed = sum(checks.values())
    total = len(checks)

    if passed == total:
        status = "secure"
    elif passed > 0:
        status = "warning"
    else:
        status = "error"

    return {
        "status": status,
        "score": f"{passed}/{total}",
        "checks": checks,
        "message": generate_access_message(checks)
    }

def evaluate_gdpr(encryption_status, access_control):
    processes_personal_data = False
    checks = {
        "data_encrypted": encryption_status == "secure",
        "access_restricted": access_control["checks"]["network_restricted"],
        "public_access_disabled": access_control["checks"]["public_access_disabled"],
        "secure_transport": access_control["checks"]["secure_tls"],
        "no_personal_data_processed": not processes_personal_data
    }

    passed = sum(checks.values())
    total = len(checks)

    if passed == total:
        status = "secure"
    elif passed >= 3:
        status = "warning"
    else:
        status = "error"

    return {
        "status": status,
        "score": f"{passed}/{total}",
        "checks": checks,
        "message": generate_gdpr_message(checks, processes_personal_data)
    }


def generate_gdpr_message(checks, processes_personal_data):
    if not processes_personal_data:
        return "No personal data processed. Strong GDPR readiness based on infrastructure controls."

    missing = []

    if not checks["data_encrypted"]:
        missing.append("Encryption not properly configured")

    if not checks["access_restricted"]:
        missing.append("Network access not restricted")

    if not checks["public_access_disabled"]:
        missing.append("Public access is enabled")

    if not checks["secure_transport"]:
        missing.append("Secure transport (TLS) not enforced")

    if not missing:
        return "Strong GDPR readiness based on infrastructure controls"

    return " · ".join(missing)

app = FastAPI()

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://4.206.200.150:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()
SUBSCRIPTION_ID = "eba634ec-0ab9-49b5-8ebc-a9747f14a701"
RESOURCE_GROUP = "nutrition-app-rg"
STORAGE_ACCOUNT = "nutritionappstorage01"
# ─── Data Endpoints ───────────────────────────────────────────────────────────

@app.get("/api/data/nutritional-insights")
def nutritional_insights(diet: str = None, search: str = None, limit: int = 20):
    return {"data": get_recipes(diet=diet, search=search, limit=limit)}


@app.get("/api/data/recipes")
def recipes(diet: str = None, search: str = None, limit: int = 20):
    return {"data": get_recipe_list(diet=diet, search=search, limit=limit)}


@app.get("/api/data/clusters")
def clusters(diet: str = None, search: str = None, limit: int = 50):
    return {"data": get_recipe_clusters(diet=diet, search=search, limit=limit)}

# ─── Chart Endpoints ──────────────────────────────────────────────────────────

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

@app.get("/api/security/status")
def security_status():
    uptime_seconds = int(time.time() - START_TIME)
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60

    # Query real encryption status from Azure
    try:
        credential = ManagedIdentityCredential()
        storage_client = StorageManagementClient(credential, SUBSCRIPTION_ID)
        account = storage_client.storage_accounts.get_properties(RESOURCE_GROUP, STORAGE_ACCOUNT)
        
        encryption = account.encryption
        is_blob_encrypted = encryption.services.blob.enabled
        is_file_encrypted = encryption.services.file.enabled
        key_type = "CMK" if encryption.key_source == "Microsoft.Keyvault" else "Microsoft-managed"
        https_only = account.enable_https_traffic_only
        key_vault_uri = encryption.key_vault_properties.key_vault_uri if encryption.key_vault_properties else None

        access_control = evaluate_access_control(
            account.allow_blob_public_access,
            account.network_rule_set.default_action,
            account.minimum_tls_version
        )

        encryption_status = evaluate_encryption(
            is_blob_encrypted,
            is_file_encrypted,
            key_type,
            https_only,
            key_vault_uri
        )

        gdpr_compliance = evaluate_gdpr(
            encryption_status["status"],
            access_control
        )
    except Exception as e:
        encryption_status = {
            "status": "warning",
            "message": "Could not retrieve encryption status"
        }

        access_control = {
            "status": "warning",
            "message": "Could not retrieve access control configuration"
        }

        gdpr_compliance = {
            "status": "warning",
            "message": "Could not retrieve GDPR compliance information"
        }

    return {
        "encryption": encryption_status,
        "access_control": access_control,
        "compliance": gdpr_compliance,
        "uptime": {
            "status": "secure",
            "message": f"{uptime_hours}h {uptime_minutes % 60}m {uptime_seconds % 60}s"
        },
        "last_checked": datetime.now(timezone.utc).isoformat()
    }