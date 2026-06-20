---
title: "Azure Landing Zones: A Pragmatic Quickstart"
category: how-to
tags: [azure, landing-zones, governance, bicep]
summary: A no-nonsense walkthrough for standing up an enterprise-ready Azure Landing Zone foundation without boiling the ocean.
---

Azure Landing Zones get a reputation for being heavyweight. They don't have to be.
This walkthrough sets up a pragmatic foundation you can grow into, focusing on the
pieces that actually matter on day one: **management group structure**, **policy
guardrails**, and a **repeatable deployment**.

## 1. Design the management group hierarchy

Keep it shallow. A hierarchy that mirrors your org chart will rot the moment the org
changes. Start with intent-based groups instead:

- `Platform` — shared services (identity, connectivity, management)
- `Landing Zones` — workload subscriptions (split `Corp` and `Online`)
- `Sandbox` — experimentation with loose policy
- `Decommissioned` — quarantine before deletion

## 2. Apply policy guardrails early

Guardrails are cheapest to apply before workloads land. A minimal starter set:

- Allowed locations (keep data in-region)
- Require tags (`owner`, `costCenter`)
- Deny public IPs on the `Corp` group
- Enable Microsoft Defender for Cloud

## 3. Deploy it as code

Wire the structure into Bicep so it's reviewable and repeatable:

```bicep
targetScope = 'managementGroup'

@description('Child management groups to create under the current scope.')
param childGroups array = [
  { name: 'platform',     displayName: 'Platform' }
  { name: 'landingzones', displayName: 'Landing Zones' }
  { name: 'sandbox',      displayName: 'Sandbox' }
]

resource groups 'Microsoft.Management/managementGroups@2023-04-01' = [for g in childGroups: {
  name: g.name
  properties: {
    displayName: g.displayName
  }
}]
```

Deploy with the Azure CLI:

```bash
az deployment mg create \
  --management-group-id contoso-root \
  --location eastus \
  --template-file landing-zones.bicep
```

## 4. Validate before you celebrate

Run a `what-if` to see the blast radius before applying anything to a real tenant:

```bash
az deployment mg what-if \
  --management-group-id contoso-root \
  --location eastus \
  --template-file landing-zones.bicep
```

## Wrap-up

That's a foundation you can actually maintain. Next week I'll layer on **hub-and-spoke
networking** and a **policy-as-code pipeline** so guardrails ship through pull requests
instead of the portal.
