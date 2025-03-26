import json
import os
import subprocess
import shlex
import pandas as pd
from sqlalchemy import text
from dotenv import load_dotenv
from database_discovery.v1.auth_service.auth import check_login, auth_database
from database_discovery.v1.log import log_format


# get only project list
def get_only_project_list():
    # check authentication gcp
    try:
        check_login()
    except Exception as e:
        log_format("error", f"[Project Module] - Error: {e}")
        exit()

    # LOAD ENV FILE
    load_dotenv()
    default_username = os.environ.get("DEFAULT_USERNAME")

    check_login()
    # START GCLOUD COMMAND
    try:
        log_format("info", "[Project Module] - Getting Project List")
        proj_command = "gcloud projects list --format json"
        proj_command = shlex.split(proj_command)
        proj_output = subprocess.run(proj_command, capture_output=True)
        proj_output = json.loads(proj_output.stdout)
        # SET JSON TO DATAFRAME
        proj_output = [
            {
                k1: v1
                for k1, v1 in d.items()
                if k1 in ["projectId", "projectNumber", "name", "createTime"]
            }
            for d in proj_output
        ]
        df = pd.DataFrame(proj_output)

        # SET createTime as DateTime
        df.createTime = pd.to_datetime(df.createTime).dt.strftime("%Y-%m-%d %H:%M:%S")

        # SET Env name
        # env_name = str(df.name[-4:])
        env_mapping = {"prd": "PROD", "stg": "STAGING", "dev": "DEV", "prod": "PROD"}
        env_name = [
            env_mapping[str(x[-4:]).replace("-", "")]
            if str(x[-4:]).replace("-", "") in env_mapping
            else "NONE"
            for x in df["name"]
        ]

        # assign default value for created_by and updated_by
        df = df.assign(
            created_by=default_username, updated_by=default_username, env_name=env_name
        )

        log_format("info", "[Project Module] - Finish Getting Project List")

        # rename column
        df1 = pd.DataFrame(
            df.rename(
                columns={
                    "projectNumber": "project_number",
                    "projectId": "project_id",
                    "name": "project_name",
                    "createTime": "project_createtime",
                }
            )
        )
        log_format("info", "[Project Module] - Finish Rename Column")
        return df1
    except Exception as e:
        log_format("error", f"[Project Module] - Error: {e}")
        exit()


# insert to database
def upload_to_database(good_df):
    try:
        # setup connection database
        conn = auth_database()

        df1 = good_df
        # write dataframe to database
        df1.to_sql(name="tmproject", con=conn, if_exists="append", index=False)

        # close connection
        conn.close()
        log_format("info", "[Project Module] - Finish Writing Project List to Database")

    except Exception as e:
        log_format("error", f"[Project Module] - Error: {e}")
        exit()
    return


# compare project between gcloud and database before insert
def compare_project_list():
    # open connection database
    conn = auth_database()
    # cek data from database
    exist_fromdb = pd.read_sql(
        text(
            """
            SELECT 
            project_createtime
            ,project_name
            ,project_id
            ,project_number
            ,created_by
            ,updated_by
            FROM tmproject
            """
        ),
        conn,
    )
    # cek exsiting data from database
    total = int(len(exist_fromdb))
    if total == 0:
        try:
            # insert all data to database
            all_project = get_only_project_list()
            upload_to_database(all_project)
            log_format(
                "info", "[Project Module] - Finish Writing Project List to Database"
            )
        except Exception as e:
            log_format("error", f"[Project Module] - Error: {e}")
            exit()
    else:
        try:
            # compare dataframe from db and gcloud command
            new_project = get_only_project_list()
            n_merge = new_project.merge(
                exist_fromdb, on=["project_name", "project_id", "project_number"]
            )
            hasil = new_project[
                (~new_project.project_name.isin(n_merge.project_name))
                & (~new_project.project_id.isin(n_merge.project_id))
                & (~new_project.project_number.isin(n_merge.project_number))
            ]
            log_format("info", "[Project Module] - Finish Compare Project List")

            # if hasil compare is 0
            if len(hasil) == 0:
                log_format("info", "[Project Module] - No New Project Found")
            else:
                log_format("info", "[Project Module] - New Project Found")
                # insert only new data to database
                upload_to_database(hasil)
                log_format(
                    "info",
                    "[Project Module] - Finish Writing New Project List to Database",
                )

        except Exception as e:
            log_format("error", f"[Project Module] - Error: {e}")
            exit()
    return


if __name__ == "__main__":
    # get_only_project_list()
    # get_project_list()
    compare_project_list()
