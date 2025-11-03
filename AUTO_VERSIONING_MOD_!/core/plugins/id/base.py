"""
base.py
=======

Abstract base class for ID module plugins. Plugins provide a
consistent interface to perform actions on ID Cards, the ledger
and the registry. Implementations must override the :meth:`run`
method to perform their specific behaviour.

Plugins may be executed in a CLI context (see ``scripts/id_cli.py``)
or as part of CI workflows. They should avoid side effects during
initialisation and perform all I/O within :meth:`run`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class IDPlugin(ABC):
    """Abstract base class for ID plugins."""

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the plugin.

        Concrete plugins must implement this method. It should accept
        positional and keyword arguments relevant to the plugin's
        function and return a result object or raise an exception on
        failure.
        """
        raise NotImplementedError
