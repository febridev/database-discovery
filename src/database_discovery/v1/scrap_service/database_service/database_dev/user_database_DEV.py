import os
import sqlalchemy
import datetime
from sqlalchemy import text 
from dotenv import load_dotenv
from database_discovery.v1.log import log_format
from collections import namedtuple


def auth_database():
    try:
        # LOAD ENV FILE
        load_dotenv()
        log_format("info", "[Auth Module] - Loading Env File Successful !")
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
        log_format("info", "[Auth DB Module] - Database Connection Successful !")
        return conn
    except OperationalError:
        log_format("error", "[Auth DB Module] - Wrong Username Or Password !!")
        exit()
    except InterfaceError:
        log_format(
            "error", "[Auth DB Module] - Host Not Found !! (Error Code: InterfaceError)"
        )
        exit()
    except ProgrammingError:
        log_format(
            "error",
            "[Auth DB Module] - Database Not Found !! (Error Code: ProgrammingError)",
        )
        exit()
    except Exception as e:
        log_format("error", f"[Auth DB Module] - Error {e}")
        exit()


def get_instance_list():
    conn = auth_database()
    query = text("""
    SELECT 
        hi.seq_id, 
        hi.instance_name,
        hi.ip_address, 
        mi.database_type, 
        CASE 
            WHEN mi.database_type = 'mysql' THEN 'mysql'
            WHEN mi.database_type = 'postgres' THEN 'postgres'
            WHEN mi.database_type = 'sqlserver' THEN 'master'
            ELSE NULL
        END AS default_database,
         mp.env_name
    FROM 
        tmproject mp
        JOIN tthinstance hi ON mp.seq_id = hi.project_id 
        JOIN tminstance_type mi ON mi.seq_id = hi.instance_type
    WHERE 
        hi.is_replica IN (0, 2) 
        AND mp.env_name = 'DEV'
        AND hi.instance_name IN ('dbops-d-cloudsql-mysql-test', 'dbops-d-cloudsql-postgres-xxew1', 'dbops-d-cloudsql-sqlserver-test1')
    ORDER BY 
        mp.project_id ASC, 
        hi.instance_name ASC;
    """)
    result = conn.execute(query)
    data = result.fetchall()
    conn.close()
    return data


def get_remote_connection(ip_address, default_database, database_type):
    load_dotenv()
    user = os.environ.get("REMOTE_DB_USER")
    password = os.environ.get("REMOTE_DB_PASSWORD")

    # Hardcode port sesuai dengan jenis database
    if database_type == 'mysql':
        port = 3306
        db_uri = f"mysql+mysqldb://{user}:{password}@{ip_address}:{port}/{default_database}"
    elif database_type == 'postgres':
        port = 5432
        db_uri = f"postgresql://{user}:{password}@{ip_address}:{port}/{default_database}"
    elif database_type == 'sqlserver':
        port = 1433
        db_uri = f"mssql+pymssql://{user}:{password}@{ip_address}:{port}/{default_database}"
    else:
        raise ValueError(f"Unsupported database type: {database_type}")

    try:
        engine = sqlalchemy.create_engine(db_uri)
        conn = engine.connect()
        #log_format("info", f"[Remote DB Module] - Connection to {database_name} [{database_type}] database at {ip_address} successful!")
        return conn
    except Exception as e:
        log_format("error", f"[Remote DB Module] - Error connecting to {default_database} [{database_type}] database at {ip_address}: {e}")
        return None


