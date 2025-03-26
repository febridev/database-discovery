import subprocess
import shlex
from sqlalchemy import text
from database_discovery.v1.auth_service.auth import check_login, auth_database
from database_discovery.v1.log import log_format

def get_instances(conn):
    query = text("""
        SELECT hi.seq_id, mp.project_id, hi.instance_name, mp.env_name
         FROM tmproject mp
        	JOIN tthinstance hi 
            ON mp.seq_id = hi.project_id
        where mp.env_name = 'PROD'
	        and mp.full_feature = 1
	        and hi.is_deleted = 0
	        and hi.is_replica in (0, 1, 2)
        order by mp.project_id asc, hi.instance_name asc
    """)
    result = conn.execute(query)
    instances = [dict(row) for row in result.mappings()]
    return instances

def get_databases(project_id, instance_name):
    command_gcloud = f"gcloud sql databases list --project={project_id} --instance={instance_name} --format='value(name)'"
    
    # Run the gcloud command and capture the output and errors
    process_gcloud = subprocess.Popen(shlex.split(command_gcloud), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output_gcloud, error_gcloud = process_gcloud.communicate()

    if process_gcloud.returncode != 0:
        log_format("error", f"Error executing gcloud command: {error_gcloud.strip()}")
        return []
    
    # Proceed to filter the output with grep
    command_grep = "grep -Ev '^(mysql|information_schema|performance_schema|sys|postgres|master|tempdb|model|msdb)$'"
    process_grep = subprocess.Popen(shlex.split(command_grep), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Pass gcloud output to grep
    output_grep, error_grep = process_grep.communicate(input=output_gcloud)

    if process_grep.returncode != 0:
        log_format("error", f"Error executing grep command: {error_grep.strip()}")
        return []
    
    return output_grep.strip().split('\n')

def get_existing_databases(conn, instance_id):
    query = text("""
        SELECT database_name
        FROM tthdatabase
        WHERE h_instance_id = :instance_id
    """)
    result = conn.execute(query, {"instance_id": instance_id})
    return set(row['database_name'] for row in result.mappings())


def insert_new_databases(conn, instance_id, new_databases):
    for db_name in new_databases:
        query = text("""
            INSERT INTO tthdatabase (h_instance_id, database_name, created_by, updated_by)
            VALUES (:h_instance_id, :database_name, 'interface', 'interface')
        """)
        conn.execute(query, {"h_instance_id": instance_id, "database_name": db_name})

def update_flag_isdeleted(conn, instance_id, old_databases):
    for db_name in old_databases:
        query = text("""         
            UPDATE tthdatabase
            SET is_deleted = 1
            WHERE h_instance_id = :h_instance_id 
                AND database_name = :database_name
        """)
        conn.execute(query, {"h_instance_id": instance_id, "database_name": db_name})

def main():
    # Check GCP authentication
    auth_status = check_login()
    if auth_status != "Authentication successful":
        log_format("error", "GCP authentication failed")
        return

    # Create database connection
    try:
        conn = auth_database()
    except Exception as e:
        log_format("error", f"Error creating database connection: {e}")
        return

    try:
        # Get instances from local database
        instances = get_instances(conn)
        log_format("info", f"Retrieved {len(instances)} instances from local database")

        for instance in instances:
            try:
                # Get existing databases for this instance
                existing_databases = get_existing_databases(conn, instance['seq_id'])
                
                # Get current databases from GCP
                current_databases = set(get_databases(instance['project_id'], instance['instance_name']))
                
                # Find new databases to insert and old databases to delete
                new_databases = current_databases - existing_databases
                old_databases = existing_databases - current_databases
                
                if new_databases:
                    # Insert only new databases
                    insert_new_databases(conn, instance['seq_id'], new_databases)
                    log_format("info", f"Inserted {len(new_databases)} new databases for instance {instance['instance_name']}: {', '.join(new_databases)}")

                if old_databases:
                    # Delete old databases
                    update_flag_isdeleted(conn, instance['seq_id'], old_databases)
                    log_format("info", f"update flag is_deleted {len(old_databases)} for instance {instance['instance_name']}: {', '.join(old_databases)}")

                if not new_databases and not old_databases:
                    log_format("info", f"No changes found for instance {instance['instance_name']}")
            except Exception as e:
                log_format("error", f"Error processing instance {instance['instance_name']}: {e}")

        conn.commit()
        log_format("info", "Database discovery and update completed successfully")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
