import json
import os
import subprocess
import shlex
import pandas as pd
from sqlalchemy import text
from dotenv import load_dotenv
from database_discovery.v1.auth_service.auth import check_login, auth_database
from database_discovery.v1.log import log_format


# Set Service Account Project ID
def get_project_fromdb():
    # GET Project from db tmproject
    sqltext = """
            SELECT
                project_id
            FROM tmproject
            """
    try:
        conn = auth_database()
        df = pd.read_sql(sqltext, conn, index_col=None)
        log_format("info", "[Instance Module] - Success Get Project ID From Database")
        return df
    except Exception as e:
        log_format("error", f"[Instance Module] - Error: {e}")
        exit()


# GET PROJECT ID FROM DATABASE
def get_project_id_db(v_project_id):
    # GET PROJECT ID FROM TABLE tmproject
    sqltext = f"""
            SELECT
                seq_id
            FROM tmproject
            WHERE project_id ='{v_project_id}'
            """
    try:
        conn = auth_database()
        result = conn.execute(text(sqltext)).fetchone()
        if result is not None:
            proj_id = int(result[0])
            log_format(
                "info", "[Instance Module] - Success Get Project ID From Database"
            )
            return proj_id
        else:
            log_format("warning", "[Instance Module] - Project ID Not Found")
            return None

    except Exception as e:
        log_format("error", f"[Instance Modeule] - Error: {e}")
        exit()


def get_instance_type_id_db(v_instance_type, v_db_type):
    # GET PROJECT ID FROM TABLE tmproject
    sqltext = f"""
            SELECT
                seq_id
            FROM tminstance_type
            WHERE instance_type = '{v_instance_type}'
            AND database_type = '{v_db_type}'
            """
    try:
        conn = auth_database()
        result = conn.execute(text(sqltext)).fetchone()
        if result is not None:
            instance_type_id = int(result[0])
            log_format(
                "info",
                f"[Instance Module] - Success Get Instance Type ({v_instance_type},{v_db_type}) ID From Database",
            )
            return instance_type_id
        else:
            log_format(
                "warning",
                f"[Instance Module] - Instance Type ({v_instance_type},{v_db_type}) ID Not Found",
            )
            return None

    except Exception as e:
        log_format("error", f"[Instance Module] - Error: {e}")
        exit()


def set_project_id(project_id):
    # Try Authentication
    try:
        check_login()
    except Exception as e:
        log_format("error", f"[Instance Module] - Error: {e}")
        exit()

    # EXEC GCLOUD SET PROJECT FROM project_id
    try:
        set_project_command = f"gcloud config set project {project_id}"
        set_project_command = shlex.split(set_project_command)
        set_project_output = subprocess.run(set_project_command)
        log_format("info", f"[Instance Module] - Success Set Project: {project_id}")
        return set_project_output
    except Exception as e:
        log_format("error", f"[Instance Module] - Error: {e}")
        exit()


