# Implementation Plan: DB Export to YAML (Redacted)

## Objective
Expand the project to support exporting the entire database to a YAML file format. The exported YAML will include all database tables (Full Database Dump) but will unconditionally redact sensitive information (such as password hashes and encrypted tenant secrets) to allow safe sharing, auditing, and version control.

## Background & Motivation
Users need a way to extract the internal state and configuration of the zs-config database in a human-readable text format (YAML). By redacting secrets, the exported YAML file can be safely attached to support tickets, committed to version control, or audited without risking credential exposure.

## Scope & Impact
- **Backend:** A new FastAPI endpoint (`GET /api/v1/admin/export-db-yaml`) will be added to read all SQLAlchemy models, redact specific sensitive fields, and serialize the data to YAML.
- **Frontend:** A new API hook (`exportDatabaseYaml`) and a "Download YAML Export" button will be added to the `AdminSettingsPage`.
- **Exclusions:** Since the YAML export is redacted, a corresponding *import* feature will not be built, as importing redacted secrets would break tenant configurations.

---

### Step 1: Add Backend YAML Export Endpoint

**What & Why**
Add a new `GET` endpoint in the admin router to dump the full database to a YAML file. We will use `yaml.safe_dump` (PyYAML is already installed in the environment) to serialize the database models. Sensitive fields (`client_secret_enc` on `TenantConfig`, `password_hash` on `User`, and `public_key` on `WebAuthnCredential`) will be replaced with `<REDACTED>`.

**File Placement**
- New code → `api/routers/admin.py` → Add new endpoint `export_db_yaml` near the existing database maintenance functions.

**Pseudo Code**
```python
import yaml
from fastapi.responses import Response
from datetime import datetime
from db.database import get_session
from api.dependencies import require_admin
from api.schemas import AuthUser # whatever auth user is

@router.get("/export-db-yaml")
def export_db_yaml(_: AuthUser = Depends(require_admin)):
    from db.models import AppSettings, User, TenantConfig, Certificate, WebAuthnCredential, \
                          UserTenantEntitlement, ScheduledTask, TaskRunHistory, \
                          ZIAResource, ZPAResource, ZCCResource, RestorePoint, \
                          ZIATemplate, ZCCSnapshot, ZCCSnapshotItem, SyncLog, AuditLog
    with get_session() as session:
        data = {}
        # List all models explicitly to guarantee order and inclusion
        models = [AppSettings, User, TenantConfig, Certificate, WebAuthnCredential, 
                  UserTenantEntitlement, ScheduledTask, TaskRunHistory, 
                  ZIAResource, ZPAResource, ZCCResource, RestorePoint, 
                  ZIATemplate, ZCCSnapshot, ZCCSnapshotItem, SyncLog, AuditLog]
        
        for model in models:
            table_name = model.__tablename__
            rows = session.query(model).all()
            data[table_name] = []
            for row in rows:
                row_dict = {}
                for col in model.__table__.columns:
                    val = getattr(row, col.name)
                    # Redact sensitive fields
                    if col.name in ("client_secret_enc", "password_hash", "public_key") and val is not None:
                        val = "<REDACTED>"
                    elif isinstance(val, datetime):
                        val = val.isoformat()
                    row_dict[col.name] = val
                data[table_name].append(row_dict)
                
    yaml_content = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    return Response(
        content=yaml_content,
        media_type="application/x-yaml",
        headers={"Content-Disposition": 'attachment; filename="zscaler_db_export.yaml"'}
    )
```

**Blast Radius**
- Files affected: `api/routers/admin.py`
- Functions affected: None (new function added)
- APIs / Services / DBs affected: New REST endpoint added.
- Deployment risk: Low — pure read-only operation on the database.

**Impact & Negative Consequences**
- The YAML file may become large if the database contains millions of log entries or huge snapshot JSON payloads. We will use `safe_dump` which handles large payloads reasonably well, but it might consume significant memory for very large databases.

