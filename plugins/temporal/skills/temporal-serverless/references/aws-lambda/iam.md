# AWS Lambda — IAM & permissions

<!-- Sources:
  docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx
  docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx
-->

This file covers three distinct identities: the **operator** (whose credentials run the deploy commands), the **execution role** (grants the function permission to run), and the **Temporal invocation role** (grants Temporal permission to invoke the function). The deploy steps themselves are in `setup.md`; self-hosted server enablement is in `self-hosted.md`.

## Operator AWS permissions

The identity whose credentials run the `aws`/CloudFormation commands (local profile, EC2/ECS instance role, CI role, or CloudShell console identity) needs the actions below. These are separate from the execution and invocation roles created in Step 3.

| Deployment step | Operator actions required |
|---|---|
| Deploy / update the Lambda (`setup.md`, Step 2) | `lambda:CreateFunction`, `lambda:UpdateFunctionCode`, `lambda:GetFunction`, `lambda:PublishVersion`, `lambda:InvokeFunction`, and **`iam:PassRole`** on the execution role. |
| Create the execution role directly (if not using CloudFormation) | `iam:CreateRole`, `iam:AttachRolePolicy`. |
| Create the invocation role via CloudFormation (Step 3) | `cloudformation:CreateStack`, `cloudformation:DescribeStacks`, plus IAM write (`iam:CreateRole`, `iam:PutRolePolicy`/`iam:AttachRolePolicy`, `iam:GetRole`, `iam:DeleteRole` for rollback) — hence `--capabilities CAPABILITY_NAMED_IAM`. |
| Read Worker logs (`setup.md` verify + `diagnostics.md`) | `logs:FilterLogEvents`, `logs:GetLogEvents`, `logs:DescribeLogGroups`, `logs:DescribeLogStreams`. |

`iam:PassRole` is required separately from `lambda:CreateFunction`: `create-function` attaches the execution role to the function, and without `iam:PassRole` on that role the deploy fails with `AccessDenied ... not authorized to perform: iam:PassRole` even when `CreateFunction` is allowed. Scope it to the execution role ARN.

If the operator cannot have IAM write permissions, have an administrator run the Step 3 CloudFormation stack once and hand back the `RoleARN` output (and pre-create the execution role if needed). The operator then needs only the Lambda actions, `iam:PassRole` on the pre-created execution role, and CloudWatch Logs read.

### Preflight check

Run before any command that creates or modifies AWS resources. None should print `DENIED`:

```bash
aws sts get-caller-identity
aws lambda list-functions --max-items 1 >/dev/null 2>&1 && echo "lambda: ok" || echo "lambda: DENIED"
aws cloudformation describe-stacks >/dev/null 2>&1 && echo "cloudformation: ok" || echo "cloudformation: DENIED"
aws iam list-roles --max-items 1 >/dev/null 2>&1 && echo "iam read: ok" || echo "iam: limited (role creation may be blocked)"
aws logs describe-log-groups --limit 1 >/dev/null 2>&1 && echo "logs: ok" || echo "logs: DENIED"
```

The calls above cannot exercise `iam:PassRole`. To check it (and any other specific action) authoritatively, use the policy simulator against the caller's ARN:

```bash
CALLER_ARN=$(aws sts get-caller-identity --query Arn --output text)
aws iam simulate-principal-policy \
  --policy-source-arn "$CALLER_ARN" \
  --action-names lambda:CreateFunction iam:PassRole cloudformation:CreateStack iam:CreateRole \
  --query 'EvaluationResults[].{action:EvalActionName,decision:EvalDecision}' --output table
```

For an assumed-role session, rewrite the ARN (`arn:aws:sts::…:assumed-role/Name/session`) to the underlying role ARN (`arn:aws:iam::…:role/Name`) for `simulate-principal-policy`.

### When the preflight cannot authenticate

`aws sts get-caller-identity` failing does not mean the user has no access — most often no profile is selected, or an SSO token has expired. Classify before concluding anything:

| Error | Meaning | Action |
|---|---|---|
| `Unable to locate credentials` | Nothing configured or selected | Check for existing profiles before concluding there are none |
| `ExpiredToken`, `The SSO session associated with this profile has expired` | Profile is fine, token is stale | Refresh it, below |
| `InvalidClientTokenId`, `SignatureDoesNotMatch`, `UnrecognizedClientException` | Credentials exist but are invalid — stale static keys, a deleted user, or the wrong account | Do not retry; re-authenticate, or ask which profile is intended. Report the account you *did* resolve, if any |
| `AccessDenied` on an action while `get-caller-identity` succeeds | Authenticated, insufficient permissions | Genuine permissions problem — see the operator table above |

