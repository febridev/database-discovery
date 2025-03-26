import json
import os
import subprocess
import shlex
import pandas as pd
from dotenv import load_dotenv
from database_discovery.v1.auth_service.auth import check_login, auth_database
from database_discovery.v1.log import log_format


# GET ALL HEADER INSTANCE
def get_all_header_instance():
    sqltext = """
           SELECT
            ih.seq_id,
            ih.instance_name,
            pj.project_id
           FROM tthinstance ih
           INNER JOIN tmproject pj ON ih.project_id = pj.seq_id
           ORDER BY ih.seq_id asc;
    """
    # GET ALL INSTANCE
    try:
        conn = auth_database()
        df = pd.read_sql(sqltext, con=conn)
        log_format(
            "info", "[Instance Detail Module] - Successfully get all header instance"
        )
        return df
    except Exception as e:
        print()
        log_format("error", f"[Instance Detail Module] - Error: {e}")


# EXPLODE TIER CPU N RAM
def explode_instance_tier(v_instance_tier):
    # SET tier variable as v_instance_tier
    tier = v_instance_tier
    # SPLIT v instance tier to list
    split_hasil = tier.split("-")
    try:
        # CHECK CUSTOM OR NOT
        if split_hasil[1] != "custom":
            # GET TIER LIST FROM GCP
            get_tier_text = (
                f"gcloud sql tiers list --filter='tier={v_instance_tier}' --format json"
            )
            get_tier_command = shlex.split(get_tier_text)
            get_tier_output = subprocess.check_output(get_tier_command)
            get_tier_output = json.loads(get_tier_output)

            # GET & CONVERT RAM TO GB
            ram_gb = float(get_tier_output[0].get("RAM")) / 1024 / 1024 / 1024

            # GET CPU CORE
            if len(split_hasil) == 3:
                cpu_core = 1
            else:
                cpu_core = split_hasil[3]

            cpu_memory = [cpu_core, ram_gb]
            log_format(
                "info", "[Instance Detail Module] - Successfully explode instance tier"
            )
            return cpu_memory
        else:
            rev_hasil = split_hasil[::-1]
            v_cpu = rev_hasil[1]
            v_memory = float(rev_hasil[0]) / 1024
            cpu_memory = [v_cpu, v_memory]
            log_format(
                "info", "[Instance Detail Module] - Successfully explode instance tier"
            )
            return cpu_memory

    except Exception as e:
        log_format("error", f"[Instance Detail Module] - Error: {e}")
        exit()


# GET TIER INSTANCE FROM GCP
def get_tier_instance_from_gcp(v_project_id, v_instance_name):
    # SET COMMAND GOOGLE CLOUD SQL
    get_instance_text = f"gcloud sql instances list --project {v_project_id} --filter='name:{v_instance_name}' --format='json(name,backendType,settings[tier],settings[dataDiskSizeGb])'"

    # EXECUTE COMMAND
    try:
        get_instance_command = shlex.split(get_instance_text)
        get_instance_output = subprocess.check_output(get_instance_command)
        get_instance_output = json.loads(get_instance_output)

        # CHECK DATA IS NOT EMPTY
        if len(get_instance_output) == 0:
            return None
        else:
            get_instance_output = [
                {
                    k1: v1
                    for k1, v1 in k.items()
                    if k1
                    in [
                        "name",
                        "backendType",
                        "settings",
                    ]
                }
                for k in get_instance_output
            ]
        # CREATE DATAFRAME
        df = pd.DataFrame(get_instance_output)

        # REMOVE EXTERNAL INSTANCE
        df = df[~df.backendType.isin(["EXTERNAL"])]

        log_format(
            "info",
            "[Instance Detail Module] - Successfully get all header instance from gcp",
        )
        # print(df)
    except Exception as e:
        log_format("error", f"[Instance Detail Module] - Error: {e}")
        exit()

    # TRANSFORM DATAFRAME TO DATABASE format
    try:
        dfclean = pd.DataFrame(df)
        df_tier = dfclean["settings"][0]["tier"]
        df_rdisk = dfclean["settings"][0]["dataDiskSizeGb"]
        cpu_memory = explode_instance_tier(df_tier)
        cpu_core = cpu_memory[0]
        memory_gb = cpu_memory[1]
        created_by = os.environ.get("DEFAULT_USERNAME")
        updated_by = os.environ.get("DEFAULT_USERNAME")

        # ASSIGN NEW COLUMN
        dfclean = dfclean.assign(
            cpu_core=cpu_core,
            memory_gb=memory_gb,
            tier=df_tier,
            reserved_disk_gb=df_rdisk,
            created_by=created_by,
            updated_by=updated_by,
        )

        # REMOVE COLUMN SETTINGS
        dfclean = dfclean.drop(columns=["settings", "backendType"])

        return dfclean

    except Exception as e:
        log_format("error", f"[Instance Detail Module] - Error: {e}")
        exit()


def upload_to_database(good_df):
    try:
        # setup connection database
        conn = auth_database()

        df1 = good_df
        # write dataframe to database
        df1.to_sql(name="ttdinstance", con=conn, if_exists="append", index=False)

        # close connection
        conn.close()
        log_format(
            "info", "[Instance Module] - Finish Writing Instance Detail to Database"
        )

    except Exception as e:
        log_format("error", f"[Instance Module] - Error: {e}")
        exit()
    return


def main_detail_instance():
    # LOAD ENV
    load_dotenv()

    # CHECK LOGIN GCP
    try:
        check_login()
    except Exception as e:
        log_format("error", f"[Instance Detail Module] - Error: {e}")
        exit()

    # GET ALL HEADER INSTANCE
    df_header = pd.DataFrame(get_all_header_instance())
    df_detail_tier = pd.DataFrame()

    # LOOP HEADER INSTANCE AND GET DETAIL INSTANCE
    try:
        for h_instance in range(int(len(df_header))):
            # print(df_header["project_id"][h_instance])
            df_detail_tier = pd.concat(
                [
                    df_detail_tier,
                    pd.DataFrame(
                        get_tier_instance_from_gcp(
                            df_header["project_id"][h_instance],
                            df_header["instance_name"][h_instance],
                        )
                    ),
                ],
                ignore_index=True,
            )

    except Exception as e:
        log_format("error", f"[Instance Detail Module] - Error: {e}")
        exit()

    # MERGE df_header & df_detail_tier and Clean DataFrame
    try:
        df_merge = df_detail_tier.merge(
            df_header, left_on=["name"], right_on=["instance_name"]
        )
        # RENAME COLUMN seq_id TO h_instance_id
        df_merge = df_merge.rename(columns={"seq_id": "h_instance_id"})

        # DROP COLUMN NOT USE
        df_final = df_merge.drop(
            columns=["tier", "name", "instance_name", "project_id"]
        )
        log_format(
            "info", "[Instance Detail Module] - Successfully Merge And Clean DataFrame"
        )
    except Exception as e:
        log_format("error", f"[Instance Detail Module] - Error: {e}")
        exit()

    # UPLOAD DATABASE
    try:
        upload_to_database(df_final)
        log_format(
            "info",
            "[Instance Detail Module] - Successfully Upload Instance Detail to Database",
        )
    except Exception as e:
        log_format("error", f"[Instance Detail Module] - Error: {e}")
        exit()


if __name__ == "__main__":
    main_detail_instance()
