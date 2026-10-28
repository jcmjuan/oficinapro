"""Container de dependências da interface."""

from __future__ import annotations

from pathlib import Path

from application.configuracao_service import ConfiguracaoService
from application.orcamento_service import OrcamentoService
from application.ordem_servico_service import OrdemServicoService
from application.relatorio_service import RelatorioService
from infrastructure.database import Database
from infrastructure.repositories.cliente_repository import ClienteRepository
from infrastructure.repositories.configuracao_repository import ConfiguracaoRepository
from infrastructure.repositories.mecanico_repository import MecanicoRepository
from infrastructure.repositories.oficina_repository import OficinaRepository
from infrastructure.repositories.ordem_servico_repository import OrdemServicoRepository
from infrastructure.repositories.veiculo_repository import VeiculoRepository
from infrastructure.seed import seed_demo


class AppContext:
    """Instancia banco, repositórios e serviços uma única vez."""

    def __init__(self, db_path: str | Path = "oficinapro.db") -> None:
        self.db_path = Path(db_path)
        self.db = Database(self.db_path)
        seed_demo(self.db)

        self.clientes = ClienteRepository(self.db)
        self.mecanicos = MecanicoRepository(self.db)
        self.veiculos = VeiculoRepository(self.db)
        self.ordens = OrdemServicoRepository(self.db)
        self.oficinas = OficinaRepository(self.db)
        self.configuracoes = ConfiguracaoRepository(self.db)

        self.ordem_service = OrdemServicoService(
            self.clientes,
            self.veiculos,
            self.mecanicos,
            self.ordens,
            self.oficinas,
        )
        self.orcamento_service = OrcamentoService(self.ordens, self.oficinas)
        self.relatorio_service = RelatorioService(self.ordens)
        self.configuracao_service = ConfiguracaoService(
            self.configuracoes,
            self.oficinas,
            self.db,
        )

    def fechar(self) -> None:
        self.db.fechar()

    def recarregar(self) -> None:
        self.db.reabrir()

    def resumo(self) -> dict:
        return {
            "clientes": self.clientes.contar(),
            "mecanicos": self.mecanicos.contar(),
            "veiculos": self.veiculos.contar(),
            "ordens": self.ordens.contar(),
        }
