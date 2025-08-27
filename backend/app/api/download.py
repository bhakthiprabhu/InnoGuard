from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from core.security import get_current_role
from db.connection import get_db_connection
from services.audit_service import log_audit
import uuid
import io
import csv


ROLE_TO_VIEW = {
    "clinician": "privacy_gateway.patients",
    "researcher": "privacy_gateway.v_patients_researcher",
    "developer": "privacy_gateway.v_patients_developer"
}

router = APIRouter()

@router.get("/patients", summary="Download all patient data as CSV")
def download_patients(role: str = Depends(get_current_role)):
    """
    Download the entire dataset for a role as CSV.
    """
    user_id = str(uuid.uuid4())

    if role not in ROLE_TO_VIEW:
        log_audit(user_id, role, "DOWNLOAD_PATIENTS", "DENIED")
        raise HTTPException(status_code=403, detail="Forbidden")

    view_name = ROLE_TO_VIEW[role]
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {view_name};")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    # Write CSV to memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(colnames)
    writer.writerows(rows)
    output.seek(0)

    # Audit
    patient_ids = [row[0] for row in rows] if rows else []
    patient_id_for_audit = patient_ids[0] if role in ["clinician", "developer"] and patient_ids else None
    log_audit(
        actor_id=user_id,
        actor_role=role,
        action="DOWNLOAD_PATIENTS",
        outcome="SUCCESS",
        patient_id=patient_id_for_audit,
        meta={"row_count": len(rows)}
    )

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=patients.csv"}
    )