def get_all_instance(v_project_id):
    try:
        check_login()
    except Exception as e:
        log_format("error", f"[Instance Module] - Error: {e}")
        exit()

    # LOAD ENV FILE
    load_dotenv()
    default_username = os.environ.get("DEFAULT_USERNAME")

    # GET ALL INSTANCE

    try:
        project_id = v_project_id
        # SET GCLOUD PROJECT
        set_project_id(project_id)

        get_instance_command = (
            f"gcloud sql instances list --project {project_id} --format json"
        )
        get_instance_command = shlex.split(get_instance_command)
        get_instance_output = subprocess.run(get_instance_command, capture_output=True)
        get_instance_output = json.loads(get_instance_output.stdout)

        # CHECK DATA IS NO EMPTY
        if len(get_instance_output) == 0:
            log_format("warning", f"[Instance Module] - Data Empty: {project_id}")
            return None
        else:
            # SET DATAFRAME WITH SPECIFIC COLUMN
            try:
                get_instance_output = [
                    {
                        k1: v1
                        for k1, v1 in k.items()
                        if k1
                        in [
                            "name",
                            "project",
                            "ipAddresses",
                            "instanceType",
                            "backendType",
                            "connectionName",
                            "databaseVersion",
                            "tier",
                            "masterInstanceName",
                            "databaseInstalledVersion",
                        ]
                    }
                    for k in get_instance_output
                ]
                # CREATE DATAFRAME FROM JSON
                df = pd.DataFrame(get_instance_output)
                log_format(
                    "info",
                    "[Instance Module] - Success Set Dataframe With Specific Column",
                )
            except Exception as e:
                log_format("error", f"[Instance Module] - Error: {e}")
                exit()

            try:
                # REMOVE EXTERNALE INSTANCE
                df = df[~df.backendType.isin(["EXTERNAL"])]
                log_format(
                    "info", "[Instance Module] - Success Remove External Instance"
                )
            except Exception as e:
                log_format("error", f"[Instance Module] - Error: {e}")
                exit()

            # GET DB TYPE
            try:
                df_db_type = (
                    str(df["databaseVersion"].to_string(index=False))
                    .split("_")[0]
                    .lstrip()
                )
                log_format("info", "[Instance Module] - Success Get DB Type")
            except Exception as e:
                log_format("error", f"[Instance Module] - Error: {e}")
                exit()

            # GET INSTANCE instanceType
            try:
                if (
                    str(df["instanceType"].to_string(index=False))
                    .split("_")[0]
                    .lstrip()
                    == "READ"
                ):
                    df_db_instance_type = "CLOUDSQL"
                else:
                    df_db_instance_type = (
                        str(df["instanceType"].to_string(index=False))
                        .split("_")[0]
                        .lstrip()
                        + "SQL"
                    )
                log_format("info", "[Instance Module] - Success Get Instance Type")
            except Exception as e:
                log_format("error", f"[Instance Module] - Error: {e}")
                exit()

            # CEK REPLICA OR NOT
            try:
                is_replica = [
                    0 if x == "CLOUD_SQL_INSTANCE" else 1 for x in df["instanceType"]
                ]
                log_format("info", "[Instance Module] - Success Check Replica")
            except Exception as e:
                log_format("error", f"[Instance Module] - Error: {e}")
                exit()

            # GET IP ADDRESS FROM OBJECT ipAddresses
            try:
                ip_address = df["ipAddresses"].str[0].str["ipAddress"]
                log_format("info", "[Instance Module] - Success Get IP Address")
            except Exception as e:
                log_format("error", f"[Instance Module] - Error: {e}")
                exit()

            # GET PROJECT ID FROM DB for specific Instance
            try:
                # project_id = get_project_id_db(str(df["project"][0]))
                project_id = [get_project_id_db(x) for x in df["project"]]
                log_format("info", "[Instance Module] - Success Get Project ID")
            except Exception as e:
                log_format("error", f"[Instance Module] - Error: {e}")
                exit()



            # ASSIGN NEW COLUMN TO DATAFRAME
            try:
                df = df.assign(
                    project_id=project_id,
                    created_by=default_username,
                    updated_by=default_username,
                    db_type=df_db_type,
                    db_instance_type=df_db_instance_type,
                    ip_address=ip_address,
                    instance_type=get_instance_type_id_db(
                        df_db_instance_type, df_db_type
                    ),
                    is_replica=is_replica,
                )
                log_format("info", "[Instance Module] - Success Assign New Column")
            except Exception as e:
                log_format("error", f"[Instance Module] - Error: {e}")
                exit()

            # RENAME COLUMN
            try:
                dfren = pd.DataFrame(
                    df.rename(
                        columns={
                            "name": "instance_name",
                            "connectionName": "connection_name",
                            "databaseVersion": "database_version",
                            "tier": "instance_tier",
                            "masterInstanceName": "master_instance_name",
                            "region": "zone",
                            "databaseInstalledVersion":"engine_version",
                        },
                    )
                )
                df_all_instance = dfren[
                    [
                        "project_id",
                        "instance_type",
                        "instance_name",
                        "ip_address",
                        "connection_name",
                        "is_replica",
                        "created_by",
                        "updated_by",
                    "engine_version",

                    ]
                ]
                log_format(
                    "info",
                    "[Instance Module] - Success Rename & Match Column Dataframe With Database",
                )
                return df_all_instance
            except Exception as e:
                log_format("error", f"[Instance Module] - Error: {e}")
                exit()

    except Exception as e:
        log_format("error", f"[Instance Module] - END Error: {e}")
        exit()


