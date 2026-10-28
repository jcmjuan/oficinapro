"""Serviços de aplicação para ordens de serviço."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from domain.exceptions import RegraNegocioError
from domain.mao_de_obra import MaoDeObra
from domain.ordem_servico import OrdemServico
from domain.peca import Peca
from domain.status_os import StatusOS
from domain.validators import decimal_valor, parse_datetime

from infrastructure.repositories.cliente_repository import ClienteRepository
from infrastructure.repositories.mecanico_repository import MecanicoRepository
from infrastructure.repositories.oficina_repository import OficinaRepository
from infrastructure.repositories.ordem_servico_repository import OrdemServicoRepository
from infrastructure.repositories.veiculo_repository import VeiculoRepository


class OrdemServicoService:
    def __init__(
        self,
        cliente_repo: ClienteRepository,
        veiculo_repo: VeiculoRepository,
        mecanico_repo: MecanicoRepository,
        os_repo: OrdemServicoRepository,
        oficina_repo: OficinaRepository,
    ) -> None:
        self.clientes = cliente_repo
        self.veiculos = veiculo_repo
        self.mecanicos = mecanico_repo
        self.ordens = os_repo
        self.oficina_repo = oficina_repo

    def criar_ordem(
        self,
        cliente_id: int,
        veiculo_id: int,
        mecanico_id: int,
        *,
        observacoes: str = "",
        data_abertura: datetime | str | None = None,
        criado_por: str = "",
    ) -> OrdemServico:
        cliente = self.clientes.buscar_por_id(cliente_id)
        veiculo = self.veiculos.buscar_por_id(veiculo_id)
        if veiculo.cliente is None or veiculo.cliente.id != cliente.id:
            raise RegraNegocioError("O veículo selecionado não pertence ao cliente.")
        veiculo.vincular_cliente(cliente)
        mecanico = self.mecanicos.buscar_por_id(mecanico_id)
        abertura = parse_datetime(data_abertura) or datetime.now()
        numero = self.ordens.proximo_numero(abertura.year)
        ordem = OrdemServico(
            numero,
            cliente,
            veiculo,
            mecanico,
            data_abertura=abertura,
            observacoes=observacoes,
            criado_por=criado_por,
        )
        return self.ordens.salvar(ordem)

    def obter(self, numero: str) -> OrdemServico:
        return self.ordens.obter(numero)

    def listar(self, **filtros) -> list[OrdemServico]:
        return self.ordens.listar(**filtros)

    def adicionar_peca(
        self,
        numero: str,
        descricao: str,
        quantidade,
        valor_unitario,
        *,
        codigo: str | None = None,
        fornecedor: str | None = None,
    ) -> OrdemServico:
        ordem = self.ordens.obter(numero)
        ordem.adicionar_item(
            Peca(descricao, quantidade, valor_unitario, codigo=codigo, fornecedor=fornecedor)
        )
        return self.ordens.salvar(ordem)

    def adicionar_mao_de_obra(
        self,
        numero: str,
        descricao: str,
        horas,
        taxa_horaria=None,
        *,
        mecanico_id: int | None = None,
    ) -> OrdemServico:
        ordem = self.ordens.obter(numero)
        if taxa_horaria is None:
            taxa_horaria = self.oficina_repo.obter().taxa_horaria_padrao
        taxa = decimal_valor(taxa_horaria, "Taxa horária", minimo=Decimal("0"))
        if mecanico_id is None:
            mecanico = ordem.mecanico
        else:
            mecanico = self.mecanicos.buscar_por_id(mecanico_id)
        ordem.adicionar_item(MaoDeObra(descricao, horas, taxa, mecanico))
        return self.ordens.salvar(ordem)

    def remover_item(self, numero: str, indice: int) -> OrdemServico:
        ordem = self.ordens.obter(numero)
        ordem.remover_item(indice)
        return self.ordens.salvar(ordem)

    def aplicar_desconto(self, numero: str, desconto) -> OrdemServico:
        ordem = self.ordens.obter(numero)
        ordem.aplicar_desconto(desconto)
        return self.ordens.salvar(ordem)

    def aprovar(self, numero: str, usuario: str = "") -> OrdemServico:
        ordem = self.ordens.obter(numero)
        ordem.aprovar(usuario)
        return self.ordens.salvar(ordem)

    def iniciar(self, numero: str, usuario: str = "") -> OrdemServico:
        ordem = self.ordens.obter(numero)
        ordem.iniciar(usuario)
        return self.ordens.salvar(ordem)

    def finalizar(
        self,
        numero: str,
        *,
        km_saida: int | None = None,
        usuario: str = "",
    ) -> OrdemServico:
        ordem = self.ordens.obter(numero)
        ordem.finalizar(km_saida, usuario)
        self.veiculos.salvar(ordem.veiculo)
        return self.ordens.salvar(ordem)

    def cancelar(self, numero: str, motivo: str, usuario: str = "") -> OrdemServico:
        ordem = self.ordens.obter(numero)
        ordem.cancelar(motivo, usuario)
        return self.ordens.salvar(ordem)

    def atualizar_observacoes(self, numero: str, observacoes: str) -> OrdemServico:
        ordem = self.ordens.obter(numero)
        ordem.atualizar_observacoes(observacoes)
        return self.ordens.salvar(ordem)

    def resumo_dashboard(self) -> dict:
        oficina = self.oficina_repo.obter()
        contagem = self.ordens.contar_por_status()
        return {
            "oficina": oficina,
            "contagem": contagem,
            "abertas": (
                contagem.get(StatusOS.ORCAMENTO.value, 0)
                + contagem.get(StatusOS.APROVADA.value, 0)
                + contagem.get(StatusOS.EM_EXECUCAO.value, 0)
            ),
            "total_os": sum(contagem.values()),
        }
