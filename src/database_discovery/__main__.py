from logging import log
from database_discovery.v1.log import log_format
from database_discovery.v1.scrap_service.project_service.project import (
    compare_project_list,
)
from database_discovery.v1.scrap_service.instance_service.instance import (
    main_instance_list,
)
from database_discovery.v1.scrap_service.instance_service.instance_detail import (
    main_detail_instance,
)

# # scrap database service
# # daily 18:05
# # note = for moudule get user database and get table detail, scheduller on crontab root, check crontab -l
# from database_discovery.v1.scrap_service.database_service.database_prod.database_PROD import main as main_database_PROD
# from database_discovery.v1.scrap_service.database_service.database_prod.database_detail_PROD import main as main_database_detail_PROD
# from database_discovery.v1.scrap_service.database_service.database_prod.table_header_PROD import main as main_table_header_PROD
# 



try:
    log_format("info", "[Main] - Start Scrap Project")
    compare_project_list()
    log_format("info", "[Main] - Finish Scrap Project")
except Exception as e:
    log_format("error", f"[Main] - Error Scrap Project{e}")
try:
    log_format("info", "[Main] - Start Scrap Instance")
    main_instance_list()
    log_format("info", "[Main] - Finish Scrap Instance")
except Exception as e:
    log_format("error", f"[Main] - Error Scrap Instance{e}")

try:
    log_format("info", "[Main] - Start Scrap Instance Detail")
    main_detail_instance()
    log_format("info", "[Main] - Finish Scrap Instance Detail")
except Exception as e:
    log_format("error", f"[Main] - Error Scrap Instance Detail{e}")

# 
# # scrap database service
# #get database_PROD
# try:
#     log_format("info", "[Main] - Start Scrap Project")
#     main_database_PROD()
#     log_format("info", "[Main] - Finish Scrap Project")
# except Exception as e:
#     log_format("error", f"[Main] - Error Scrap Project{e}")
# #get database_detail_PROD
# try:
#     log_format("info", "[Main] - Start Scrap Project")
#     main_database_detail_PROD()
#     log_format("info", "[Main] - Finish Scrap Project")
# except Exception as e:
#     log_format("error", f"[Main] - Error Scrap Project{e}")
# #get table_header_PROD
# try:
#     log_format("info", "[Main] - Start Scrap Project")
#     main_table_header_PROD()
#     log_format("info", "[Main] - Finish Scrap Project")
# except Exception as e:
#     log_format("error", f"[Main] - Error Scrap Project{e}")
# 

