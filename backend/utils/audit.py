from utils.db import get_db_connection
from datetime import datetime
import json

def log_audit(actor_id: str, actor_role: str, action: str, outcome: str,
              patient_id: int = None, meta: dict = None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO privacy_gateway.audit_logs
        (timestamp, actor_id, actor_role, action, outcome, patient_id, meta)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (datetime.utcnow(),
         actor_id,
         actor_role,
         action,
         outcome,
         patient_id,
         json.dumps(meta) if meta else None)
    )
    conn.commit()
    cur.close()
    conn.close()
