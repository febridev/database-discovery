import os
import sqlalchemy
from sqlalchemy import text
from database_discovery.v1.log import log_format
from database_discovery.v1.scrap_service.database_service.database_dev.database_detail_DEV import get_database_list, get_remote_connection
from dotenv import load_dotenv

# notes = dikarenakan ada bug di function `log_format`, sehingga hasil log me-looping lebih banyak, ada penyesuain management log di feature ini.
#         yang dilempar ke log_format hanya status `error` dan  beberapa log `info` yang dilempar ke function log_format

#use function auth_database() minimize log info
def auth_database():
    try:
        # LOAD ENV FILE
        load_dotenv()
        print("[INFO] [Auth Module] - Loading Env File Successful!")
    except Exception as e:
        log_format("error", f"[Auth Module] - Error {e}")
        exit()

    # DEFINE DATABASE PARAM
    user_db = os.environ.get("DB_USER")
    password_db = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")
    db_name = os.environ.get("DB_NAME")
    db_uri = f"mysql+pymysql://{user_db}:{password_db}@{db_host}:{db_port}/{db_name}"
    try:
        engine = sqlalchemy.create_engine(db_uri)
        conn = engine.connect()
        print("[INFO] [Auth DB Module] - Database Connection Successful!")
        return conn
    except OperationalError:
        log_format("error", "[Auth DB Module] - Wrong Username Or Password!")
        exit()
    except InterfaceError:
        log_format("error", "[Auth DB Module] - Host Not Found! (Error Code: InterfaceError)")
        exit()
    except ProgrammingError:
        log_format("error", "[Auth DB Module] - Database Not Found! (Error Code: ProgrammingError)")
        exit()
    except Exception as e:
        log_format("error", f"[Auth DB Module] - Error {e}")
        exit()


def get_table_detail(conn, database_type):
    if database_type == 'mysql':
        query = """
        SELECT TABLE_SCHEMA as schema_name, TABLE_NAME as table_name, TABLE_ROWS as total_row, ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) as table_size_mb 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = database() 
        ORDER BY schema_name asc, table_name asc;
        """
    elif database_type == 'postgres':
        query = """
        SELECT t.schemaname as schema_name , relname as table_name, n_live_tup as total_row, ROUND(pg_total_relation_size(relid) / 1024 / 1024, 2) as table_size_mb 
        FROM pg_stat_user_tables t 
        ORDER BY schema_name asc, table_name asc;
        """
    elif database_type == 'sqlserver':
        query = """
        SELECT s.name AS schema_name, t.name AS table_name, p.rows AS total_row, ROUND(SUM(a.total_pages) * 8 / 1024.0, 2) AS table_size_mb
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        JOIN sys.indexes i ON t.object_id = i.object_id
        JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
        JOIN sys.allocation_units a ON p.partition_id = a.container_id
        WHERE t.type = 'U'
        GROUP BY s.name, t.name, p.rows
        ORDER BY schema_name asc, table_name asc;
        """
    else:
        raise ValueError(f"Unsupported database type: {database_type}")

    result = conn.execute(text(query)).mappings()  # Add .mappings() here to return dictionaries
    table_details = [row for row in result]
    return table_details

def get_table_name_dbdiscovery(conn, instance_id):
    query = text("""         
        SELECT seq_id, schema_name, table_name
        FROM tthtable_discovery 
        WHERE is_deleted = 0
        ORDER BY schema_name asc, table_name asc        
    """)
    result = conn.execute(query, {"instance_id": instance_id})
    return {f"{row['schema_name']}.{row['table_name']}": row['seq_id'] for row in result.mappings()}

def insert_table_detail(seq_id, total_row, table_size_mb):
    conn = auth_database()
    insert_query = text("""
    INSERT INTO ttdtable_discovery (h_table_id, total_row, table_size_mb, created_by, updated_by)
    VALUES (:seq_id, :total_row, :table_size_mb, 'interface', 'interface')
    """)
    #log_format("info", f"[Insert table name] - Starting transaction for {seq_id}.")
    try:
        conn.execute(insert_query, {'seq_id': seq_id, 'total_row': total_row, 'table_size_mb': table_size_mb})
        conn.commit()
        #log_format("info", f"[Insert table name] - Transaction committed for table ID {seq_id}.")
    except Exception as e:
        log_format("error", f"[Insert table name] - Failed to insert for table ID {seq_id}: {e}")
    finally:
        conn.close()


