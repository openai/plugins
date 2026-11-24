# AWS IAM Role Setup

Use this reference only after the S3 trust-policy Tool returns a complete Trust
Policy.

## Configure the Role

1. Open the [AWS IAM Roles console](https://console.aws.amazon.com/iam/home#/roles).
2. Create the Role and apply the exact generated Trust Policy.
3. Attach S3 permissions for the resolved bucket and prefix. If the user
   requested permission guidance, use the least-privilege policy already loaded
   by the owning Skill.
4. Copy the exact Role ARN after both trust and S3 permissions are applied.

## AWS Documentation

- [Create an IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html)
