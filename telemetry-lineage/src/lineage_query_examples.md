# Lineage Query Examples

## Upstream Query
- **Query:** What are the upstream sources for `Analytics_PurchaseOrder.PO_ID`?
- **Result:**
```
[
  ["Lakehouse_PurchaseOrder", "PurchaseOrderId"]
]
```

## Downstream Query
- **Query:** What are the downstream targets for `SAP_EKPO.EBELN`?
- **Result:**
```
[
  ["Lakehouse_PurchaseOrder", "PurchaseOrderId"]
]
```

## What-if Impact Analysis
- **Query:** If `SAP_EKPO.EBELN` changes, what fields are impacted downstream?
- **Result:**
```
{
  ["Lakehouse_PurchaseOrder", "PurchaseOrderId"],
  ["Analytics_PurchaseOrder", "PO_ID"]
}
```
