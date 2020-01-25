import os

STAC_VERSION = os.getenv('STAC_VERSION', '0.9.0')

STAC_PATH_TEMPLATE = os.getenv('STAC_PATH_TEMPLATE', '${collection}/${id}')
