import HTTP_database.src.config as config
import HTTP_database.src.service as service


# singleton config

def get_config():
    if not hasattr(get_config, "config"):
        get_config.config = config.Config()
    return get_config.config


# singleton service

def get_service():
    if not hasattr(get_service, "service"):
        get_service.service = service.CollectionService(get_config().BASE_DIRECTORY)
    return get_service.service
