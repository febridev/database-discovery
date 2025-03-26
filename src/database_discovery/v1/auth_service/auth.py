import os
import json
import subprocess
import shlex
import logging
import sqlalchemy
from sqlalchemy.exc import InterfaceError, OperationalError, ProgrammingError
from database_discovery.v1.log import log_format
from dotenv import load_dotenv


# set connection to database open and close
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


# setup and check authentication to GCP
def check_login():
    # LOAD ENV FILE
    load_dotenv()
    sa_email = os.environ.get("SERVICE_ACCOUNT_MAIL")
    sa_path = os.environ.get("SERVICE_ACCOUNT_PATH")
    sa_account = os.environ.get("SERVICE_ACCOUNT_NAME")
    auth_command_gcp = ""
    if sa_path != "":
        auth_command_gcp = (
            f"gcloud auth list --filter-account='{sa_account}' --format json"
        )
        auth_command_gcp = shlex.split(auth_command_gcp)
        auth_output_gcp = subprocess.run(auth_command_gcp, capture_output=True)
        auth_output_gcp = json.loads(auth_output_gcp.stdout)
    else:
        auth_command_gcp = "gcloud auth list --format json"
        auth_command_gcp = shlex.split(auth_command_gcp)
        auth_output_gcp = subprocess.run(auth_command_gcp, capture_output=True)
        auth_output_gcp = json.loads(auth_output_gcp.stdout)
    auth_output_email = auth_output_gcp[0]["account"]
    if (sa_email in auth_output_email) or (sa_path in auth_output_email):
        message = "Authentication successful"
        log_format("info", f"[Auth GCP Module] - {message}")
    else:
        message = "Authentication failed"
        log_format("error", f"[Auth GCP Module] - {message}")
        if sa_path != "":
            log_format("info", "Set Service Account")
            auth_command_gcp = (
                f"gcloud auth activate-service-account --key-file='{sa_path}'"
            )
            auth_command_gcp = shlex.split(auth_command_gcp)
            auth_output_gcp = subprocess.run(auth_command_gcp, capture_output=True)
            message = "Set Service Account"
        else:
            message = "Service Account Not Available"
            log_format("error", f"[Auth GCP Module] - {message}")

    return message


if __name__ == "__main__":
    check_login()