**Spaghetti Code Risk Check**
- [x] Single Responsibility: Pass
- [x] Separation of Concerns: Pass
- [x] Size Limits: Pass
- [x] God Class/Function: Pass
- [x] Naming Clarity: Pass

**Project Goal Alignment**
This change directly satisfies the goal of expanding the project with a DB export in YAML format.

**Test Coverage**
We will add a test `test_export_db_yaml` in the relevant test suite (or create one for `api/routers/admin.py` if tests exist) that authenticates as an admin, calls the endpoint, and verifies the response is valid YAML and that secrets are correctly replaced with `<REDACTED>`.

---

### Step 2: Add Frontend API Hook

**What & Why**
Add a frontend function to trigger the file download from the new backend endpoint. Because it returns a file attachment, the cleanest approach is to use the standard fetch API and trigger a blob download.

**File Placement**
- New code → `web/src/api/admin.ts` → Add `exportDatabaseYaml` function at the bottom.

**Pseudo Code**
```typescript
export async function exportDatabaseYaml(): Promise<void> {
  const token = localStorage.getItem("token"); // Assuming token is in localStorage, or use apiFetch behavior
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  
  const response = await fetch("/api/v1/admin/export-db-yaml", { headers });
  if (!response.ok) {
    throw new Error("Failed to export database");
  }
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "zscaler_db_export.yaml";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}
```

**Blast Radius**
- Files affected: `web/src/api/admin.ts`
- Functions affected: None (new function added)
- APIs / Services / DBs affected: None
- Deployment risk: Low

**Impact & Negative Consequences**
- No negative consequences identified.

**Spaghetti Code Risk Check**
- [x] Single Responsibility: Pass
- [x] Separation of Concerns: Pass
- [x] Size Limits: Pass
- [x] God Class/Function: Pass
- [x] Naming Clarity: Pass

**Project Goal Alignment**
Connects the UI to the backend functionality seamlessly.

**Test Coverage**
Verified manually through the UI. The core functionality is tested by the backend test.

---

### Step 3: Add UI Button for YAML Export

**What & Why**
Add a new section or button in `web/src/pages/AdminSettingsPage.tsx` under the Database Maintenance card, allowing administrators to click and download the redacted YAML export.

**File Placement**
- New code → `web/src/pages/AdminSettingsPage.tsx` → In `DatabaseMaintenanceCard` and a new `ExportDatabaseYamlSection` component.

**Pseudo Code**
```tsx
import { exportDatabaseYaml } from "../api/admin";

function ExportDatabaseYamlSection() {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function handleExport() {
    setLoading(true);
    setErr(null);
    try {
      await exportDatabaseYaml();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Export failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-xs text-gray-500">
        Export the entire database as a human-readable YAML file. 
        Sensitive secrets (like passwords and tenant keys) are permanently redacted.
      </p>
      {err && <p className="text-xs text-red-600">{err}</p>}
      <div>
        <button
          onClick={handleExport}
          disabled={loading}
          className="px-4 py-2 text-sm font-medium rounded-md bg-zs-500 hover:bg-zs-600 text-white disabled:opacity-50 transition-colors"
        >
          {loading ? "Exporting…" : "Export to YAML"}
        </button>
      </div>
    </div>
  );
}
// Add to DatabaseMaintenanceCard:
// <hr className="border-gray-100" />
// <p className="text-sm font-semibold text-gray-700 mb-1">Export Database (YAML)</p>
// <ExportDatabaseYamlSection />
```

**Blast Radius**
- Files affected: `web/src/pages/AdminSettingsPage.tsx`
- Functions affected: `DatabaseMaintenanceCard`
- APIs / Services / DBs affected: None
- Deployment risk: Low

**Impact & Negative Consequences**
- No negative consequences identified.

**Spaghetti Code Risk Check**
- [x] Single Responsibility: Pass
- [x] Separation of Concerns: Pass
- [x] Size Limits: Pass
- [x] God Class/Function: Pass
- [x] Naming Clarity: Pass

**Project Goal Alignment**
Exposes the required feature to end-users via the admin interface.

**Test Coverage**
Verified manually through the UI.