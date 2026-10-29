"""Ordem de serviço: agregado raiz do atendimento."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Iterable

from .cliente import Cliente
from .exceptions import RegraNegocioError, TransicaoInvalida, ValidacaoError
from .item_os import ItemOS
from .mao_de_obra import MaoDeObra
from .mecanico import Mecanico
from .peca import Peca
from .status_historico import StatusHistorico
from .status_os import StatusOS
from .tipo_item import TipoItem
from .validators import (
    decimal_valor,
    formatar_brl,
    normalizar_numero_os,
    parse_datetime,
    texto_obrigatorio,
)
from .veiculo import Veiculo

_ZERO = Decimal("0.00")
_CENTAVOS = Decimal("0.01")

_TRANSICOES = {
    StatusOS.ORCAMENTO: {StatusOS.APROVADA, StatusOS.CANCELADA},
    StatusOS.APROVADA: {StatusOS.EM_EXECUCAO, StatusOS.CANCELADA},
    StatusOS.EM_EXECUCAO: {StatusOS.FINALIZADA, StatusOS.CANCELADA},
    StatusOS.FINALIZADA: set(),
    StatusOS.CANCELADA: set(),
}


class OrdemServico:
    def __init__(
        self,
        numero: str,
        cliente: Cliente,
        veiculo: Veiculo,
        mecanico: Mecanico,
        *,
        status: StatusOS | str = StatusOS.ORCAMENTO,
        desconto: Decimal | int | float | str = _ZERO,
        data_abertura: datetime | str | None = None,
        data_aprovacao: datetime | str | None = None,
        data_inicio: datetime | str | None = None,
        data_finalizacao: datetime | str | None = None,
        data_cancelamento: datetime | str | None = None,
        motivo_cancelamento: str | None = None,
        observacoes: str = "",
        criado_por: str = "",
        itens: Iterable[ItemOS] | None = None,
        historico: Iterable[StatusHistorico] | None = None,
        id: int | None = None,
    ) -> None:
        if not isinstance(cliente, Cliente):
            raise ValidacaoError("Cliente inválido para a OS.")
        if not isinstance(veiculo, Veiculo):
            raise ValidacaoError("Veículo inválido para a OS.")
        if not isinstance(mecanico, Mecanico):
            raise ValidacaoError("Mecânico inválido para a OS.")
        if veiculo.cliente is not None and veiculo.cliente is not cliente:
            raise RegraNegocioError("O veículo não pertence ao cliente informado.")

        self._id = id
        self._numero = normalizar_numero_os(numero)
        self._cliente = cliente
        self._veiculo = veiculo
        self._mecanico = mecanico
        self._status = StatusOS.from_value(status)
        self._desconto = decimal_valor(
            desconto, "Desconto", minimo=_ZERO, casas="0.01"
        )
        self._data_abertura = parse_datetime(data_abertura) or datetime.now()
        self._data_aprovacao = parse_datetime(data_aprovacao)
        self._data_inicio = parse_datetime(data_inicio)
        self._data_finalizacao = parse_datetime(data_finalizacao)
        self._data_cancelamento = parse_datetime(data_cancelamento)
        self._motivo_cancelamento = (
            motivo_cancelamento.strip() if motivo_cancelamento else None
        )
        self._observacoes = (observacoes or "").strip()
        self._criado_por = (criado_por or "").strip()
        self._itens: list[ItemOS] = list(itens or [])
        for item in self._itens:
            if not isinstance(item, ItemOS):
                raise ValidacaoError("Todos os itens devem herdar de ItemOS.")
        self.__subtotal = _ZERO
        self.__total = _ZERO
        self.__recalcular_total()
        self._historico: list[StatusHistorico] = list(historico or [])
        if not self._historico:
            self._historico.append(
                StatusHistorico(
                    status_anterior=None,
                    status_novo=self._status,
                    data_hora=self._data_abertura,
                    usuario=self._criado_por,
                    motivo="Abertura da OS",
                )
            )
        self.__validar_datas()

    def __validar_datas(self) -> None:
        if self._status is not StatusOS.FINALIZADA and self._data_finalizacao is not None:
            raise RegraNegocioError(
                "data_finalizacao só pode existir em uma OS FINALIZADA."
            )
        if self._status is not StatusOS.CANCELADA and self._data_cancelamento is not None:
            raise RegraNegocioError(
                "data_cancelamento só pode existir em uma OS CANCELADA."
            )
        if self._status is StatusOS.FINALIZADA and self._data_finalizacao is None:
            raise RegraNegocioError("OS FINALIZADA exige data_finalizacao.")
        if self._status is StatusOS.CANCELADA and self._data_cancelamento is None:
            raise RegraNegocioError("OS CANCELADA exige data_cancelamento.")

    def __recalcular_total(self) -> None:
        subtotal = sum((item.calcular_subtotal() for item in self._itens), _ZERO)
        subtotal = subtotal.quantize(_CENTAVOS)
        if self._desconto > subtotal:
            raise RegraNegocioError("Desconto não pode ser maior que o subtotal.")
        self.__subtotal = subtotal
        self.__total = (subtotal - self._desconto).quantize(_CENTAVOS)

    def __validar_transicao(self, novo: StatusOS) -> None:
        novo = StatusOS.from_value(novo)
        if novo not in _TRANSICOES[self._status]:
            raise TransicaoInvalida(
                f"OS {self._numero}: {self._status.rotulo} não pode ir para "
                f"{novo.rotulo}."
            )

    def __registrar_historico(
        self,
        novo: StatusOS,
        data_hora: datetime,
        usuario: str,
        motivo: str,
    ) -> None:
        self._historico.append(
            StatusHistorico(
                status_anterior=self._status,
                status_novo=novo,
                data_hora=data_hora,
                usuario=(usuario or "").strip(),
                motivo=motivo,
            )
        )

    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, valor: int | None) -> None:
        self._id = valor

    @property
    def numero(self) -> str:
        return self._numero

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def veiculo(self) -> Veiculo:
        return self._veiculo

    @property
    def mecanico(self) -> Mecanico:
        return self._mecanico

    @property
    def status(self) -> StatusOS:
        return self._status

    @property
    def desconto(self) -> Decimal:
        return self._desconto

    @property
    def data_abertura(self) -> datetime:
        return self._data_abertura

    @property
    def data_aprovacao(self) -> datetime | None:
        return self._data_aprovacao

    @property
    def data_inicio(self) -> datetime | None:
        return self._data_inicio

    @property
    def data_finalizacao(self) -> datetime | None:
        return self._data_finalizacao

    @property
    def data_cancelamento(self) -> datetime | None:
        return self._data_cancelamento

    @property
    def motivo_cancelamento(self) -> str | None:
        return self._motivo_cancelamento

    @property
    def observacoes(self) -> str:
        return self._observacoes

    @property
    def criado_por(self) -> str:
        return self._criado_por

    @property
    def itens(self) -> tuple[ItemOS, ...]:
        return tuple(self._itens)

    @property
    def historico(self) -> tuple[StatusHistorico, ...]:
        return tuple(self._historico)

    @property
    def status_historico(self) -> tuple[StatusHistorico, ...]:
        return self.historico

    @property
    def subtotal(self) -> Decimal:
        return self.__subtotal

    @property
    def total(self) -> Decimal:
        return self.__total

    @property
    def quantidade_itens(self) -> int:
        return len(self._itens)

    @property
    def subtotal_pecas(self) -> Decimal:
        return sum(
            (
                item.calcular_subtotal()
                for item in self._itens
                if item.tipo() is TipoItem.PECA
            ),
            _ZERO,
        ).quantize(_CENTAVOS)

    @property
    def subtotal_mao_obra(self) -> Decimal:
        return sum(
            (
                item.calcular_subtotal()
                for item in self._itens
                if item.tipo() is TipoItem.MAO_DE_OBRA
            ),
            _ZERO,
        ).quantize(_CENTAVOS)

    def adicionar_item(self, item: ItemOS) -> None:
        if self._status is not StatusOS.ORCAMENTO:
            raise RegraNegocioError(
                "Itens só podem ser alterados enquanto a OS está em ORCAMENTO."
            )
        if not isinstance(item, ItemOS):
            raise ValidacaoError("Item inválido.")
        self._itens.append(item)
        self.__recalcular_total()

    def remover_item(self, item_ou_indice: ItemOS | int) -> ItemOS:
        if self._status is not StatusOS.ORCAMENTO:
            raise RegraNegocioError(
                "Itens só podem ser alterados enquanto a OS está em ORCAMENTO."
            )
        if isinstance(item_ou_indice, int):
            try:
                item = self._itens.pop(item_ou_indice)
            except IndexError as exc:
                raise ValidacaoError("Índice de item inválido.") from exc
        else:
            if item_ou_indice not in self._itens:
                raise ValidacaoError("Item não pertence a esta OS.")
            self._itens.remove(item_ou_indice)
            item = item_ou_indice
        self.__recalcular_total()
        return item

    def aplicar_desconto(self, desconto: Decimal | int | float | str) -> None:
        if self._status is not StatusOS.ORCAMENTO:
            raise RegraNegocioError("Desconto só pode ser aplicado em ORCAMENTO.")
        valor = decimal_valor(desconto, "Desconto", minimo=_ZERO, casas="0.01")
        if valor > self.__subtotal:
            raise RegraNegocioError("Desconto não pode ser maior que o subtotal.")
        self._desconto = valor
        self.__recalcular_total()

    def aprovar(self, usuario: str = "", *, data_hora: datetime | str | None = None) -> None:
        if not self._itens:
            raise RegraNegocioError("A OS precisa ter pelo menos um item para ser aprovada.")
        if self.__total <= _ZERO:
            raise RegraNegocioError("A OS precisa ter total maior que zero para ser aprovada.")
        self.__validar_transicao(StatusOS.APROVADA)
        agora = parse_datetime(data_hora) or datetime.now()
        self.__registrar_historico(StatusOS.APROVADA, agora, usuario, "Orçamento aprovado")
        self._status = StatusOS.APROVADA
        self._data_aprovacao = agora

    def iniciar(self, usuario: str = "", *, data_hora: datetime | str | None = None) -> None:
        if self._mecanico is None:
            raise RegraNegocioError("A OS precisa de um mecânico responsável.")
        self.__validar_transicao(StatusOS.EM_EXECUCAO)
        agora = parse_datetime(data_hora) or datetime.now()
        self.__registrar_historico(StatusOS.EM_EXECUCAO, agora, usuario, "Execução iniciada")
        self._status = StatusOS.EM_EXECUCAO
        self._data_inicio = agora

    def finalizar(
        self,
        km_saida: int | None = None,
        usuario: str = "",
        *,
        data_hora: datetime | str | None = None,
    ) -> None:
        if not self._itens:
            raise RegraNegocioError("A OS precisa ter itens para ser finalizada.")
        self.__validar_transicao(StatusOS.FINALIZADA)
        if km_saida is not None:
            self._veiculo.atualizar_km(km_saida)
        agora = parse_datetime(data_hora) or datetime.now()
        self.__registrar_historico(StatusOS.FINALIZADA, agora, usuario, "Serviço finalizado")
        self._status = StatusOS.FINALIZADA
        self._data_finalizacao = agora

    def cancelar(
        self,
        motivo: str,
        usuario: str = "",
        *,
        data_hora: datetime | str | None = None,
    ) -> None:
        motivo_limpo = texto_obrigatorio(motivo, "Motivo do cancelamento", 3)
        self.__validar_transicao(StatusOS.CANCELADA)
        agora = parse_datetime(data_hora) or datetime.now()
        self.__registrar_historico(StatusOS.CANCELADA, agora, usuario, motivo_limpo)
        self._status = StatusOS.CANCELADA
        self._data_cancelamento = agora
        self._motivo_cancelamento = motivo_limpo

    def atualizar_observacoes(self, observacoes: str) -> None:
        self._observacoes = (observacoes or "").strip()

    def resumo(self) -> str:
        return (
            f"OS {self._numero} • {self._cliente.nome} • "
            f"{self._veiculo.marca} {self._veiculo.modelo} {self._veiculo.placa}\n"
            f"Itens: {self.quantidade_itens} • Subtotal: {formatar_brl(self.subtotal)} • "
            f"Total: {formatar_brl(self.total)} • Status: {self._status.value}"
        )

    def __repr__(self) -> str:
        return (
            f"OrdemServico(id={self.id!r}, numero={self.numero!r}, "
            f"status={self.status.value!r}, total={self.total!r})"
        )
