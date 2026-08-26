# AWS Lambda — Self-hosted Temporal Service

<!-- Sources:
  docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx
-->

Self-hosted Serverless Workers require Temporal Service v1.31.0 or later. <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:28 -->

Complete this server enablement before following `setup.md`. For the Lambda invocation role Temporal assumes (the CloudFormation stack and trust policy), see `iam.md`.

## Network reachability

The Temporal Service frontend must be reachable from the Lambda execution environment. If the Temporal Service runs on a private network, you may need VPC access for Lambda, VPC peering, or a similar mechanism. <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:44-47 -->

## Enable the Worker Controller Instance (WCI)

WCI is disabled by default and must be enabled through dynamic configuration. <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:52-53 -->

Add the following keys to your dynamic config file: <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:55 -->

```yaml
workercontroller.enabled:
  - value: true

workercontroller.compute_providers.enabled:
  - value:
      - aws-lambda

workercontroller.scaling_algorithms.enabled:
  - value:
      - no-sync
```
<!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:57-68 -->

To enable WCI for specific Namespaces instead of globally, add a `constraints` section with the Namespace name under `workercontroller.enabled`: <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:70-71 -->

```yaml
workercontroller.enabled:
  - value: true
    constraints:
      namespace: 'your-namespace'
```
<!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:73-78 -->

The Temporal Service watches the dynamic config file for changes and applies updates without a restart. <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:80 -->

## Configure AWS credentials

The Temporal Service needs AWS credentials to assume an IAM role that invokes Lambda functions. <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:84 -->

**On AWS infrastructure (EC2, ECS, EKS):** The server uses the attached instance role, task role, or pod role automatically. No additional credential configuration is needed. The attached role must have `sts:AssumeRole` permission for the Lambda invocation role. <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:87-89 -->

**Outside AWS:** Use IAM Roles Anywhere, or configure static AWS credentials in the server's environment (not recommended). These credentials must belong to an IAM user or role that has `sts:AssumeRole` permission for the Lambda invocation role. <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:91-101 -->

```
AWS_ACCESS_KEY_ID=<access-key>
AWS_SECRET_ACCESS_KEY=<secret-key>
AWS_REGION=<region>
```
<!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:94-98 -->
