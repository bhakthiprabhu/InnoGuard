from fastapi import APIRouter, Depends, HTTPException
from utils.auth import get_current_role
from utils.db import get_db_connection
from utils.audit import log_audit

router = APIRouter()

ROLE_TO_VIEW = {
    "clinician": "privacy_gateway.patients",
    "researcher": "privacy_gateway.v_patients_researcher",
    "developer": "privacy_gateway.v_patients_developer"
}

@router.get("/")
def get_patients(role: str = Depends(get_current_role)):
    import uuid
    user_id = str(uuid.uuid4())  # Replace with real user_id from JWT in prod

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
    cur.execute(f"SELECT * FROM {view_name} LIMIT 100;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Extract patient IDs (first column)
    patient_ids = [row[0] for row in rows] if rows else []

    # Only log real IDs for clinician/developer
    patient_id_for_audit = patient_ids[0] if role in ["clinician", "developer"] and patient_ids else None

    # For researchers, store pseudonymized IDs in meta
    log_audit(
        actor_id=user_id,
        actor_role=role,
        action="VIEW_PATIENTS",
        outcome="SUCCESS",
        patient_id=patient_id_for_audit,
        meta={"returned_ids": patient_ids, "limit": 100}
    )

    return {"role": role, "data": rows}
