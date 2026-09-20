users = {
    "cloud_architect": {
        "role": "cloud_security",
        "clearance": 4,
        "department": "Cloud",
        "active": True,
    },
    "devops_engineer": {
        "role": "devops",
        "clearance": 3,
        "department": "DevOps",
        "active": True,
    },
    "qa_tester": {
        "role": "quality_assurance",
        "clearance": 2,
        "department": "QA",
        "active": True,
    },
    "partner_access": {
        "role": "partner",
        "clearance": 2,
        "department": "Partnership",
        "active": True,
    },
    "migrated_user": {
        "role": "migrated",
        "clearance": 1,
        "department": "Migration",
        "active": False,
    },
}

resources = [
    ("cloud_configs", 4),
    ("deployment_pipelines", 3),
    ("test_environments", 2),
    ("partner_apis", 2),
    ("infrastructure_code", 4),
    ("shared_resources", 1),
    ("container_registry", 3),
    ("secrets_vault", 4),
    ("build_artifacts", 2),
    ("public_endpoints", 1),
]

security_levels = (
    "Development",
    "Staging",
    "Production",
    "Critical Infrastructure",
)

blocked_users = {"migrated_user", "container_breach", "pipeline_compromise"}

for key, value in resources:
    print(f"{key}: {security_levels[value - 1]}")


def check_res():
    for key, value in users.items():
        for rsr, lvl in resources:
            if key in blocked_users:
                print(f"user=[{key}] resource=[{rsr}] -> DENY (User is blocked)")
            else:
                if value["active"]:
                    if value["clearance"] >= lvl:
                        print(f"user=[{key}] resource=[{rsr}] -> ALLOW")
                    else:
                        print(
                            f"user=[{key}] resource=[{rsr}] -> DENY (Insufficient clearance)"
                        )
                else:
                    print(f"user=[{key}] resource=[{rsr}] -> DENY (Account inactive)")


check_res()