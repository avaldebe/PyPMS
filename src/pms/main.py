"""
Load extra cli commands from plugins from plugins (entry points) advertized as `"pypms.extras"`
"""

import sys

if sys.version_info >= (3, 10):
    from importlib import metadata
else:
    import importlib_metadata as metadata

from loguru import logger

from .cli import main

ep: metadata.EntryPoint
for ep in metadata.entry_points(group="pypms.extras"):
    try:
        main.command(name=ep.name)(ep.load())
    except ModuleNotFoundError as e:  # pragma: no cover
        logger.enable("pms")
        logger.error(f"loading CLI plugin {ep.name} from {ep.pattern} raised {e}")
