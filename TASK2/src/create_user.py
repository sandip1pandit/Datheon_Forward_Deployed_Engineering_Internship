import argparse
from getpass import getpass

from .models import ClearanceLevel
from .user_store import initialize_database, create_user


def main():
    parser = argparse.ArgumentParser(
        description="Provision an enterprise RAG user"
    )

    parser.add_argument("--username", required=True)
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--department", required=True)
    parser.add_argument(
        "--clearance",
        choices=[level.name for level in ClearanceLevel],
        required=True
    )
    parser.add_argument(
        "--roles",
        default="employee",
        help="Comma-separated roles, e.g. employee or tenant_admin"
    )

    args = parser.parse_args()

    password = getpass("Enter password: ")
    confirm_password = getpass("Confirm password: ")

    if password != confirm_password:
        raise SystemExit("Passwords do not match")

    initialize_database()

    create_user(
        username=args.username,
        password=password,
        tenant_id=args.tenant_id,
        department=args.department,
        clearance_level=ClearanceLevel[args.clearance],
        roles=[
            role.strip()
            for role in args.roles.split(",")
            if role.strip()
        ]
    )

    print(f"User '{args.username}' created successfully.")


if __name__ == "__main__":
    main()
