from db.connection import get_db_connection
import json

def log_audit(actor_id, actor_role, action, outcome, patient_id=None, meta=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO privacy_gateway.audit_logs
        (actor_id, actor_role, action, outcome, patient_id, meta)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (actor_id, actor_role, action, outcome, patient_id, json.dumps(meta) if meta else None))
    conn.commit()
    cur.close()
    conn.close()

