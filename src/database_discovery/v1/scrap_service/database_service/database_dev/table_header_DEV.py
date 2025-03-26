import sqlalchemy
from sqlalchemy import text 
from database_discovery.v1.auth_service.auth import auth_database
from database_discovery.v1.log import log_format
from database_discovery.v1.scrap_service.database_service.database_dev.database_detail_DEV import get_database_list, get_remote_connection


def get_table_name(conn, database_type):
    if database_type == 'mysql':
        query = """
        SELECT table_schema as schema_name, table_name 
        from information_schema.tables 
        where table_schema = database() 
            and table_type = 'BASE TABLE'
        order by schema_name asc, table_name asc;
        """        
    elif database_type == 'postgres':
        query = """
        SELECT table_schema as schema_name, table_name 
        FROM information_schema.tables 
        WHERE table_type = 'BASE TABLE' 
        	and table_schema not in ('pg_catalog', 'information_schema') 
        ORDER BY schema_name asc, table_name asc;
        """
    elif database_type == 'sqlserver':
        query = """
        SELECT table_schema as schema_name, table_name 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        order by schema_name asc, table_name asc;
        """       
    else:
        raise ValueError(f"Unsupported database type: {database_type}")
    result = conn.execute(text(query))
    table_headers = result.fetchall()
    return table_headers


def get_local_table_names(seq_id):
    conn = auth_database()
    query = text("""
    SELECT schema_name, table_name FROM tthtable_discovery 
    WHERE h_database_id = :seq_id AND is_deleted = 0;
    """)
    result = conn.execute(query, {'seq_id': seq_id})
    local_tables = result.fetchall()
    conn.close()
    return set(local_tables)


def insert_table_header(seq_id, schema_name, table_name):
    conn = auth_database()
    insert_query = text("""
    INSERT INTO tthtable_discovery (h_database_id, schema_name, table_name, created_by, updated_by)
    VALUES (:h_database_id, :schema_name, :table_name, 'interface', 'interface')
    """)
    log_format("info", f"[Insert table name] - Starting transaction for database ID {seq_id}: {schema_name}.{table_name}.")
    try:
        conn.execute(insert_query, {'h_database_id': seq_id, 'schema_name': schema_name, 'table_name': table_name})
        conn.commit()
        log_format("info", f"[Insert table name] - Transaction committed for database ID {seq_id} {schema_name}.{table_name}.")
    except Exception as e:
        log_format("error", f"[Insert table name] - Failed to insert table name for database ID {seq_id} {schema_name}.{table_name}: {e}")
    finally:
        conn.close()


def mark_table_as_deleted(seq_id, schema_name, table_name):
    conn = auth_database()
    update_query = text("""
    UPDATE tthtable_discovery
    SET is_deleted = 1, updated_by = 'interface'
    WHERE h_database_id = :seq_id AND schema_name = :schema_name AND table_name = :table_name;
    """)
    log_format("info", f"[Mark as deleted] - Marking table as deleted for database ID {seq_id}: {schema_name}.{table_name}.")
    try:
        conn.execute(update_query, {'seq_id': seq_id, 'schema_name': schema_name, 'table_name': table_name})
        conn.commit()
        log_format("info", f"[Mark as deleted] - Successfully marked table as deleted for database ID {seq_id} {schema_name}.{table_name}.")
    except Exception as e:
        log_format("error", f"[Mark as deleted] - Failed to mark table as deleted for database ID {seq_id} {schema_name}.{table_name}: {e}")
    finally:
        conn.close()


def main():
    database_list = get_database_list()

    for db_info in database_list:
        seq_id, ip_address, database_name, database_type, env_name = db_info
        remote_conn = get_remote_connection(ip_address, database_name, database_type)
        if remote_conn:
            remote_tables = set(get_table_name(remote_conn, database_type))
            local_tables = get_local_table_names(seq_id)

            # Insert new tables from remote that are not in local
            for table in remote_tables - local_tables:
                schema_name, table_name = table
                insert_table_header(seq_id, schema_name, table_name)

            # Mark tables as deleted in local if not found in remote
            for table in local_tables - remote_tables:
                schema_name, table_name = table
                mark_table_as_deleted(seq_id, schema_name, table_name)

            remote_conn.close()


if __name__ == "__main__":
    main()
