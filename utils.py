import logging
def init_loging_config():
    level = logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    _logger = logging.getLogger("qd_98")
    _logger.setLevel(level)
    return _logger


logger = init_loging_config()
