"""Carga de dados fictícios usada na demonstração e nos testes."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from domain.cliente import Cliente
from domain.mao_de_obra import MaoDeObra
from domain.mecanico import Mecanico
from domain.oficina import Oficina
from domain.ordem_servico import OrdemServico
from domain.peca import Peca
from domain.veiculo import Veiculo

from .database import Database
from .repositories.cliente_repository import ClienteRepository
from .repositories.configuracao_repository import ConfiguracaoRepository
from .repositories.mecanico_repository import MecanicoRepository
from .repositories.oficina_repository import OficinaRepository
from .repositories.ordem_servico_repository import OrdemServicoRepository
from .repositories.veiculo_repository import VeiculoRepository


def _criar_os(
    numero: str,
    cliente: Cliente,
    veiculo: Veiculo,
    mecanico: Mecanico,
    data_abertura: datetime,
) -> OrdemServico:
    return OrdemServico(
        numero,
        cliente,
        veiculo,
        mecanico,
        data_abertura=data_abertura,
        criado_por="seed",
    )


def _finalizar_os(
    ordem: OrdemServico,
    veiculo_repo: VeiculoRepository,
) -> None:
    abertura = ordem.data_abertura
    ordem.aprovar("seed", data_hora=abertura + timedelta(hours=2))
    ordem.iniciar("seed", data_hora=abertura + timedelta(hours=3))
    ordem.finalizar(
        ordem.veiculo.km + 100,
        "seed",
        data_hora=abertura + timedelta(days=1),
    )
    veiculo_repo.salvar(ordem.veiculo)


def seed_demo(db: Database, *, forcar: bool = False) -> dict[str, int]:
    """Cria a base demonstrativa do OficinaPro.

    A carga reproduz os totais da Etapa 2: R$ 18.450,00 de faturamento,
    R$ 6.320,00 de mão de obra, R$ 12.130,00 de peças e R$ 743,00 de comissões.
    """
    cliente_repo = ClienteRepository(db)
    mecanico_repo = MecanicoRepository(db)
    veiculo_repo = VeiculoRepository(db)
    os_repo = OrdemServicoRepository(db)
    oficina_repo = OficinaRepository(db)
    config_repo = ConfiguracaoRepository(db)

    if os_repo.contar() > 0 and not forcar:
        return {
            "clientes": cliente_repo.contar(),
            "mecanicos": mecanico_repo.contar(),
            "veiculos": veiculo_repo.contar(),
            "ordens": os_repo.contar(),
        }

    if forcar:
        with db.transacao() as conn:
            for tabela in (
                "status_historico",
                "item_os",
                "ordem_servico",
                "veiculo",
                "cliente",
                "mecanico",
                "oficina",
                "configuracao",
                "comissao_pagamento",
            ):
                conn.execute(f"DELETE FROM {tabela}")

    oficina = Oficina(
        "DevSolo Studio",
        "12.345.678/0001-90",
        telefone="(11) 98765-4321",
        endereco="Av. das Oficinas, 120 — Vila Industrial, São Paulo/SP",
        taxa_horaria_padrao=Decimal("120.00"),
        comissao_padrao=Decimal("0.10"),
    )
    oficina_repo.salvar(oficina)
    for chave, valor in {
        "oficina.nome": oficina.nome,
        "oficina.cnpj": oficina.cnpj,
        "oficina.telefone": oficina.telefone,
        "oficina.endereco": oficina.endereco,
        "oficina.taxa_horaria_padrao": str(oficina.taxa_horaria_padrao),
        "oficina.comissao_padrao": str(oficina.comissao_padrao),
    }.items():
        config_repo.definir(chave, valor)

    ana = cliente_repo.salvar(
        Cliente(
            "Ana Paula Ribeiro",
            "(11) 98765-4321",
            "123.456.789-00",
            email="ana.ribeiro@email.com",
            endereco="Rua das Acácias, 120 — Jardim Primavera, São Paulo/SP",
            data_nascimento="1990-05-14",
        )
    )
    carlos = cliente_repo.salvar(
        Cliente(
            "Carlos Eduardo Lima",
            "(11) 97654-3210",
            "234.567.890-11",
            email="carlos.lima@email.com",
            endereco="Av. Paulista, 900 — Bela Vista, São Paulo/SP",
            data_nascimento="1985-09-22",
        )
    )
    fernanda = cliente_repo.salvar(
        Cliente(
            "Fernanda Souza",
            "(11) 96543-2109",
            "345.678.901-22",
            email="fernanda.souza@email.com",
            endereco="Rua Harmonia, 45 — Vila Madalena, São Paulo/SP",
            data_nascimento="1992-02-08",
        )
    )
    joao = cliente_repo.salvar(
        Cliente(
            "João Batista",
            "(11) 95432-1098",
            "456.789.012-33",
            email="joao.batista@email.com",
            endereco="Rua do Bosque, 78 — Barra Funda, São Paulo/SP",
            data_nascimento="1978-11-30",
        )
    )
    mariana = cliente_repo.salvar(
        Cliente(
            "Mariana Alves",
            "(11) 94321-0987",
            "567.890.123-44",
            email="mariana.alves@email.com",
            endereco="Al. Santos, 300 — Cerqueira César, São Paulo/SP",
            data_nascimento="1995-07-19",
        )
    )
    roberto = cliente_repo.salvar(
        Cliente(
            "Roberto Nunes",
            "(11) 93210-9876",
            "678.901.234-55",
            email="roberto.nunes@email.com",
            endereco="Rua Vergueiro, 1500 — Liberdade, São Paulo/SP",
            data_nascimento="1982-03-11",
        )
    )

    marcos = mecanico_repo.salvar(
        Mecanico(
            "Marcos Silva",
            "(11) 98888-7777",
            "MEC-001",
            Decimal("0.12"),
            email="marcos.silva@devsolo.studio",
            especialidade="Motor e injeção",
        )
    )
    rafael = mecanico_repo.salvar(
        Mecanico(
            "Rafael Costa",
            "(11) 97777-6666",
            "MEC-002",
            Decimal("0.10"),
            email="rafael.costa@devsolo.studio",
            especialidade="Suspensão e freios",
        )
    )
    diego = mecanico_repo.salvar(
        Mecanico(
            "Diego Almeida",
            "(11) 96666-5555",
            "MEC-003",
            Decimal("0.15"),
            email="diego.almeida@devsolo.studio",
            especialidade="Elétrica e diagnóstico",
        )
    )

    civic = veiculo_repo.salvar(
        Veiculo("ABC-1D23", "Honda", "Civic", 2019, 62480, ana, cor="Prata", combustivel="Flex")
    )
    gol = veiculo_repo.salvar(
        Veiculo("XYZ-9K87", "Volkswagen", "Gol", 2015, 118920, carlos, cor="Branco", combustivel="Flex")
    )
    argo = veiculo_repo.salvar(
        Veiculo("QWE-2A34", "Fiat", "Argo", 2021, 34210, fernanda, cor="Vermelho", combustivel="Flex")
    )
    corolla = veiculo_repo.salvar(
        Veiculo("JKL-5M67", "Toyota", "Corolla", 2018, 78950, joao, cor="Preto", combustivel="Flex")
    )
    onix = veiculo_repo.salvar(
        Veiculo("MNO-8P90", "Chevrolet", "Onix", 2020, 45730, mariana, cor="Azul", combustivel="Flex")
    )
    ka = veiculo_repo.salvar(
        Veiculo("RST-3V45", "Ford", "Ka", 2016, 96540, roberto, cor="Cinza", combustivel="Flex")
    )

    # OS 2026-0042 — orçamento em aberto, total R$ 1.240,00.
    os_0042 = _criar_os("2026-0042", ana, civic, marcos, datetime(2026, 10, 24, 9, 30))
    for item in (
        Peca("Filtro de óleo", 1, 45, "FLT-001", "Auto Peças Central"),
        Peca("Óleo de motor 5W30", 1, 180, "OLE-5W30", "Lubrificantes Silva"),
        MaoDeObra("Troca de óleo e filtros", Decimal("1.50"), 120, marcos),
        MaoDeObra("Alinhamento e balanceamento", Decimal("1.00"), 120, marcos),
        Peca("Pastilha de freio dianteira", 1, 320, "PST-014", "Freios & Cia"),
        MaoDeObra("Substituição de pastilhas", Decimal("1.50"), 120, marcos),
        Peca("Correia dentada", 1, 215, "CRR-220", "Auto Peças Central"),
    ):
        os_0042.adicionar_item(item)
    os_repo.salvar(os_0042)

    # OS 2026-0041 — em execução, total R$ 860,00.
    os_0041 = _criar_os("2026-0041", carlos, gol, marcos, datetime(2026, 10, 23, 8, 15))
    for item in (
        Peca("Pastilha de freio dianteira", 1, 320, "PST-014", "Freios & Cia"),
        MaoDeObra("Substituição de pastilhas", Decimal("1.50"), 120, marcos),
        Peca("Disco de freio", 1, 240, "DSC-008", "Freios & Cia"),
        MaoDeObra("Revisão do sistema de freios", Decimal("1.00"), 120, marcos),
    ):
        os_0041.adicionar_item(item)
    os_0041.aprovar("seed", data_hora=datetime(2026, 10, 23, 9, 15))
    os_0041.iniciar("seed", data_hora=datetime(2026, 10, 23, 10, 0))
    os_repo.salvar(os_0041)

    # OS 2026-0039 — aprovada, total R$ 2.300,00.
    os_0039 = _criar_os("2026-0039", joao, corolla, diego, datetime(2026, 10, 22, 14, 0))
    for item in (
        Peca("Kit de embreagem", 1, 1450, "EMB-300", "Transmissões ABC"),
        MaoDeObra("Troca de kit de embreagem", Decimal("4.00"), 120, diego),
        Peca("Atuador hidráulico", 1, 250, "ATU-045", "Transmissões ABC"),
        MaoDeObra("Sangria e regulagem", Decimal("1.00"), 120, diego),
    ):
        os_0039.adicionar_item(item)
    os_0039.aprovar("seed", data_hora=datetime(2026, 10, 22, 15, 0))
    os_repo.salvar(os_0039)

    # OS 2026-0038 — cancelada, total R$ 420,00.
    os_0038 = _criar_os("2026-0038", mariana, onix, rafael, datetime(2026, 10, 21, 11, 0))
    os_0038.adicionar_item(Peca("Sensor de estacionamento", 1, 300, "SNS-009", "Elétrica Paulista"))
    os_0038.adicionar_item(MaoDeObra("Instalação de sensor", Decimal("1.00"), 120, rafael))
    os_0038.cancelar(
        "Cliente optou por adiar o serviço",
        "seed",
        data_hora=datetime(2026, 10, 21, 12, 0),
    )
    os_repo.salvar(os_0038)

    # OS 2026-0040 — finalizada, total R$ 1.980,00.
    os_0040 = _criar_os("2026-0040", fernanda, argo, rafael, datetime(2026, 10, 20, 10, 0))
    os_0040.adicionar_item(Peca("Kit de suspensão dianteira", 1, 1500, "SUS-100", "Suspensões SP"))
    os_0040.adicionar_item(MaoDeObra("Substituição de suspensão", Decimal("4.00"), 120, rafael))
    _finalizar_os(os_0040, veiculo_repo)
    os_repo.salvar(os_0040)

    # OS 2026-0037 — finalizada, total R$ 980,00.
    os_0037 = _criar_os("2026-0037", roberto, ka, diego, datetime(2026, 10, 19, 9, 0))
    os_0037.adicionar_item(Peca("Bateria 60Ah", 1, 740, "BAT-060", "Baterias Power"))
    os_0037.adicionar_item(MaoDeObra("Diagnóstico e troca de bateria", Decimal("2.00"), 120, diego))
    _finalizar_os(os_0037, veiculo_repo)
    os_repo.salvar(os_0037)

    # 16 OS finalizadas que completam os totais históricos da Etapa 2.
    clientes = [ana, carlos, fernanda, joao, mariana, roberto]
    veiculos = [civic, gol, argo, corolla, onix, ka]
    geradas = [
        # (número, mecânico, horas, taxa, valor_peça, descrição da peça, índice cliente/veículo)
        ("2026-0021", marcos, Decimal("3.00"), 120, 625, "Kit de manutenção preventiva", 0),
        ("2026-0022", marcos, Decimal("3.00"), 120, 625, "Filtros e fluidos", 1),
        ("2026-0023", marcos, Decimal("3.00"), 120, 625, "Correia e tensores", 2),
        ("2026-0024", marcos, Decimal("3.00"), 120, 625, "Velas e cabos de ignição", 3),
        ("2026-0025", marcos, Decimal("3.00"), 120, 625, "Bomba de combustível", 4),
        ("2026-0026", marcos, Decimal("3.00"), 120, 625, "Sensores e atuadores", 5),
        ("2026-0027", marcos, Decimal("3.00"), 120, 625, "Revisão de 60 mil km", 0),
        ("2026-0028", marcos, Decimal("4.00"), 120, 625, "Kit de embreagem", 1),
        ("2026-0029", rafael, Decimal("3.00"), 120, 800, "Pastilhas e discos", 2),
        ("2026-0030", rafael, Decimal("3.00"), 120, 800, "Amortecedores dianteiros", 3),
        ("2026-0031", rafael, Decimal("3.00"), 120, 800, "Kit de suspensão", 4),
        ("2026-0032", rafael, Decimal("3.00"), 120, 800, "Alinhamento e balanceamento", 5),
        ("2026-0033", rafael, Decimal("1.00"), 380, 800, "Diagnóstico de suspensão", 0),
        ("2026-0034", diego, Decimal("2.00"), 120, 296, "Bateria e terminais", 1),
        ("2026-0035", diego, Decimal("2.00"), 120, 297, "Alternador", 2),
        ("2026-0036", diego, Decimal("2.50"), 120, 297, "Motor de partida", 3),
    ]
    for indice, (numero, mecanico, horas, taxa, valor_peca, descricao_peca, ref) in enumerate(geradas):
        cliente = clientes[ref % len(clientes)]
        veiculo = veiculos[ref % len(veiculos)]
        os_gerada = _criar_os(
            numero,
            cliente,
            veiculo,
            mecanico,
            datetime(2026, 10, 1 + indice, 9, 0),
        )
        os_gerada.adicionar_item(
            Peca(descricao_peca, 1, valor_peca, f"PEC-{numero[-4:]}", "Fornecedor Demo")
        )
        os_gerada.adicionar_item(
            MaoDeObra("Serviço executado", horas, taxa, mecanico)
        )
        _finalizar_os(os_gerada, veiculo_repo)
        os_repo.salvar(os_gerada)

    return {
        "clientes": cliente_repo.contar(),
        "mecanicos": mecanico_repo.contar(),
        "veiculos": veiculo_repo.contar(),
        "ordens": os_repo.contar(),
    }