def get_index_size(conn, database_type):
    if database_type == 'mysql':
        query = """
        SELECT t.database_name as schema_name, table_name, index_name, ROUND(stat_value * @@innodb_page_size / 1024 / 1024, 2) AS index_size_mb
        FROM mysql.innodb_index_stats t
        WHERE stat_name = 'size' AND database_name = database()
        ORDER BY schema_name asc, table_name asc;
        """
    elif database_type == 'postgres':
        query = """
        SELECT idx.schemaname as schema_name, idx.tablename as table_name, idx.indexname AS index_name, pg_relation_size(stat.indexrelid) / 1024 / 1024 AS index_size_mb
        FROM pg_stat_user_indexes AS stat
        JOIN pg_indexes AS idx ON idx.indexname = stat.indexrelname
        ORDER BY schema_name asc, table_name asc;
        """
    elif database_type == 'sqlserver':
        query = """
        SELECT s.name AS schema_name, tn.name AS table_name, ix.name AS index_name, ROUND(SUM(sz.used_page_count) * 8 / 1024.0, 2) AS index_size_mb
        FROM sys.dm_db_partition_stats AS sz
        INNER JOIN sys.indexes AS ix ON sz.object_id = ix.object_id AND sz.index_id = ix.index_id
        INNER JOIN sys.tables tn ON tn.object_id = ix.object_id
        INNER JOIN sys.schemas s ON tn.schema_id = s.schema_id
        GROUP BY s.name, tn.name, ix.name
        ORDER BY schema_name asc, table_name asc;
        """
    else:
        raise ValueError(f"Unsupported database type: {database_type}")

    result = conn.execute(text(query)).mappings()  # Add .mappings() here to return dictionaries
    index_details = [row for row in result]
    return index_details

def insert_index_detail(h_table_id, index_name, index_size_mb):
    conn = auth_database()
    insert_query = text("""
    INSERT INTO ttdindex_discovery (h_table_id, index_name, index_size_mb, created_by, updated_by)
    VALUES (:h_table_id, :index_name, :index_size_mb, 'interface', 'interface')
    """)
    #log_format("info", f"[Insert Index Detail] - Starting transaction for index {index_name}.")
    try:
        conn.execute(insert_query, {'h_table_id': h_table_id, 'index_name': index_name, 'index_size_mb': index_size_mb})
        conn.commit()
        #log_format("info", f"[Insert Index Detail] - Transaction committed for index {index_name}.")
    except Exception as e:
        log_format("error", f"[Insert Index Detail] - Failed to insert index {index_name} for table ID {h_table_id}: {e}")
    finally:
        conn.close()

def main():
    # Step 1: Get all database connections list
    db_list = get_database_list()

    # Step 2: Loop through each database connection for remote access
    for db_info in db_list:
        seq_id, ip_address, db_name, db_type, env_name = db_info
        remote_conn = get_remote_connection(ip_address, db_name, db_type)

        if remote_conn:
            # Step 3: Fetch table and index details from remote database
            table_details = get_table_detail(remote_conn, db_type)
            index_sizes = get_index_size(remote_conn, db_type)
            remote_conn.close()
        else:
            log_format("error", f"[Main] - Failed to connect to {db_name} at {ip_address}.")
            continue

        # Step 4: Connect to local db discovery to fetch table names and IDs
        local_conn = auth_database()
        db_discovery_tables = get_table_name_dbdiscovery(local_conn, seq_id)
        local_conn.close()

        # Step 5: Insert table details into ttdtable_discovery
        for table_detail in table_details:
            schema_table_key = f"{table_detail['schema_name']}.{table_detail['table_name']}"
            if schema_table_key in db_discovery_tables:
                h_table_id = db_discovery_tables[schema_table_key]
                insert_table_detail(h_table_id, table_detail['total_row'], table_detail['table_size_mb'])

        # Step 6: Insert index details into ttdindex_discovery
        for index_detail in index_sizes:
            schema_table_key = f"{index_detail['schema_name']}.{index_detail['table_name']}"
            if schema_table_key in db_discovery_tables:
                h_table_id = db_discovery_tables[schema_table_key]
                insert_index_detail(h_table_id, index_detail['index_name'], index_detail['index_size_mb'])

        log_format("info", f"[Main] - Completed processing for database {db_name} on {ip_address}.")

if __name__ == "__main__":
    main()