def get_usernames(conn, database_type):
    if database_type == 'mysql':
        query = """
         SELECT 
            user AS username,
            CASE 
                WHEN IFNULL(password_lifetime, 0) = 0 THEN NULL
                ELSE DATE(DATE_ADD(password_last_changed, INTERVAL password_lifetime DAY))
            END AS expired_date,
            IFNULL(
                CASE 
                    WHEN IFNULL(password_lifetime, 0) = 0 THEN NULL
                    ELSE DATEDIFF(DATE_ADD(password_last_changed, INTERVAL password_lifetime DAY), NOW())
                END, 
                0
            ) AS expired_in,
            CASE 
                WHEN (
                    IFNULL(
                        CASE 
                            WHEN IFNULL(password_lifetime, 0) = 0 THEN NULL
                            ELSE DATEDIFF(DATE_ADD(password_last_changed, INTERVAL password_lifetime DAY), NOW())
                        END, 
                        0
                    )
                ) < 0 THEN 'expired'
                WHEN (
                    IFNULL(
                        CASE 
                            WHEN IFNULL(password_lifetime, 0) = 0 THEN NULL
                            ELSE DATEDIFF(DATE_ADD(password_last_changed, INTERVAL password_lifetime DAY), NOW())
                        END, 
                        0
                    )
                ) = 0 THEN 'available, no expired date'
                ELSE 'available, with expired'
            END AS status_user
        FROM 
            mysql.user
        WHERE 
            password_last_changed IS NOT NULL
            AND account_locked = 'N'
            AND user NOT LIKE 'cloudsql%'
        ORDER BY 
            user ASC;
       """        
    elif database_type == 'postgres':
        query = """
        SELECT 
            usename AS username,
            TO_CHAR(valuntil, 'YYYY-MM-DD') AS expired_date,
            CASE 
                WHEN valuntil IS NOT NULL THEN EXTRACT(DAY FROM (valuntil - CURRENT_DATE))
                ELSE 0
            END AS expired_in,
            CASE 
                WHEN valuntil IS NOT NULL AND EXTRACT(DAY FROM (valuntil - CURRENT_DATE)) < 0 THEN 'expired'
                WHEN valuntil IS NOT NULL AND EXTRACT(DAY FROM (valuntil - CURRENT_DATE)) > 0 THEN 'available, with expired'
                ELSE 'available, no expired date'
            END AS status_user
        FROM 
            pg_user
        WHERE 
            usename NOT LIKE 'cloudsql%'
        ORDER BY usename ASC;
        """
    elif database_type == 'sqlserver':
        query = """
        SELECT 
            name AS username,
            CONVERT(VARCHAR(10), DATEADD(DAY, CONVERT(INT, LOGINPROPERTY(name, 'DaysUntilExpiration')), 
            CONVERT(DATETIME, LOGINPROPERTY(name, 'PasswordLastSetTime'))), 23) AS expired_date,
            ISNULL(DATEDIFF(DAY, GETDATE(), DATEADD(DAY, CONVERT(INT, LOGINPROPERTY(name, 'DaysUntilExpiration')), 
            CONVERT(DATETIME, LOGINPROPERTY(name, 'PasswordLastSetTime')))), 0) AS expired_in,
            CASE 
                WHEN ISNULL(DATEDIFF(DAY, GETDATE(), DATEADD(DAY, CONVERT(INT, LOGINPROPERTY(name, 'DaysUntilExpiration')), 
                CONVERT(DATETIME, LOGINPROPERTY(name, 'PasswordLastSetTime')))), 0) < 0 THEN 'expired'
                WHEN ISNULL(DATEDIFF(DAY, GETDATE(), DATEADD(DAY, CONVERT(INT, LOGINPROPERTY(name, 'DaysUntilExpiration')), 
                CONVERT(DATETIME, LOGINPROPERTY(name, 'PasswordLastSetTime')))), 0) = 0 THEN 'available, no expired date'
                ELSE 'available, with expired'
            END AS status_user
        FROM 
            sys.sql_logins
        WHERE 
            name NOT LIKE '##%'
            AND name NOT LIKE 'CloudDbSql%'
        ORDER BY 
            name ASC;
        """       
    else:
        raise ValueError(f"Unsupported database type: {database_type}")
    result = conn.execute(text(query))
    table_headers = result.fetchall()
    return table_headers

def get_local_usernames(seq_id):
    conn = auth_database()
    query = text("""
    SELECT 
        username, 
        expired_date, 
        expired_in, 
        status_user
    FROM ttuser_instance    
    WHERE h_instance_id = :seq_id AND is_deleted = 0;
    """)
    
    result = conn.execute(query, {'seq_id': seq_id})
    local_usernames = result.fetchall()
    conn.close()
    
    # Membuat namedtuple untuk konsistensi struktur data
    from collections import namedtuple
    UserInfo = namedtuple('UserInfo', ['username', 'expired_date', 'expired_in', 'status_user'])
    
    return {UserInfo(*row) for row in local_usernames}


def insert_usernames_header(seq_id, instance_name, username, expired_date, expired_in, status_user):
    conn = auth_database()
    insert_query = text("""
    INSERT INTO ttuser_instance (h_instance_id, username, expired_date, expired_in, status_user, created_by, updated_by)
    VALUES (:h_instance_id, :username, :expired_date, :expired_in, :status_user, 'interface', 'interface')
    """)
    log_format("info", f"[Insert username] - Starting transaction for Instance '{instance_name}' h_instance_id = {seq_id} | '{username}' ")
    try:
        conn.execute(insert_query, {
            'h_instance_id': seq_id,
            'username': username,
            'expired_date': expired_date,
            'expired_in': expired_in,
            'status_user': status_user
        })
        conn.commit()
        log_format("info", f"[Insert username] - Transaction committed for Instance '{instance_name}' h_instance_id = {seq_id} | '{username}' ")
    except Exception as e:
        log_format("error", f"[Insert username] - Failed to insert table name for Instance '{instance_name}' h_instance_id = {seq_id} | '{username}': {e}")
    finally:
        conn.close()


