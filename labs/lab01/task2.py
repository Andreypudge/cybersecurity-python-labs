<<<<<<< HEAD
=======
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

if __name__ == "__main__":
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}\n")

>>>>>>> 300270f (1,2 tasks update)
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


<<<<<<< HEAD
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
=======
def check_res(user, info):
    for rsr, lvl in resources:
        if user not in users:
            print(f"user=[{user}] resource=[{rsr}] -> DENY (User not found)")
        elif user in blocked_users:
            print(f"user=[{user}] resource=[{rsr}] -> DENY (User is blocked)")
        elif not info["active"]:
            print(f"user=[{user}] resource=[{rsr}] -> DENY (Account inactive)")
        elif info["clearance"] >= lvl:
            print(f"user=[{user}] resource=[{rsr}] -> ALLOW")
        else:
            print(f"user=[{user}] resource=[{rsr}] -> DENY (Insufficient clearance)")
                
            
        



for usname, info in users.items():
    check_res(usname, info)

check_res("unknown_user", {})
>>>>>>> 300270f (1,2 tasks update)
