"""
Classe Base para Adaptadores de Coleta de Vagas
"""
from abc import ABC, abstractmethod
from typing import List
from ..core.schemas import JobOfferBase


class BaseJobAdapter(ABC):
    platform_name: str = "base"

    @abstractmethod
    def search(self, search_term: str, location: str = "Brasil", limit: int = 15) -> List[JobOfferBase]:
        """
        Executa a varredura na plataforma e devolve uma lista de vagas padronizadas.
        """
        pass
