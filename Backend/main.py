from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_analysis import (
    get_avg_protein_bar,
    get_macros_heatmap,
    get_top_protein_scatter,
    get_recipe_distribution_pie,
    get_highest_protein_diet,
    get_most_common_cuisine
)
import time
import psutil
from datetime import datetime, timezone
from azure.identity import ManagedIdentityCredential
from azure.mgmt.storage import StorageManagementClient

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