# insert to database
def upload_to_database(good_df):
    try:
        # setup connection database
        conn = auth_database()

        df1 = good_df
        # write dataframe to database
        df1.to_sql(name="tthinstance", con=conn, if_exists="append", index=False)

        # close connection
        conn.close()
        log_format(
            "info", "[Instance Module] - Finish Writing Project List to Database"
        )

    except Exception as e:
        log_format("error", f"[Instance Module] - Error: {e}")
        exit()
    return


def main_instance_list():
    # open connection database
    conn = auth_database()
    # cek data from database
    exist_fromdb = pd.read_sql(
        text(
            """
            SELECT
                project_id,
                instance_type,
                instance_name,
                ip_address,
                connection_name,
                is_replica,
                engine_version
            FROM tthinstance
            """
        ),
        conn,
    )
    # cek exsiting data from database
    total = int(len(exist_fromdb))
    if total == 0:
        try:
            all_project = get_project_fromdb()
            total_data = len(get_project_fromdb())
            log_format("info", "[Instance Module] - main Func Success Get All Project")
            # insert all data to database
            # LOOP DATAFRAME
            for i in range(total_data):
                project_id = all_project.iloc[i].iat[0]
                df_to_db = get_all_instance(project_id)
                if df_to_db is None:
                    log_format(
                        "info", f"[Instance Module] - No Data Available {df_to_db}"
                    )
                    continue
                else:
                    upload_to_database(df_to_db)
                    log_format(
                        "info", "[Instance Module] - Success Upload Data to Database"
                    )

        except Exception as e:
            log_format("error", f"Error: {e}")
            exit()
    else:
        try:
            # compare dataframe from db and gcloud command
            log_format("info", "[Instance Module] - START COMPARE DATAFRAME")
            cdf = pd.DataFrame()
            all_project = get_project_fromdb()
            total_data = len(get_project_fromdb())
            log_format("info", "[Instance Module] - main Func Success Get All Project")
            # insert all data to database
            # LOOP DATAFRAME
            for i in range(total_data):
                project_id = all_project.iloc[i].iat[0]
                df_to_db = get_all_instance(project_id)
                if df_to_db is None:
                    log_format(
                        "info", f"[Instance Module] - No Data Available {df_to_db}"
                    )
                    continue
                else:
                    cdf = pd.concat([cdf, df_to_db], ignore_index=True)

            n_merge = cdf.merge(
                exist_fromdb,
                on=["instance_name", "ip_address"],
            )
            # COMPARE BETWEEN DB AND NEW DATAFRAME
            hasil = cdf[
                (~cdf.instance_name.isin(n_merge.instance_name))
                & (~cdf.ip_address.isin(n_merge.ip_address))
            ]
            log_format("info", "[Instance Module] - Success Compare Instance List")

            # if hasil compare is 0
            if len(hasil) == 0:
                log_format("info", "[Instance Module] - No New Instance Found")
            else:
                log_format("info", "[Instance Module] - New Instance Found")
                # insert only new data to database
                upload_to_database(hasil)
                log_format(
                    "info",
                    "[Instance Module] - Finish Writing New Instance List to Database",
                )

        except Exception as e:
            log_format("error", f"[Instance Module] - Error: {e}")
            exit()
    return


if __name__ == "__main__":
    main_instance_list()
