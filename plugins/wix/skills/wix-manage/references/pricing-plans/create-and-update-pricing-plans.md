---
name: "Create and Update Pricing Plans"
description: Creates subscription and one-time payment plans using Plans API. Covers pricing models (recurring, one-time, free), trial periods, perks configuration, and plan visibility.
---
# Technical Step-by-Step Instructions: Creating or Updating a Wix Pricing Plans (Real-World, API-First)

## Description
Below are the recommended steps to successfully create or update a Wix Pricing Plans (or several at once) on Wix and attach a booking session to a pricing plan, with real-world troubleshooting and fixes for common API issues.

---

## Overview
Wix Pricing Plans includes Plans that allows Wix users to build a customized membership plan experiences and sell them to their customers. Pricing plans can also have bundled booking session as benefits.

- With Plans, a site owner can create different types of plans, such as, free, one-time or recurring subscriptions and memberships.
- With Benefits, a site owner can connect other wix apps like booking service to a pricing plan subscription or membership. Read the full list of pricing plan integration [here](https://dev.wix.com/docs/api-reference/business-solutions/pricing-plans/introduction#integrations).

### IMPORTANT NOTES
- Always Prioritize Reading Full API Method Documentation: this overview article provides a general workflow. However, it repeatedly stresses the importance of reading the full documentation for each specific REST method you intend to use. This is critical for understanding detailed requirements.
- Pay close attention to all required fields, data types, enum values, and specific ID types (e.g., resourceId vs. id) as defined in the detailed schema of each API endpoint. The overview article serves as a guide but doesn't replace the need to consult these specifics.

---

## Steps
### 0. Read pricing plans API docs
Before proceeding to further steps I must read the following [documentation](https://dev.wix.com/docs/api-reference/business-solutions/pricing-plans/introduction) on how to form request to pricing plans API.

### 1. Create a pricing plan
Creating a pricing plan can be done by using [create plan](https://dev.wix.com/docs/api-reference/business-solutions/pricing-plans/plans-v3/create-plan) endpoint.

### 2. Attach integrating app entity to pricing plans

To attach integrating app entity, like bookings or blog to pricing plans read the [Benefit Programs](https://dev.wix.com/docs/api-reference/business-solutions/benefit-programs/introduction) documentation and proceed to further steps.

#### 2.1. Find program definition

Use [Get Program Definition By External Id And Namespace](https://dev.wix.com/docs/api-reference/business-solutions/benefit-programs/program-definitions/get-program-definition-by-external-id-and-namespace) endpoint to find the corresponding program definition of the plan. The call must have these query params:
- `externalId` must be equal to pricing plan id.
- `namespace` must be `@wix/pricing-plans`

Example the request in curl:
```bash
curl --request GET \
  "https://www.wixapis.com/benefit-programs/v1/program-definitions/by-namespace-and-external-id?externalId=00000000-0000-0000-0000-000000000001&namespace=@wix/pricing-plans" \
  -H 'Authorization: <AUTH>' \
  -H "Content-Type: application/json"
```

#### 2.2. Create a pool definition

Only one pool definition per integrating app must be created. The pool definition should be created using [create pool definition](https://dev.wix.com/docs/api-reference/business-solutions/benefit-programs/pool-definitions/create-pool-definition) endpoint.

The request for this endpoint must adhere to these rules:
- `namespace` must be `@wix/pricing-plans`
-  only one benefit can be defined in the pool definition
- benefit benefitKey must be a random generated UUID
- benefit provider app id must be the integrating app def id. For the full list of wix app def ids read [this](https://dev.wix.com/docs/api-reference/articles/get-started/apps-created-by-wix) article.
- benefit price must be only 1 or 0. 0 - if you want the benefit to have unlimited credits and 1 - for the benefit to be limited.
- `creditConfiguration` must be empty if the benefit is unlimited

#### 2.3. Create benefit items

This step is needed to attach the integrating app entity to benefit program. This is done by using [bulk create items](https://dev.wix.com/docs/api-reference/business-solutions/benefit-programs/items/bulk-create-items) endpoint.

Each item in the request for this endpoint must adhere to these rules:
- `namespace` must be `@wix/pricing-plans`
-  `category` must be empty string
- provider app id must be the integrating app def id. For the full list of wix app def ids read [this](https://dev.wix.com/docs/api-reference/articles/get-started/apps-created-by-wix) article.
- `itemSetId` must set to the created pool definition benefit item set id.
- `externalId` must be set to the integrating app entity id, example: booking service id or blog post id.

## Pricing plans REST API Documentation Reference
- [Create plan](https://dev.wix.com/docs/api-reference/business-solutions/pricing-plans/plans-v3/create-plan)
- [Get plan](https://dev.wix.com/docs/api-reference/business-solutions/pricing-plans/plans-v3/get-plan)
- [Update plan](https://dev.wix.com/docs/api-reference/business-solutions/pricing-plans/plans-v3/update-plan)
- [Query Plans](https://dev.wix.com/docs/api-reference/business-solutions/pricing-plans/plans-v3/query-plans)
- [Pricing Plans Introduction](https://dev.wix.com/docs/api-reference/business-solutions/pricing-plans/introduction)
