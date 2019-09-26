from typing import Callable
from invoke import Program, Collection
from pms import __version__, tasks

cli = Program(namespace=Collection.from_module(tasks), version=__version__)