Look at what is already configured before asking the user for anything:

```bash
echo "AWS_PROFILE=${AWS_PROFILE:-<unset>}"
aws configure list-profiles
```

Then pick the login command by what that turned up. These are two different commands, not aliases — do not substitute one for the other:

**A profile already exists (token is just stale)** — refresh the IAM Identity Center token:

```bash
aws sso login --profile <profile> --no-browser
```

`--no-browser` prints the verification URL and user code instead of opening a browser. Auto-open is unreliable over SSH, containers, and remote sessions, and the user needs the URL in the conversation either way.

**Nothing is configured at all** — `aws login` needs no prior setup, acquiring temporary credentials from a Management Console session plus a refresh token that the CLI renews automatically:

```bash
aws login
```

Two limits on it. AWS scopes this command to *local development*, so do not use it as the identity for a CI or production deployment — those need a configured profile or an assumed role. And it is recent enough that older CLIs do not have it: confirm with `aws login help` before offering it, and fall back to asking the user to run `aws configure sso` themselves if it is absent. Avoid its `--remote` flag in an agent shell — unlike `aws sso login --no-browser`, it prompts for an authorization code on stdin; on a remote host, prefer configuring an SSO profile and using `aws sso login --no-browser` instead.

Either command blocks until the browser flow finishes, so run it in a background shell, surface the URL (and code, if any) to the user, and poll until credentials land:

```bash
aws sts get-caller-identity
```

Re-run the preflight above and continue the deployment.

If the organization wraps credentials in its own tool (`aws-vault`, `granted`/`assume`, `saml2aws`), use that instead — ask which, rather than guessing.

**Never run `aws configure`/`aws configure sso` interactively, and never ask the user to paste access keys or session tokens into the conversation** — the wizards block an agent shell on stdin, and pasted keys land in the transcript and shell history. If neither login command applies, ask the user to configure a profile or export credentials in their own shell, then tell you when to re-run the preflight.

## Execution role

The Lambda execution role grants the function permission to run. It is trusted by `lambda.amazonaws.com` and must have at least the `AWSLambdaBasicExecutionRole` managed policy attached (which includes the CloudWatch Logs permissions the Worker needs). This is separate from the Temporal invocation role below. Pass its ARN as `--role` when you create the function (`setup.md`, Step 2). <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:317 -->

## Step 3: Configure IAM for Temporal invocation

### Temporal Cloud

This section applies to Temporal Cloud. For self-hosted, see the self-hosted section below. <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:379-383 -->

Temporal needs permission to invoke your Lambda function and check its status. The Temporal server assumes an IAM role in your AWS account with a handful of Lambda permissions scoped to your Worker functions. The trust policy on the role includes an External ID condition to prevent confused deputy attacks. <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:385-388 -->

#### CloudFormation template parameters

<!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:394-398 -->

| Parameter | Description |
|---|---|
| `AssumeRoleExternalId` | A string you choose to prevent confused deputy attacks. Can be any value. Use the same value when creating the Worker Deployment Version. |
| `LambdaFunctionARNs` | Comma-separated list of Lambda function ARNs that Temporal may invoke. To allow invocation of any published version of a function, use a wildcard suffix (for example, `arn:aws:lambda:...:function:my-temporal-worker:*`). One role can authorize multiple Worker Lambdas. |
| `RoleName` | Base name for the created IAM role. Defaults to `Temporal-Cloud-Serverless-Worker`. Provide a new role name if creating more than one stack. |

#### Before creating the stack: check whether the role already exists

**The default `RoleName` collides, and the failure mode is a full stack rollback.** The template creates a *named* IAM role, and IAM role names are unique per account. Any earlier serverless deployment in the same account already holds `Temporal-Cloud-Serverless-Worker`, so a second `create-stack` with default parameters fails with `already exists` and rolls the whole stack back. Check first:

```bash
ROLE=Temporal-Cloud-Serverless-Worker   # or whatever name you intend to use

# Does the role already exist?
aws iam get-role --role-name "$ROLE" --query 'Role.Arn' --output text 2>/dev/null \
  || echo "not present — safe to create"

# If it does: which stack owns it? CloudFormation tags the resources it creates.
# Empty output means the role is orphaned or hand-created, not stack-managed.
aws iam list-role-tags --role-name "$ROLE" \
  --query 'Tags[?Key==`aws:cloudformation:stack-name`].Value' --output text

# Cross-check against the stack list if the tag lookup comes back empty
aws cloudformation describe-stacks --region <AWS_REGION> \
  --query 'Stacks[?StackStatus!=`DELETE_COMPLETE`].{Name:StackName,Status:StackStatus}' \
  --output table
```

