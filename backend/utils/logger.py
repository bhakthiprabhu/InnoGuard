def log_access(user_role, action, patient_id=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO privacy_gateway.audit_logs (user_role, action, patient_id, accessed_at)
        VALUES (%s, %s, %s, NOW())
    """, (user_role, action, patient_id))
    conn.commit()
    cur.close()
    conn.close()