def mark_username_as_deleted(seq_id, instance_name, username, expired_date=None, expired_in=None, status_user='deleted'):
    conn = auth_database()
    update_query = text("""
    UPDATE ttuser_instance
    SET is_deleted = 1, 
        updated_by = 'interface',
        expired_date = :expired_date, 
        expired_in = :expired_in,
        status_user = :status_user
    WHERE h_instance_id = :seq_id AND username = :username;
    """)
    log_format("info", f"[Mark as deleted] - Marking table as deleted for Instance '{instance_name}' h_instance_id = {seq_id} | '{username}' ")
    try:
        conn.execute(update_query, {
            'seq_id': seq_id, 
            'username': username,
            'expired_date': expired_date,
            'expired_in': expired_in,
            'status_user': status_user
        })
        conn.commit()
        log_format("info", f"[Mark as deleted] - Successfully marked table as deleted for Instance '{instance_name}' h_instance_id = {seq_id} | '{username}' ")
    except Exception as e:
        log_format("error", f"[Mark as deleted] - Failed to mark table as deleted for Instance '{instance_name}' h_instance_id = {seq_id} | '{username}': {e}")
    finally:
        conn.close()

def update_username_details(seq_id, instance_name, username, expired_date, expired_in, status_user):
    conn = auth_database()
    update_query = text("""
    UPDATE ttuser_instance
    SET expired_date = :expired_date, 
        expired_in = :expired_in,
        status_user = :status_user                       
    WHERE h_instance_id = :seq_id AND username = :username;
    """)
    log_format("info", f"[update_username_details] - update daily username details (expired_date, expired_in, status_user) for Instance '{instance_name}' h_instance_id = {seq_id} | '{username}' ")   
    try:
        conn.execute(update_query, {'expired_date': expired_date, 'expired_in': expired_in, 'status_user': status_user, 'seq_id': seq_id, 'username': username})
        conn.commit()
        log_format("info", f"[update_username_details] - Successfully update daily username details (expired_date, expired_in, status_user) for Instance '{instance_name}' h_instance_id = {seq_id} | '{username}'")
    except Exception as e:
        log_format("error", f"[update_username_details] - Failed update daily username details (expired_date, expired_in, status_user) for Instance '{instance_name}' h_instance_id = {seq_id} | '{username}' : {e}")
    finally:
        conn.close()


def main():
    instances = get_instance_list()

    for instance in instances:
        seq_id = instance.seq_id
        instance_name = instance.instance_name
        ip_address = instance.ip_address
        default_database = instance.default_database
        database_type = instance.database_type

        # create connection remote database
        remote_conn = get_remote_connection(ip_address, default_database, database_type)
        if not remote_conn:
            log_format("error", f"[Main] - Failed to connect to remote database for instance {instance.instance_name}")
            continue

        # define namedtuple
        UserInfo = namedtuple('UserInfo', ['username', 'expired_date', 'expired_in', 'status_user'])

        # get username remote and local
        original_remote_usernames = set(get_usernames(remote_conn, database_type))
        local_usernames = get_local_usernames(seq_id)

        # debug
        log_format("info", f"list original remote username: {original_remote_usernames}")
        log_format("info", f"list local username: {local_usernames}")

        # Cleansing type data remote_usernames
        remote_usernames = set()
        for user in original_remote_usernames:
            # Konversi expired_date ke string jika tipe data datetime.date
            if isinstance(user.expired_date, datetime.date):
                # Buat namedtuple baru dengan expired_date sudah dikonversi
                cleansed_user = UserInfo(
                    username=user.username,
                    expired_date=user.expired_date.strftime('%Y-%m-%d'),
                    expired_in=user.expired_in,
                    status_user=user.status_user
                )
                remote_usernames.add(cleansed_user)
            else:
                remote_usernames.add(user)

        # Debugging
        log_format("info", f"list cleansing remote username: {remote_usernames}")
        log_format("info", f"list local username: {local_usernames}")

        
        log_format("info", f"Remote usernames count: {len(remote_usernames)}")
        log_format("info", f"Local usernames count: {len(local_usernames)}")

        log_format("info", f"list remote username: {remote_usernames}")
        log_format("info", f"list local username: {local_usernames}")


        # Compare Process
        usernames_to_insert = remote_usernames - local_usernames
        usernames_to_delete = local_usernames - remote_usernames
        usernames_to_update = remote_usernames & local_usernames

        # Debugging
        log_format("info", f"Usernames to insert: {[u.username for u in usernames_to_insert]}")
        log_format("info", f"Usernames to delete: {[u.username for u in usernames_to_delete]}")
        log_format("info", f"Usernames to update: {[u.username for u in usernames_to_update]}")

        # logic compare
        for username_data in usernames_to_insert:
            insert_usernames_header(seq_id, instance_name, username_data.username, username_data.expired_date, username_data.expired_in, username_data.status_user)

        for username_data in usernames_to_delete:
            mark_username_as_deleted(seq_id, instance_name, username_data.username, expired_date=username_data.expired_date, expired_in=username_data.expired_in, status_user='deleted')

        for username_data in usernames_to_update:
            update_username_details(seq_id, instance_name, username_data.username, username_data.expired_date, username_data.expired_in, username_data.status_user)

        # close connection remote database
        remote_conn.close()
if __name__ == "__main__":
    main()
