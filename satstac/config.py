import os

STAC_VERSION = os.getenv('STAC_VERSION', '1.0.0-beta.1')

STAC_PATH_TEMPLATE = os.getenv('STAC_PATH_TEMPLATE', '${collection}/${id}')
