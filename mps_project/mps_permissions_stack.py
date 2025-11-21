from aws_cdk import (
    Stack,
    CfnOutput,
    aws_iam as iam,
)
from constructs import Construct


class PermissionsStack(Stack):
    """
    AWS Lake Formation Permissions Stack for MPS Project.
    
    Creates IAM roles with fine-grained column-level permissions for the mps_users table.
    
    Roles created:
    - mps-users-readonly: Can view basic user contact info (email, phone, name)
    - mps-analyst-readonly: Can view all columns except login section
    - mps-datacientist-readonly: Can view all columns (full access)
    
    Note: These are IAM roles that must be associated with Lake Formation permissions
    in the AWS console for column-level access control to take effect.
    
    Attributes:
        users_readonly_role: IAM role for basic users
        analyst_readonly_role: IAM role for analysts
        datacientist_readonly_role: IAM role for data scientists
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        rol_names = {
            "users" : "MPS-DataUsersReadOnlyRole",
            "analyst" : "MPS-DataAnalystReadOnlyRole",
            "datacientist" : "MPS-DataScientistReadOnlyRole",
        }

        # ============================================================================
        # ROLE 1: mps-users-readonly
        # Can view: email, phone, cell, name.title, name.first, name.last
        # ============================================================================
        self.users_readonly_role = iam.Role(
            self,
            id=rol_names["users"],
            role_name=rol_names["users"],
            assumed_by=iam.ServicePrincipal("lakeformation.amazonaws.com"),
            description="Role for basic users - can view contact info only (email, phone, name)",
        )

        # Add inline policy with Glue permissions for querying
        self.users_readonly_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "glue:GetDatabase",
                    "glue:GetTable",
                    "glue:GetPartitions",
                    "glue:GetDatabases",
                    "glue:GetTables",
                ],
                resources=[
                    f"arn:aws:glue:{self.region}:{self.account}:catalog",
                    f"arn:aws:glue:{self.region}:{self.account}:database/mps-data-db",
                    f"arn:aws:glue:{self.region}:{self.account}:table/mps-data-db/user_*",
                ]
            )
        )

        # ============================================================================
        # ROLE 2: mps-analyst-readonly
        # Can view: All columns EXCEPT login section
        # ============================================================================
        self.analyst_readonly_role = iam.Role(
            self,
            id=rol_names["analyst"],
            role_name=rol_names["analyst"],
            assumed_by=iam.ServicePrincipal("lakeformation.amazonaws.com"),
            description="Role for analysts - can view all columns except login section",
        )

        # Add inline policy with Glue permissions for querying
        self.analyst_readonly_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "glue:GetDatabase",
                    "glue:GetTable",
                    "glue:GetPartitions",
                    "glue:GetDatabases",
                    "glue:GetTables",
                ],
                resources=[
                    f"arn:aws:glue:{self.region}:{self.account}:catalog",
                    f"arn:aws:glue:{self.region}:{self.account}:database/mps-data-db",
                    f"arn:aws:glue:{self.region}:{self.account}:table/mps-data-db/user_*",
                ]
            )
        )

        # ============================================================================
        # ROLE 3: mps-datacientist-readonly
        # Can view: All columns (full access)
        # ============================================================================
        self.datacientist_readonly_role = iam.Role(
            self,
            id=rol_names["datacientist"],
            role_name=rol_names["datacientist"],
            assumed_by=iam.ServicePrincipal("lakeformation.amazonaws.com"),
            description="Role for data scientists - can view all columns",
        )

        # Add inline policy with Glue permissions for querying
        self.datacientist_readonly_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "glue:GetDatabase",
                    "glue:GetTable",
                    "glue:GetPartitions",
                    "glue:GetDatabases",
                    "glue:GetTables",
                ],
                resources=[
                    f"arn:aws:glue:{self.region}:{self.account}:catalog",
                    f"arn:aws:glue:{self.region}:{self.account}:database/mps-data-db",
                    f"arn:aws:glue:{self.region}:{self.account}:table/mps-data-db/user_*",
                ]
            )
        )

        # ============================================================================
        # OUTPUTS
        # ============================================================================
        CfnOutput(
            self,
            id="UsersReadOnlyRoleArn",
            value=self.users_readonly_role.role_arn,
            description="ARN of mps-users-readonly role",
            export_name="mps-users-readonly-role-arn",
        )

        CfnOutput(
            self,
            id="UsersReadOnlyRoleName",
            value=self.users_readonly_role.role_name,
            description="Name of mps-users-readonly role",
            export_name="mps-users-readonly-role-name",
        )

        CfnOutput(
            self,
            id="AnalystReadOnlyRoleArn",
            value=self.analyst_readonly_role.role_arn,
            description="ARN of mps-analyst-readonly role",
            export_name="mps-analyst-readonly-role-arn",
        )

        CfnOutput(
            self,
            id="AnalystReadOnlyRoleName",
            value=self.analyst_readonly_role.role_name,
            description="Name of mps-analyst-readonly role",
            export_name="mps-analyst-readonly-role-name",
        )

        CfnOutput(
            self,
            id="DataScientistReadOnlyRoleArn",
            value=self.datacientist_readonly_role.role_arn,
            description="ARN of mps-datacientist-readonly role",
            export_name="mps-datacientist-readonly-role-arn",
        )

        CfnOutput(
            self,
            id="DataScientistReadOnlyRoleName",
            value=self.datacientist_readonly_role.role_name,
            description="Name of mps-datacientist-readonly role",
            export_name="mps-datacientist-readonly-role-name",
        )
