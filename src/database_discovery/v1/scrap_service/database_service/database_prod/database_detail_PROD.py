import os
import sqlalchemy
from sqlalchemy import text 
from dotenv import load_dotenv
from database_discovery.v1.auth_service.auth import auth_database
from database_discovery.v1.log import log_format

def get_database_list():
    conn = auth_database()
    query = text("""
    SELECT hd.seq_id, hi.ip_address, hd.database_name, mi.database_type, mp.env_name
    FROM tmproject mp
        JOIN tthinstance hi ON mp.seq_id = hi.project_id 
        JOIN tminstance_type mi ON mi.seq_id = hi.instance_type
        JOIN tthdatabase hd ON hd.h_instance_id = hi.seq_id
    WHERE hi.is_replica in (0, 2) 
        AND hd.is_deleted = 0
        AND mp.env_name = 'PROD'
    ORDER BY mp.project_id asc, hi.instance_name asc, hd.database_name
    """)
    result = conn.execute(query)
    data = result.fetchall()
    conn.close()
    return data

def get_remote_connection(ip_address, database_name, database_type):
    load_dotenv()
    user = os.environ.get("REMOTE_DB_USER")
    password = os.environ.get("REMOTE_DB_PASSWORD")

    # Hardcode port sesuai dengan jenis database
    if database_type == 'mysql':
        port = 3306
        db_uri = f"mysql+mysqldb://{user}:{password}@{ip_address}:{port}/{database_name}"
    elif database_type == 'postgresql':
        port = 5432
        db_uri = f"postgresql://{user}:{password}@{ip_address}:{port}/{database_name}"
    elif database_type == 'sqlserver':
        port = 1433
        db_uri = f"mssql+pymssql://{user}:{password}@{ip_address}:{port}/{database_name}"
    else:
        raise ValueError(f"Unsupported database type: {database_type}")

    try:
        engine = sqlalchemy.create_engine(db_uri)
        conn = engine.connect()
        #log_format("info", f"[Remote DB Module] - Connection to {database_name} [{database_type}] database at {ip_address} successful!")
        return conn
    except Exception as e:
        log_format("error", f"[Remote DB Module] - Error connecting to {database_name} [{database_type}] database at {ip_address}: {e}")
        return None

def calculate_database_size(conn, database_type):
    if database_type == 'mysql':
        query = "SELECT ROUND(IFNULL(SUM(data_length + index_length) / 1024 / 1024, 0), 3) AS size_mb FROM information_schema.tables WHERE table_schema = DATABASE();"
    elif database_type == 'postgresql':
        query = "SELECT ROUND(pg_database_size(current_database()) / 1024 / 1024, 3) AS size_mb;"
    elif database_type == 'sqlserver':
        query = "SELECT CAST(SUM(size * 8 / 1024.0) AS DECIMAL(10, 3)) AS size_mb FROM sys.master_files WHERE DB_NAME(database_id) = DB_NAME() AND type = 0;"
    else:
        raise ValueError(f"Unsupported database type: {database_type}")

    # Use 'text()' for query string
    result = conn.execute(text(query))
    size_mb = result.scalar()
    return size_mb

def insert_database_size(seq_id, size_mb):
    conn = auth_database()
    insert_query = text("""
    INSERT INTO ttddatabase (h_database_id, database_size_mb, created_by, updated_by)
    VALUES (:h_database_id, :database_size_mb, 'interface', 'interface')
    """)
    log_format("info", f"[Insert DB Size] - Starting transaction for database ID {seq_id}: {size_mb} mb.")
    try:
        conn.execute(insert_query, {'h_database_id': seq_id, 'database_size_mb': size_mb})
        conn.commit()  # Ensure the transaction is committed
        log_format("info", f"[Insert DB Size] - Transaction committed for database ID {seq_id}: {size_mb} mb.")
    except Exception as e:
        log_format("error", f"[Insert DB Size] - Failed to insert size for database ID {seq_id}: {e}")
    finally:
        conn.close()


def main():
    database_list = get_database_list()

    for db_info in database_list:
        seq_id, ip_address, database_name, database_type, env_name = db_info
        remote_conn = get_remote_connection(ip_address, database_name, database_type)
        if remote_conn:
            size_mb = calculate_database_size(remote_conn, database_type)
            insert_database_size(seq_id, size_mb)
            remote_conn.close()

if __name__ == "__main__":
    main()
