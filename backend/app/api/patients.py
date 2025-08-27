from fastapi import APIRouter, Depends, HTTPException, Query
from core.security import get_current_role
from db.connection import get_db_connection
from services.audit_service import log_audit
import uuid

router = APIRouter()

# Map roles to the appropriate DB view/table
ROLE_TO_VIEW = {
    "clinician": "privacy_gateway.patients",
    "researcher": "privacy_gateway.v_patients_researcher",
    "developer": "privacy_gateway.v_patients_developer"
}


@router.get("/", summary="Get patients data with pagination")
def get_patients(
    role: str = Depends(get_current_role),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
):
    """
    Return patient data based on user role:
    - clinician → full raw patient data
    - researcher → pseudonymized data
    - developer → synthetic data
    Supports pagination with `limit` and `offset`.
    """
    user_id = str(uuid.uuid4())

    if role not in ROLE_TO_VIEW:
        log_audit(
            actor_id=user_id,
            actor_role=role,
            action="VIEW_PATIENTS",
            outcome="DENIED"
        )
        raise HTTPException(status_code=403, detail="Forbidden")

    view_name = ROLE_TO_VIEW[role]
    conn = get_db_connection()
    cur = conn.cursor()

    # Get total count for pagination metadata
    cur.execute(f"SELECT COUNT(*) FROM {view_name};")
    total_count = cur.fetchone()[0]

    # Fetch limited records with offset
    cur.execute(f"SELECT * FROM {view_name} LIMIT %s OFFSET %s;", (limit, offset))
    rows = cur.fetchall()

    # Extract column names
    col_names = [desc[0] for desc in cur.description]

    # Convert rows → list of dicts (key-value pairs)
    results = [dict(zip(col_names, row)) for row in rows]

    cur.close()
    conn.close()

    # Extract patient IDs for audit
    patient_ids = [r[col_names[0]] for r in results] if results else []

    patient_id_for_audit = None
    if role in ["clinician", "developer"] and patient_ids:
        patient_id_for_audit = patient_ids[0]

    meta_info = {
        "returned_ids": patient_ids,
        "limit": limit,
        "offset": offset,
        "total": total_count,
    }

    log_audit(
        actor_id=user_id,
        actor_role=role,
        action="VIEW_PATIENTS",
        outcome="SUCCESS",
        patient_id=patient_id_for_audit,
        meta=meta_info
    )

    return {
        "role": role,
        "data": results,  # now key-value format
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total_count,
            "has_next": offset + limit < total_count
        }
    }
