from vtutils.confparser import env_config
from vtutils.misc import get_project_root
from vtutils.vtlogger import initLog, getLog
import sys
import os

ROOT_DIR = get_project_root()
sys.path.append(ROOT_DIR)

package_name = "gruezi_api"
vtlog = initLog(package_name)

config = env_config("{0}/.env".format(ROOT_DIR))

# storage will be initialized when MongoDB is configured
# for now we don't need it
vtstorage = None

# when mongo is ready:
# from vtutils.confparser import parse_config
# configuration = parse_config("api.ini", config)
# from vtstorage.perm_storage import VTPermStorage
# vtstorage = VTPermStorage(
#     configuration["env_config"]["PERMANENT_STORAGE"],
#     configuration["mongodb"],
#     params={"database": configuration["env_config"]["PERMANENT_DB"]}
# )
