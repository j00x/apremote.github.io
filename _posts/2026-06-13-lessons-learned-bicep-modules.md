---
title: "Lessons Learned: Scaling Bicep Modules Without the Pain"
category: lessons-learned
tags: [azure, bicep, iac, devops]
summary: Hard-won lessons from growing a Bicep module library across a dozen teams — versioning, registries, and the traps that bite at scale.
---

We started with a handful of Bicep files and ended up with a module library used by a
dozen teams. Here's what I'd tell my past self before that journey.

## Lesson 1: Publish modules to a registry early

Copy-pasting modules between repos feels fine until version drift makes every
deployment a snowflake. Push modules to an **Azure Container Registry** and consume
them by version:

```bicep
module network 'br:contoso.azurecr.io/bicep/modules/vnet:1.4.0' = {
  name: 'spoke-network'
  params: {
    addressSpace: '10.20.0.0/16'
  }
}
```

Pinning a version (`:1.4.0`) means a module change can't silently break a consumer.

## Lesson 2: Treat module interfaces like public APIs

Once teams depend on your module, **its parameters are a contract**. Renaming a
parameter is a breaking change. Decorate them so misuse fails at compile time, not at
3 a.m.:

```bicep
@allowed([ 'Standard_LRS', 'Standard_ZRS', 'Premium_LRS' ])
@description('Storage SKU. ZRS is the default for resilience.')
param skuName string = 'Standard_ZRS'
```

## Lesson 3: Outputs are not a dumping ground

Every output is something a consumer can couple to. Export only what callers genuinely
need (IDs, endpoints) — never secrets. Secrets belong in **Key Vault references**, not
deployment outputs where they leak into logs and state.

## Lesson 4: Test the module, not just the deployment

A quick `build` + `what-if` in CI catches the majority of regressions before review:

```bash
az bicep build --file modules/vnet/main.bicep
az deployment group what-if \
  --resource-group rg-ci \
  --template-file modules/vnet/main.bicep \
  --parameters @test.params.json
```

## The meta-lesson

The hard part of infrastructure-as-code at scale isn't the syntax — it's treating your
modules like the **products** other teams depend on. Versioning, contracts, and tests
are what turn a pile of templates into a platform.
