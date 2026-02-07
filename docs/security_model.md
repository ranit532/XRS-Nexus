# Security Model

## Role-Based Access Control (RBAC)
- **Identity Provider:** Microsoft Entra ID (Azure AD)
- **Roles:**
  - `PlatformAdmin`: Full access to all resources and audit logs
  - `DataEngineer`: Can manage pipelines, view/edit metadata, view audit logs
  - `DataScientist`: Can view metadata, lineage, and run analytics
  - `Viewer`: Read-only access to metadata, lineage, and execution status
- **Resource Scopes:**
  - Metadata objects
  - Pipelines
  - Lineage graphs
  - Audit logs
- **Enforcement:**
  - All API endpoints require Entra ID authentication
  - Role claims checked on each request
  - Fine-grained access enforced at API and data layer
