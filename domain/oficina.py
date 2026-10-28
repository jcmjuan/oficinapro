"""Agregado que representa a oficina e suas configurações."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from .cliente import Cliente
from .exceptions import DuplicadoError, RegraNegocioError, ValidacaoError
from .mecanico import Mecanico
from .ordem_servico import OrdemServico
from .validators import decimal_valor, formatar_documento, formatar_telefone, normalizar_documento, texto_obrigatorio
from .veiculo import Veiculo


class Oficina:
    """Configuração e cadastros da oficina.

    A classe mantém a coleção em memória usada pelo modo demonstração e pela
    camada de aplicação. A persistência é responsabilidade dos repositórios.
    """

    def __init__(
        self,
        nome: str,
        cnpj: str,
        *,
        telefone: str | None = None,
        endereco: str | None = None,
        taxa_horaria_padrao: Decimal | int | float | str = Decimal("120.00"),
        comissao_padrao: Decimal | int | float | str = Decimal("0.10"),
    ) -> None:
        self._id: int | None = None
        self._nome = texto_obrigatorio(nome, "Nome da oficina", 2)
        self._documento = normalizar_documento(cnpj)
        self._telefone = (telefone or "").strip()
        self._endereco = (endereco or "").strip()
        self._taxa_horaria_padrao = decimal_valor(
            taxa_horaria_padrao, "Taxa horária padrão", minimo=Decimal("0")
        )
        self._comissao_padrao = decimal_valor(
            comissao_padrao,
            "Comissão padrão",
            minimo=Decimal("0"),
            maximo=Decimal("1"),
            casas="0.0001",
        )
        self._clientes: list[Cliente] = []
        self._mecanicos: list[Mecanico] = []
        self._veiculos: list[Veiculo] = []
        self._ordens: list[OrdemServico] = []

    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, valor: int | None) -> None:
        self._id = valor

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def cnpj(self) -> str:
        return formatar_documento(self._documento)

    @property
    def documento(self) -> str:
        return self._documento

    @property
    def telefone(self) -> str:
        return self._telefone

    @property
    def telefone_formatado(self) -> str:
        return formatar_telefone(self._telefone) if self._telefone else ""

    @property
    def endereco(self) -> str:
        return self._endereco

    @property
    def taxa_horaria_padrao(self) -> Decimal:
        return self._taxa_horaria_padrao

    @property
    def comissao_padrao(self) -> Decimal:
        return self._comissao_padrao

    @property
    def clientes(self) -> tuple[Cliente, ...]:
        return tuple(self._clientes)

    @property
    def mecanicos(self) -> tuple[Mecanico, ...]:
        return tuple(self._mecanicos)

    @property
    def veiculos(self) -> tuple[Veiculo, ...]:
        return tuple(self._veiculos)

    @property
    def ordens(self) -> tuple[OrdemServico, ...]:
        return tuple(self._ordens)

    def adicionar_cliente(self, cliente: Cliente) -> Cliente:
        if not isinstance(cliente, Cliente):
            raise ValidacaoError("Cliente inválido.")
        if any(c.documento == cliente.documento for c in self._clientes):
            raise DuplicadoError(f"Já existe cliente com o documento {cliente.cpf_cnpj}.")
        self._clientes.append(cliente)
        return cliente

    def adicionar_mecanico(self, mecanico: Mecanico) -> Mecanico:
        if not isinstance(mecanico, Mecanico):
            raise ValidacaoError("Mecânico inválido.")
        if any(m.registro == mecanico.registro for m in self._mecanicos):
            raise DuplicadoError(f"Já existe mecânico com o registro {mecanico.registro}.")
        self._mecanicos.append(mecanico)
        return mecanico

    def adicionar_veiculo(self, veiculo: Veiculo) -> Veiculo:
        if not isinstance(veiculo, Veiculo):
            raise ValidacaoError("Veículo inválido.")
        if any(v.placa_limpa == veiculo.placa_limpa for v in self._veiculos):
            raise DuplicadoError(f"Já existe veículo com a placa {veiculo.placa}.")
        if veiculo.cliente is not None and veiculo.cliente not in self._clientes:
            self.adicionar_cliente(veiculo.cliente)
        self._veiculos.append(veiculo)
        return veiculo

    def registrar_ordem(self, ordem: OrdemServico) -> OrdemServico:
        if not isinstance(ordem, OrdemServico):
            raise ValidacaoError("Ordem de serviço inválida.")
        if any(o.numero == ordem.numero for o in self._ordens):
            raise DuplicadoError(f"Já existe OS com o número {ordem.numero}.")
        self._ordens.append(ordem)
        return ordem

    def proximo_numero(self, ano: int | None = None) -> str:
        ano_ref = int(ano or datetime.now().year)
        sequencias = []
        for ordem in self._ordens:
            prefixo, _, sequencia = ordem.numero.partition("-")
            if prefixo == str(ano_ref) and sequencia.isdigit():
                sequencias.append(int(sequencia))
        proxima = max(sequencias, default=0) + 1
        return f"{ano_ref}-{proxima:04d}"

    def emitir_ordem_servico(
        self,
        cliente: Cliente,
        veiculo: Veiculo,
        mecanico: Mecanico,
        *,
        data_abertura: datetime | None = None,
        observacoes: str = "",
        criado_por: str = "",
    ) -> OrdemServico:
        if cliente not in self._clientes:
            self.adicionar_cliente(cliente)
        if mecanico not in self._mecanicos:
            self.adicionar_mecanico(mecanico)
        if veiculo not in self._veiculos:
            self.adicionar_veiculo(veiculo)
        if veiculo.cliente is not cliente:
            raise RegraNegocioError("O veículo não pertence ao cliente informado.")
        numero = self.proximo_numero((data_abertura or datetime.now()).year)
        ordem = OrdemServico(
            numero,
            cliente,
            veiculo,
            mecanico,
            data_abertura=data_abertura,
            observacoes=observacoes,
            criado_por=criado_por,
        )
        self._ordens.append(ordem)
        return ordem

    def __repr__(self) -> str:
        return f"Oficina(id={self.id!r}, nome={self.nome!r}, cnpj={self.cnpj!r})"