Then pick a path — **prefer reuse over a parallel role.** The invocation role is account-wide shared infrastructure, not per-function, and one role can authorize many Worker Lambdas:

| Situation | Action |
|---|---|
| No role, no stack | Create the stack as documented below. |
| A stack owns the role, and this deployment is a legitimate addition | **Update that stack**, adding your function's ARNs to `LambdaFunctionARNs` (`aws cloudformation update-stack` with the full comma-separated list — CloudFormation replaces the list, it does not merge). Reuse its `RoleARN` output. Do not create a second role. |
| A stack owns the role but is someone else's infrastructure you must not touch | Create a *separate* stack with an explicit distinct `RoleName` (for example `Temporal-Cloud-Serverless-Worker-<purpose>`) and say why in your summary. Two roles is the fallback, not the default. |
| The role exists but no stack owns it (orphaned or hand-created) | Do not delete it blind. Either reuse it after confirming its trust policy and permissions, or create a new stack with a distinct `RoleName`. Ask the user before removing an unowned IAM role. |

**Recovering from a rolled-back stack.** A stack in `ROLLBACK_COMPLETE` cannot be updated or re-created under the same name — delete it first, then create again with corrected parameters. Read the actual cause before changing anything:

```bash
aws cloudformation describe-stack-events --stack-name <STACK_NAME> --region <AWS_REGION> \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`].[LogicalResourceId,ResourceStatusReason]' --output table
aws cloudformation delete-stack --stack-name <STACK_NAME> --region <AWS_REGION>
aws cloudformation wait stack-delete-complete --stack-name <STACK_NAME> --region <AWS_REGION>
```

Deleting a `ROLLBACK_COMPLETE` stack is safe — it created nothing that survived. Deleting a stack in any *successful* state is not; that is live infrastructure.

#### Which ARNs to authorize

**`function:name:*` does not match the unqualified `function:name`.** In IAM, the wildcard-version ARN covers published versions and aliases only; the unqualified function ARN is a distinct resource. Temporal needs `lambda:GetFunction` and `lambda:InvokeFunction` to resolve for whatever ARN form you register on the Worker Deployment Version, so authorize **both** forms and you are covered either way:

```bash
FN=arn:aws:lambda:<AWS_REGION>:<ACCOUNT_ID>:function:my-temporal-worker
# The CLI shorthand needs the literal double quotes to survive, so that the
# embedded comma is read as a list separator and not as the next ParameterKey:
ARNS="\"$FN,$FN:*\""
# ... --parameters ParameterKey=LambdaFunctionARNs,ParameterValue="$ARNS"
```

The `:*` form is also what makes future `publish-version` builds work without an IAM change — authorizing a single fixed version (`function:my-temporal-worker:1`) means the next published version cannot be invoked, which surfaces later as a validation/invocation failure that looks unrelated to IAM. See `versioning.md`.

#### Trust policy principals

The Cloud template trusts five Temporal Cloud AWS account IDs with the role `wci-lambda-invoke`: <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:457-464 -->

- `arn:aws:iam::902542641901:role/wci-lambda-invoke` <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:459 -->
- `arn:aws:iam::160190466495:role/wci-lambda-invoke` <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:460 -->
- `arn:aws:iam::819232936619:role/wci-lambda-invoke` <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:461 -->
- `arn:aws:iam::829909441867:role/wci-lambda-invoke` <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:462 -->
- `arn:aws:iam::354116250941:role/wci-lambda-invoke` <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:463 -->

The IAM policy grants `lambda:InvokeFunction` and `lambda:GetFunction` on the specified Lambda function ARNs. <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:481-484 -->

#### Deploy the CloudFormation stack

This skill ships the complete, ready-to-deploy template at `assets/temporal-cloud-serverless-worker-role.yaml` (transcribed verbatim from the docs). Copy it into your working directory, or point `--template-body` at the skill's copy — no need to author it by hand. <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:404-501 -->

```bash
aws cloudformation create-stack \
  --stack-name <STACK_NAME> \
  --template-body file://temporal-cloud-serverless-worker-role.yaml \
  --parameters \
    ParameterKey=AssumeRoleExternalId,ParameterValue=<EXTERNAL_ID> \
    ParameterKey=LambdaFunctionARNs,ParameterValue='"<LAMBDA_FUNCTION_ARN>,<LAMBDA_FUNCTION_ARN>:*"' \
    ParameterKey=RoleName,ParameterValue=<ROLE_NAME> \
  --capabilities CAPABILITY_NAMED_IAM \
  --region <AWS_REGION>
