# AWS Lambda — Versioning, updates & rollback

<!-- Sources:
  docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx
-->

For the conceptual model — Temporal Worker Deployment Versions vs. Lambda function versions, and Pinned vs. Auto-Upgrade behavior — see `../concepts.md` ("Worker Versioning with Serverless Workers").

## The full redeploy sequence

Shipping a change touches code, AWS, and Temporal in a fixed order. Skipping or reordering a step is the most common way to end up with a version that is never invoked:

1. Bump the Build ID in the Worker code (`build-1` → `build-2`). It must match the `--build-id` you will register in step 5.
2. Rebuild and repackage (`setup.md`, Step 2).
3. `aws lambda update-function-code`, then `aws lambda wait function-updated-v2`.
4. `aws lambda publish-version` → note the new qualified ARN (`...:function:my-temporal-worker:2`).
5. `temporal worker deployment create-version` with the new build ID **and** the new qualified ARN.
6. Confirm the validation invocation bound the Task Queue (`describe-version --report-task-queue-stats`).
7. `temporal worker deployment set-current-version --yes` to shift traffic.

Two things that bite here: the Build ID lives in **three** places that must agree (Worker code, `--build-id`, and the Lambda version description if you use one), and the invocation role must authorize the *new* qualified ARN — which it does automatically only if you granted the `:*` wildcard form (see `iam.md`). A role scoped to `function:my-temporal-worker:1` silently fails to invoke `:2`.

## Update existing function

```bash
aws lambda update-function-code \
  --function-name my-temporal-worker \
  --zip-file fileb://function.zip
```
<!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:348-352 -->

**Wait for the update to settle before publishing.** `update-function-code` returns while `LastUpdateStatus` is still `InProgress`, and `publish-version` in that window either fails (`ResourceConflictException`) or, worse, snapshots the *previous* code. Block on the transition:

```bash
aws lambda wait function-updated-v2 --function-name my-temporal-worker
```

(`function-updated` on AWS CLI v1; see `setup.md` for the polling fallback.)

After updating, increment the Build ID in your Worker code and publish a new Lambda function version. <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:354-355 -->

## Publish a Lambda function version

For production, create an immutable snapshot of your Lambda code after creating the function and after each `update-function-code`, and maintain a one-to-one mapping between each Lambda function version and each Temporal Worker Deployment Version Build ID. <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:359,371 -->

```bash
aws lambda publish-version \
  --function-name my-temporal-worker \
  --description "Build ID build-5"
```
<!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:362-365 -->

The command prints the `FunctionArn` for the new version, for example `arn:aws:lambda:us-east-1:123456789012:function:my-temporal-worker:5`. Use this qualified versioned ARN when you create the Worker Deployment Version. <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:367-369 -->

For development or non-critical workloads, you can skip `publish-version` and use an unqualified ARN to iterate faster. <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:372 -->

To roll back, revert the Temporal Current Version with `temporal worker deployment set-current-version`. The previous Worker Deployment Version still points at its original Lambda function version and is ready to receive traffic again. <!-- docs/production-deployment/worker-deployments/serverless-workers/aws-lambda.mdx:375-377 -->

```bash
temporal worker deployment set-current-version \
  --deployment-name my-app --build-id build-1 --yes
```

This is the whole rollback — one Temporal-side command, no AWS change. Because each Build ID is pinned to its own immutable Lambda version, the old code is still deployed and invocable; nothing needs to be rebuilt or re-uploaded. Keep the previous version registered (do not `delete-version` right after a release) so this path stays available. Two caveats: `--yes` is required non-interactively or the command silently does nothing, and rolling back the Current Version does not move Workflows already pinned to the new build — it only redirects *new* Workflow executions.
