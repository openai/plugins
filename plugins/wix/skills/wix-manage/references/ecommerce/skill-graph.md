---
name: "eCommerce Skill Graph"
description: Mermaid diagram showing how eCommerce skills connect — unified strategy entry point, goal/flow/guardrail chain, tracking inlined, troubleshoot as direct entries.
---

## Skill Graph Diagram

```mermaid
flowchart TB
    MR["Merchant Request"] --> R

    subgraph R["R — Unified Entry Point"]
        recommend-ecommerce-strategy
    end

    R --> |"loads API ref"| Config
    R --> |"Step 4b: loads matching goal"| Goals
    R --> |"Step 2+8: tracking inlined"| TrackingAPI

    subgraph Goals["Goals — Business Objectives"]
        subgraph GD["Discount + Shipping"]
            goal-increase-aov
            goal-clear-inventory
            goal-seasonal-revenue
            goal-drive-cross-sells
        end
        subgraph GA["Abandoned Cart"]
            goal-reduce-cart-abandonment
        end
    end

    Goals --> |"loads matching flows"| Flows
    goal-increase-aov --> |"also loads shipping flows"| FS

    subgraph Flows["Flows — Business Logic"]
        subgraph FD["Discount"]
            flow-upsell-boost
            flow-bundle-and-save
            flow-stock-mover
            flow-seasonal-promotion
        end
        subgraph FS["Shipping"]
            flow-fix-coverage-gaps
            flow-add-free-shipping
            flow-optimize-shipping-rates
        end
    end

    Flows --> |"loads validation"| Guardrails
    Flows --> |"loads setup"| Config

    subgraph Guardrails["Cross-cutting: Guardrails"]
        guardrail-discount-conflicts
        guardrail-margin-protection
        guardrail-shipping-health
        guardrail-rate-pricing-sanity
    end

    subgraph Config["Config — Setup & API References"]
        setup-discount-rules
        setup-coupons
        setup-shipping-regions
        setup-shipping-rates
        api-shipping
    end

    subgraph TrackingAPI["Tracking API"]
        api-recommendation-tracking
    end

    subgraph Standalone["Direct Entry Points (from README)"]
        recipe-apply-shipping-recommendations
        setup-store-pickup-location
        troubleshoot-discount-not-applying
        troubleshoot-checkout-delivery-dropoff
    end

    Config -.-> |"calls via CallWixSiteAPI"| API

    subgraph API["Wix REST API Docs (dev.wix.com)"]
        D1["Discount Rules API"]
        D2["Coupons API"]
        D3["Products V3 API"]
        D4["Categories API"]
        D5["Catalog Analytics"]
        S3["Pickup Locations API"]
        S4["Local Delivery API"]
        SD["Profile Service API (wix-profile-client)"]
    end

    classDef goal fill:#8b5cf6,stroke:#6d28d9,color:#fff
    classDef guardrail fill:#ef4444,stroke:#dc2626,color:#fff
    classDef flow fill:#3b82f6,stroke:#2563eb,color:#fff
    classDef config fill:#f59e0b,stroke:#d97706,color:#fff
    classDef reco fill:#ec4899,stroke:#db2777,color:#fff
    classDef standalone fill:#6b7280,stroke:#4b5563,color:#fff
    classDef apidoc fill:#e5e7eb,stroke:#9ca3af,color:#374151

    class goal-increase-aov,goal-clear-inventory,goal-seasonal-revenue,goal-drive-cross-sells,goal-reduce-cart-abandonment goal
    class guardrail-discount-conflicts,guardrail-margin-protection,guardrail-shipping-health,guardrail-rate-pricing-sanity guardrail
    class flow-upsell-boost,flow-bundle-and-save,flow-stock-mover,flow-seasonal-promotion,flow-fix-coverage-gaps,flow-add-free-shipping,flow-optimize-shipping-rates flow
    class setup-discount-rules,setup-coupons,setup-shipping-regions,setup-shipping-rates,api-recommendation-tracking,api-shipping config
    class recommend-ecommerce-strategy reco
    class recipe-apply-shipping-recommendations,setup-store-pickup-location,troubleshoot-discount-not-applying,troubleshoot-checkout-delivery-dropoff standalone
    class D1,D2,D3,D4,D5,S1,S2,S3,S4,SD apidoc
```

## File Reachability

| File | Reached via |
|---|---|
| `recommend-ecommerce-strategy.md` | README routing (entry point) |
| `api-recommendation-tracking.md` | Entry point tracking steps |
| `goal-increase-aov.md` | Step 4b (UPSELL_BOOST) |
| `goal-clear-inventory.md` | Step 4b (STOCK_MOVER) |
| `goal-seasonal-revenue.md` | Step 4b (SEASONAL) |
| `goal-drive-cross-sells.md` | Step 4b (BUNDLE_AND_SAVE) |
| `goal-reduce-cart-abandonment.md` | Step 4b (ABANDONED_CART domain) |
| `flow-upsell-boost.md` | goal-increase-aov chain |
| `flow-bundle-and-save.md` | goal-increase-aov / goal-drive-cross-sells chain |
| `flow-stock-mover.md` | goal-clear-inventory chain |
| `flow-seasonal-promotion.md` | goal-seasonal-revenue chain |
| `flow-fix-coverage-gaps.md` | goal-reduce-cart-abandonment chain (critical operational fix) |
| `flow-add-free-shipping.md` | goal-increase-aov chain (shipping flows serving AOV) |
| `flow-optimize-shipping-rates.md` | goal-increase-aov chain (shipping flows serving AOV) |
| `guardrail-discount-conflicts.md` | flow-upsell-boost / bundle / stock / seasonal chains |
| `guardrail-margin-protection.md` | flow-upsell-boost / stock-mover chains |
| `guardrail-shipping-health.md` | flow-fix-coverage-gaps chain |
| `guardrail-rate-pricing-sanity.md` | flow-add-free-shipping / optimize chains |
| `setup-discount-rules.md` | All discount flow chains |
| `setup-coupons.md` | Step 4c (COUPON mechanism) |
| `setup-shipping-regions.md` | flow-fix-coverage-gaps chain |
| `setup-shipping-rates.md` | flow-add-free-shipping / optimize chains |
| `api-shipping.md` | Shipping flows (fix-coverage-gaps, add-free-shipping, optimize, recipe, setup-store-pickup) |
| `recipe-apply-shipping-recommendations.md` | README direct entry |
| `setup-store-pickup-location.md` | README direct entry |
| `troubleshoot-discount-not-applying.md` | README direct entry |
| `troubleshoot-checkout-delivery-dropoff.md` | README direct entry |
| `skill-graph.md` | Documentation reference |