```
<!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:509-517; RoleName and dual-ARN values per the guidance above -->

Notes on the parameters above:

- **Set `RoleName` explicitly** rather than relying on the default, so the name reflects this deployment and does not collide with an existing one (see the collision check above).
- **`LambdaFunctionARNs` is a `CommaDelimitedList`.** The `'"a,b"'` quoting is required: the AWS CLI's `ParameterKey=,ParameterValue=` shorthand otherwise reads the embedded comma as the start of a new key. Keep the literal double quotes inside the single quotes.
- **Generate the External ID rather than choosing a memorable string** — it is a confused-deputy guard. The template accepts 5–45 characters matching `[a-zA-Z0-9_+=,.@-]*`. Record it: you need the identical value when registering the Worker Deployment Version, and it is not recoverable from the version afterward.
  ```bash
  EXTERNAL_ID=$(openssl rand -hex 16)
  ```

Retrieve the IAM role ARN from the stack outputs: <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:519 -->

```bash
aws cloudformation describe-stacks --stack-name <STACK_NAME> --query 'Stacks[0].Outputs[?OutputKey==`RoleARN`].OutputValue' --output text --region <AWS_REGION>
```
<!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:521-522 -->

### Self-hosted invocation role

For self-hosted server enablement (dynamic config, WCI, and the server's own AWS credentials), see `self-hosted.md`. The invocation role itself is below.

Self-hosted Serverless Workers require Temporal Service v1.31.0 or later. <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:28 -->

#### Create the Lambda invocation role (self-hosted)

Temporal invokes Lambda functions by assuming an IAM role in your AWS account. This role needs `lambda:GetFunction` and `lambda:InvokeFunction` permission on your Worker Lambda functions, and a trust policy that allows the Temporal server's identity to assume it. <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:105-107 -->

This skill ships the complete self-hosted template at `assets/temporal-self-hosted-serverless-worker-role.yaml` (verbatim from the docs). Copy it locally or point `--template-body` at the skill's copy. <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:136-209 -->

```bash
aws cloudformation create-stack \
  --stack-name temporal-serverless-worker \
  --template-body file://temporal-self-hosted-serverless-worker-role.yaml \
  --parameters \
    ParameterKey=TemporalIamRoleArn,ParameterValue=<TEMPORAL_SERVER_ROLE_ARN> \
    ParameterKey=AssumeRoleExternalId,ParameterValue=<EXTERNAL_ID> \
    ParameterKey=LambdaFunctionARNs,ParameterValue='"<LAMBDA_FUNCTION_ARN>"' \
  --capabilities CAPABILITY_NAMED_IAM \
  --region <AWS_REGION>
```
<!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:113-123 -->

| Parameter | Description |
|---|---|
| `TemporalIamRoleArn` | ARN of the IAM role or user that the Temporal Service runs as (the identity used to call `sts:AssumeRole`). Run `aws sts get-caller-identity` in the server's environment to find it. |
| `AssumeRoleExternalId` | A unique string to prevent confused deputy attacks. Use the same value when creating the Worker Deployment Version. |
| `LambdaFunctionARNs` | Comma-separated list of Lambda function ARNs that Temporal may invoke. To allow any published version, use a wildcard suffix (for example, `arn:aws:lambda:...:function:my-temporal-worker:*`). |
| `RoleName` | Base name for the created IAM role. Defaults to `Temporal-Serverless-Worker`. Provide a new role name if creating more than one stack. |
<!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:125-130 -->

Retrieve the role ARN: <!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:214 -->

```bash
aws cloudformation describe-stacks \
  --stack-name temporal-serverless-worker \
  --query 'Stacks[0].Outputs[?OutputKey==`RoleARN`].OutputValue' \
  --output text \
  --region <AWS_REGION>
```
<!-- docs/production-deployment/worker-deployments/serverless-workers/self-hosted-setup.mdx:216-222 -->

**Key distinction:** The Lambda execution role (trusted by `lambda.amazonaws.com`) is separate from the Temporal invocation role (trusted by Temporal's `wci-lambda-invoke` principals for Cloud, or the Temporal Service's own IAM identity for self-hosted). The execution role grants the function permission to run. The invocation role grants Temporal permission to invoke the function. <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:317,548,586 -->
