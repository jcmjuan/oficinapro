"""Diálogos modais e documentos da interface."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from domain.cliente import Cliente
from domain.mecanico import Mecanico
from domain.ordem_servico import OrdemServico
from domain.validators import formatar_brl
from domain.veiculo import Veiculo

from .components import Card, SummaryRow, button_style, clear_children, divider, status_badge
from .theme import COLORS
from .utils import (
    abrir_arquivo,
    abrir_url,
    formatar_data,
    formatar_percentual,
    para_decimal,
    para_inteiro,
)


class FormDialog(ctk.CTkToplevel):
    """Base para formulários em modal com cabeçalho, corpo rolável e rodapé."""

    def __init__(
        self,
        parent,
        app,
        title: str,
        subtitle: str = "",
        *,
        width: int = 540,
        height: int = 660,
    ):
        super().__init__(parent)
        self.withdraw()
        self.app = app
        self.result = None
        self.title(title)
        self.configure(fg_color=COLORS["bg"])
        self.transient(parent)
        self.resizable(False, True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text=title,
            font=app.fonts.h2,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(18, 0))
        if subtitle:
            ctk.CTkLabel(
                header,
                text=subtitle,
                font=app.fonts.small,
                text_color=COLORS["muted"],
                anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=22, pady=(2, 16))
        else:
            header.grid_rowconfigure(1, minsize=16)
        ctk.CTkButton(
            header,
            text="×",
            width=32,
            height=32,
            corner_radius=8,
            font=app.fonts.h3,
            command=self.cancel,
            **button_style("ghost"),
        ).grid(row=0, column=1, rowspan=2, padx=(0, 18), pady=12)

        self.body = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["slate_light"],
            scrollbar_button_hover_color=COLORS["muted"],
        )
        self.body.grid(row=1, column=0, sticky="nsew", padx=22, pady=(16, 8))
        self.body.grid_columnconfigure(0, weight=1)

        footer = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(
            footer,
            text="Cancelar",
            command=self.cancel,
            width=110,
            height=36,
            corner_radius=9,
            font=app.fonts.button,
            **button_style("secondary"),
        ).grid(row=0, column=1, padx=(0, 8), pady=14)
        self.save_button = ctk.CTkButton(
            footer,
            text="Salvar",
            command=self.save,
            width=130,
            height=36,
            corner_radius=9,
            font=app.fonts.button,
            **button_style("primary"),
        )
        self.save_button.grid(row=0, column=2, padx=(0, 18), pady=14)

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.bind("<Escape>", lambda _event: self.cancel())
        self.bind("<Control-Return>", lambda _event: self.save())
        self._center(parent, width, height)
        self.deiconify()
        self.after_idle(self._activate)

    def _center(self, parent, width: int, height: int) -> None:
        try:
            largura, altura = parent.winfo_width(), parent.winfo_height()
            if largura <= 1 or altura <= 1:
                x = max(0, (self.winfo_screenwidth() - width) // 2)
                y = max(0, (self.winfo_screenheight() - height) // 2)
            else:
                x = parent.winfo_rootx() + max(0, (largura - width) // 2)
                y = parent.winfo_rooty() + max(0, (altura - height) // 2)
        except Exception:
            x = y = 80
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _activate(self) -> None:
        try:
            if not self.winfo_viewable():
                self.after(30, self._activate)
                return
            self.grab_set()
            self.focus_force()
        except Exception:
            pass

    def add_field(
        self,
        label: str,
        *,
        initial: str = "",
        placeholder: str = "",
        show: str | None = None,
    ) -> ctk.CTkEntry:
        wrapper = ctk.CTkFrame(self.body, fg_color="transparent")
        wrapper.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            wrapper,
            text=label,
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
            anchor="w",
        ).pack(anchor="w", pady=(0, 4))
        entry = ctk.CTkEntry(
            wrapper,
            height=38,
            corner_radius=8,
            font=self.app.fonts.body,
            placeholder_text=placeholder,
            show=show,
            border_color=COLORS["border"],
            fg_color=COLORS["surface"],
        )
        entry.pack(fill="x")
        if initial:
            entry.insert(0, str(initial))
        return entry

    def add_textbox(
        self,
        label: str,
        *,
        initial: str = "",
        height: int = 100,
        placeholder: str = "",
    ) -> ctk.CTkTextbox:
        wrapper = ctk.CTkFrame(self.body, fg_color="transparent")
        wrapper.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            wrapper,
            text=label,
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
            anchor="w",
        ).pack(anchor="w", pady=(0, 4))
        textbox = ctk.CTkTextbox(
            wrapper,
            height=height,
            corner_radius=8,
            font=self.app.fonts.body,
            border_width=1,
            border_color=COLORS["border"],
            fg_color=COLORS["surface"],
        )
        textbox.pack(fill="x")
        if initial:
            textbox.insert("1.0", initial)
        return textbox

    def add_option(
        self,
        label: str,
        values: list[str],
        variable: ctk.StringVar,
        *,
        command=None,
    ) -> ctk.CTkOptionMenu:
        wrapper = ctk.CTkFrame(self.body, fg_color="transparent")
        wrapper.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            wrapper,
            text=label,
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
            anchor="w",
        ).pack(anchor="w", pady=(0, 4))
        menu = ctk.CTkOptionMenu(
            wrapper,
            values=values or ["—"],
            variable=variable,
            command=command,
            height=38,
            corner_radius=8,
            font=self.app.fonts.body,
            fg_color=COLORS["surface_alt"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["slate_light"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["surface"],
            dropdown_text_color=COLORS["text"],
            dropdown_hover_color=COLORS["surface_alt"],
        )
        menu.pack(fill="x")
        return menu

    def add_hint(self, text: str) -> None:
        ctk.CTkLabel(
            self.body,
            text=text,
            font=self.app.fonts.tiny,
            text_color=COLORS["muted"],
            anchor="w",
            wraplength=470,
        ).pack(fill="x", pady=(0, 8))

    def save(self) -> None:  # pragma: no cover - sobrescrito
        pass

    def cancel(self) -> None:
        self.result = None
        self.destroy()

    def finish(self, result=True) -> None:
        self.result = result
        self.destroy()

    def show_error(self, mensagem: str) -> None:
        messagebox.showerror("Não foi possível salvar", mensagem, parent=self)


class ClienteDialog(FormDialog):
    def __init__(self, parent, app, cliente: Cliente | None = None):
        super().__init__(
            parent,
            app,
            "Editar cliente" if cliente else "Novo cliente",
            "Cadastro de contato e endereço",
            width=560,
            height=700,
        )
        self.repo = app.context.clientes
        self.cliente = cliente
        self.nome = self.add_field("Nome completo *", initial=cliente.nome if cliente else "")
        self.documento = self.add_field(
            "CPF/CNPJ *",
            initial=cliente.cpf_cnpj if cliente else "",
            placeholder="000.000.000-00",
        )
        self.telefone = self.add_field(
            "Telefone *",
            initial=cliente.telefone_formatado if cliente else "",
            placeholder="(11) 99999-9999",
        )
        self.email = self.add_field(
            "E-mail",
            initial=(cliente.email or "") if cliente else "",
            placeholder="cliente@email.com",
        )
        self.endereco = self.add_field(
            "Endereço",
            initial=cliente.endereco if cliente else "",
            placeholder="Rua, número — bairro, cidade/UF",
        )
        self.nascimento = self.add_field(
            "Data de nascimento",
            initial=formatar_data(cliente.data_nascimento) if cliente and cliente.data_nascimento else "",
            placeholder="DD/MM/AAAA",
        )
        self.observacoes = self.add_textbox(
            "Observações",
            initial=cliente.observacoes if cliente else "",
            height=80,
        )
        if cliente:
            self.documento.configure(state="disabled")

    def save(self) -> None:
        try:
            if self.cliente is None:
                novo = Cliente(
                    self.nome.get(),
                    self.telefone.get(),
                    self.documento.get(),
                    email=self.email.get().strip() or None,
                    endereco=self.endereco.get().strip() or None,
                    data_nascimento=self.nascimento.get().strip() or None,
                    observacoes=self.observacoes.get("1.0", "end").strip(),
                )
                self.repo.salvar(novo)
            else:
                self.cliente.atualizar_dados(
                    nome=self.nome.get(),
                    telefone=self.telefone.get(),
                    email=self.email.get().strip() or None,
                    endereco=self.endereco.get().strip() or None,
                    data_nascimento=self.nascimento.get().strip() or None,
                    observacoes=self.observacoes.get("1.0", "end").strip(),
                )
                self.repo.salvar(self.cliente)
            self.finish(True)
        except Exception as exc:
            self.show_error(str(exc))


class VeiculoDialog(FormDialog):
    def __init__(self, parent, app, veiculo: Veiculo | None = None, cliente_id: int | None = None):
        super().__init__(
            parent,
            app,
            "Editar veículo" if veiculo else "Novo veículo",
            "Dados do veículo e vínculo com o cliente",
            width=560,
            height=720,
        )
        self.repo = app.context.veiculos
        self.veiculo = veiculo
        self.clientes = app.context.clientes.listar(apenas_ativos=False)
        if not self.clientes:
            self.after(100, lambda: messagebox.showwarning(
                "Clientes", "Cadastre um cliente antes de incluir veículos.", parent=self
            ))
        self.cliente_por_label = {
            f"{c.nome} — {c.cpf_cnpj}" + ("" if c.ativo else " (inativo)"): c
            for c in self.clientes
        }
        labels = list(self.cliente_por_label) or ["—"]
        selecionado = labels[0]
        if veiculo and veiculo.cliente:
            for label, cliente in self.cliente_por_label.items():
                if cliente.id == veiculo.cliente.id:
                    selecionado = label
                    break
        elif cliente_id:
            for label, cliente in self.cliente_por_label.items():
                if cliente.id == cliente_id:
                    selecionado = label
                    break
        self.cliente_var = ctk.StringVar(value=selecionado)
        self.cliente_menu = self.add_option("Cliente *", labels, self.cliente_var)
        self.placa = self.add_field(
            "Placa *",
            initial=veiculo.placa if veiculo else "",
            placeholder="ABC-1D23",
        )
        self.marca = self.add_field("Marca *", initial=veiculo.marca if veiculo else "")
        self.modelo = self.add_field("Modelo *", initial=veiculo.modelo if veiculo else "")
        self.ano = self.add_field(
            "Ano *",
            initial=str(veiculo.ano) if veiculo else "",
            placeholder="2020",
        )
        self.km = self.add_field(
            "Quilometragem *",
            initial=str(veiculo.km) if veiculo else "0",
        )
        self.cor = self.add_field("Cor", initial=veiculo.cor if veiculo else "")
        self.combustivel = self.add_field(
            "Combustível",
            initial=veiculo.combustivel if veiculo else "",
            placeholder="Flex, gasolina, diesel...",
        )
        if veiculo:
            self.placa.configure(state="disabled")
        self.add_hint("A placa não pode ser alterada depois do cadastro. A quilometragem não pode diminuir.")

    def save(self) -> None:
        try:
            cliente = self.cliente_por_label.get(self.cliente_var.get())
            if cliente is None:
                raise ValueError("Selecione um cliente.")
            ano = para_inteiro(self.ano.get())
            km = para_inteiro(self.km.get())
            if self.veiculo is None:
                novo = Veiculo(
                    self.placa.get(),
                    self.marca.get(),
                    self.modelo.get(),
                    ano,
                    km,
                    cliente,
                    cor=self.cor.get().strip() or None,
                    combustivel=self.combustivel.get().strip() or None,
                )
                self.repo.salvar(novo)
            else:
                self.veiculo.atualizar_dados(
                    marca=self.marca.get(),
                    modelo=self.modelo.get(),
                    ano=ano,
                    cor=self.cor.get().strip() or None,
                    combustivel=self.combustivel.get().strip() or None,
                )
                self.veiculo.atualizar_km(km)
                self.veiculo.vincular_cliente(cliente)
                self.repo.salvar(self.veiculo)
            self.finish(True)
        except Exception as exc:
            self.show_error(str(exc))


class MecanicoDialog(FormDialog):
    def __init__(self, parent, app, mecanico: Mecanico | None = None):
        super().__init__(
            parent,
            app,
            "Editar mecânico" if mecanico else "Novo mecânico",
            "Equipe técnica e percentual de comissão",
            width=540,
            height=660,
        )
        self.repo = app.context.mecanicos
        self.mecanico = mecanico
        self.nome = self.add_field("Nome *", initial=mecanico.nome if mecanico else "")
        self.telefone = self.add_field(
            "Telefone *",
            initial=mecanico.telefone_formatado if mecanico else "",
            placeholder="(11) 99999-9999",
        )
        self.registro = self.add_field(
            "Registro *",
            initial=mecanico.registro if mecanico else "",
            placeholder="MEC-004",
        )
        self.email = self.add_field(
            "E-mail",
            initial=(mecanico.email or "") if mecanico else "",
        )
        self.especialidade = self.add_field(
            "Especialidade",
            initial=mecanico.especialidade if mecanico else "",
            placeholder="Motor, suspensão, elétrica...",
        )
        taxa_inicial = ""
        if mecanico:
            taxa_inicial = f"{(mecanico.taxa_comissao * 100):.1f}".replace(".", ",")
        self.taxa = self.add_field(
            "Comissão (%) *",
            initial=taxa_inicial,
            placeholder="10",
        )
        self.add_hint("A comissão é calculada sobre a mão de obra das OS finalizadas.")

    def save(self) -> None:
        try:
            taxa = para_decimal(self.taxa.get()) / Decimal("100")
            if self.mecanico is None:
                novo = Mecanico(
                    self.nome.get(),
                    self.telefone.get(),
                    self.registro.get(),
                    taxa,
                    email=self.email.get().strip() or None,
                    especialidade=self.especialidade.get().strip() or None,
                )
                self.repo.salvar(novo)
            else:
                self.mecanico.atualizar_dados(
                    nome=self.nome.get(),
                    telefone=self.telefone.get(),
                    email=self.email.get().strip() or None,
                    registro=self.registro.get(),
                    taxa_comissao=taxa,
                    especialidade=self.especialidade.get().strip() or None,
                )
                self.repo.salvar(self.mecanico)
            self.finish(True)
        except Exception as exc:
            self.show_error(str(exc))


class PromptDialog(FormDialog):
    def __init__(
        self,
        parent,
        app,
        title: str,
        label: str,
        *,
        initial: str = "",
        numeric: bool = False,
        multiline: bool = False,
        confirm_text: str = "Confirmar",
    ):
        super().__init__(parent, app, title, "", width=480, height=360)
        self.numeric = numeric
        self.multiline = multiline
        if multiline:
            self.entry = self.add_textbox(label, initial=initial, height=110)
        else:
            self.entry = self.add_field(label, initial=initial)
        self.save_button.configure(text=confirm_text)

    def save(self) -> None:
        try:
            if self.multiline:
                valor = self.entry.get("1.0", "end").strip()
            else:
                valor = self.entry.get().strip()
            if not valor:
                raise ValueError("Preencha o campo para continuar.")
            if self.numeric:
                valor = para_inteiro(valor)
            self.finish(valor)
        except Exception as exc:
            self.show_error(str(exc))


class NovaOSDialog(FormDialog):
    def __init__(
        self,
        parent,
        app,
        *,
        cliente_id: int | None = None,
        veiculo_id: int | None = None,
    ):
        super().__init__(
            parent,
            app,
            "Nova ordem de serviço",
            "Selecione o cliente, o veículo e o responsável técnico",
            width=580,
            height=560,
        )
        self.context = app.context
        self.clientes = self.context.clientes.listar()
        self.mecanicos = self.context.mecanicos.listar()
        self.cliente_por_label = {
            f"{c.nome} — {c.cpf_cnpj}": c for c in self.clientes
        }
        self.mecanico_por_label = {
            f"{m.nome} — {formatar_percentual(m.taxa_comissao)}": m for m in self.mecanicos
        }
        self.veiculo_por_label: dict[str, Veiculo] = {}
        cliente_inicial = next(iter(self.cliente_por_label), "—")
        if cliente_id:
            for label, cliente in self.cliente_por_label.items():
                if cliente.id == cliente_id:
                    cliente_inicial = label
                    break
        self.cliente_var = ctk.StringVar(value=cliente_inicial)
        self.cliente_menu = self.add_option(
            "Cliente *",
            list(self.cliente_por_label) or ["—"],
            self.cliente_var,
            command=self._atualizar_veiculos,
        )
        self.veiculo_var = ctk.StringVar(value="—")
        self.veiculo_menu = self.add_option("Veículo *", ["—"], self.veiculo_var)
        mecanico_inicial = next(iter(self.mecanico_por_label), "—")
        self.mecanico_var = ctk.StringVar(value=mecanico_inicial)
        self.mecanico_menu = self.add_option(
            "Mecânico responsável *",
            list(self.mecanico_por_label) or ["—"],
            self.mecanico_var,
        )
        self.observacoes = self.add_textbox(
            "Observações",
            height=90,
            placeholder="Relato do cliente, previsão de entrega...",
        )
        self.add_hint("A OS será criada em Orçamento. Os itens podem ser adicionados na próxima tela.")
        self._atualizar_veiculos()
        if veiculo_id:
            for label, veiculo in self.veiculo_por_label.items():
                if veiculo.id == veiculo_id:
                    self.veiculo_var.set(label)
                    break

    def _cliente_selecionado(self) -> Cliente | None:
        return self.cliente_por_label.get(self.cliente_var.get())

    def _atualizar_veiculos(self, _valor: str | None = None) -> None:
        cliente = self._cliente_selecionado()
        veiculos = (
            self.context.veiculos.listar(cliente_id=cliente.id) if cliente else []
        )
        self.veiculo_por_label = {
            f"{v.marca} {v.modelo} — {v.placa} ({v.ano})": v for v in veiculos
        }
        labels = list(self.veiculo_por_label) or ["—"]
        self.veiculo_menu.configure(values=labels)
        if self.veiculo_var.get() not in labels:
            self.veiculo_var.set(labels[0])

    def save(self) -> None:
        try:
            cliente = self._cliente_selecionado()
            veiculo = self.veiculo_por_label.get(self.veiculo_var.get())
            mecanico = self.mecanico_por_label.get(self.mecanico_var.get())
            if cliente is None:
                raise ValueError("Selecione um cliente.")
            if veiculo is None:
                raise ValueError("Selecione um veículo.")
            if mecanico is None:
                raise ValueError("Selecione um mecânico.")
            ordem = self.context.ordem_service.criar_ordem(
                cliente.id,
                veiculo.id,
                mecanico.id,
                observacoes=self.observacoes.get("1.0", "end").strip(),
                criado_por="interface",
            )
            self.finish(ordem.numero)
        except Exception as exc:
            self.show_error(str(exc))


class ItemPecaDialog(FormDialog):
    def __init__(self, parent, app, numero: str):
        super().__init__(
            parent,
            app,
            "Adicionar peça",
            f"OS {numero} • item de peça",
            width=520,
            height=620,
        )
        self.context = app.context
        self.numero = numero
        self.descricao = self.add_field("Descrição *", placeholder="Filtro de óleo")
        self.quantidade = self.add_field("Quantidade *", initial="1")
        self.valor = self.add_field("Valor unitário *", placeholder="45,00")
        self.codigo = self.add_field("Código", placeholder="FLT-001")
        self.fornecedor = self.add_field("Fornecedor", placeholder="Auto Peças Central")

    def save(self) -> None:
        try:
            self.context.ordem_service.adicionar_peca(
                self.numero,
                self.descricao.get(),
                para_decimal(self.quantidade.get()),
                para_decimal(self.valor.get()),
                codigo=self.codigo.get().strip() or None,
                fornecedor=self.fornecedor.get().strip() or None,
            )
            self.finish(True)
        except Exception as exc:
            self.show_error(str(exc))


class ItemMaoObraDialog(FormDialog):
    def __init__(self, parent, app, numero: str, ordem: OrdemServico):
        super().__init__(
            parent,
            app,
            "Adicionar mão de obra",
            f"OS {numero} • serviço executado",
            width=520,
            height=600,
        )
        self.context = app.context
        self.numero = numero
        self.ordem = ordem
        self.mecanicos = self.context.mecanicos.listar()
        self.mecanico_por_label = {
            f"{m.nome} — {formatar_percentual(m.taxa_comissao)}": m for m in self.mecanicos
        }
        self.descricao = self.add_field("Descrição *", placeholder="Troca de óleo e filtros")
        self.horas = self.add_field("Horas *", initial="1,0")
        taxa_padrao = self.context.oficinas.obter().taxa_horaria_padrao
        self.taxa = self.add_field(
            "Taxa horária *",
            initial=f"{taxa_padrao:.2f}".replace(".", ","),
        )
        labels = [f"Responsável da OS — {ordem.mecanico.nome}"] + list(self.mecanico_por_label)
        self.mecanico_var = ctk.StringVar(value=labels[0])
        self.mecanico_menu = self.add_option("Executor", labels, self.mecanico_var)
        self.add_hint("O executor define a base de comissão. Sem seleção, usa o responsável da OS.")

    def save(self) -> None:
        try:
            label = self.mecanico_var.get()
            mecanico = self.mecanico_por_label.get(label)
            mecanico_id = mecanico.id if mecanico else None
            self.context.ordem_service.adicionar_mao_de_obra(
                self.numero,
                self.descricao.get(),
                para_decimal(self.horas.get()),
                para_decimal(self.taxa.get()),
                mecanico_id=mecanico_id,
            )
            self.finish(True)
        except Exception as exc:
            self.show_error(str(exc))


class DocumentoDialog(ctk.CTkToplevel):
    """Visualização do orçamento/recibo com ações de PDF e WhatsApp."""

    def __init__(self, parent, app, ordem: OrdemServico):
        super().__init__(parent)
        self.withdraw()
        self.app = app
        self.ordem = ordem
        self.pdf_path: Path | None = None
        self.title(f"Documento — OS {ordem.numero}")
        self.configure(fg_color=COLORS["bg"])
        self.transient(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._center(parent, 780, 860)

        header = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text="Recibo" if ordem.status.value == "FINALIZADA" else "Orçamento",
            font=app.fonts.h2,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(16, 0))
        ctk.CTkLabel(
            header,
            text=f"OS {ordem.numero} • {ordem.cliente.nome}",
            font=app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=22, pady=(2, 14))
        ctk.CTkButton(
            header,
            text="×",
            width=32,
            height=32,
            corner_radius=8,
            font=app.fonts.h3,
            command=self.destroy,
            **button_style("ghost"),
        ).grid(row=0, column=1, rowspan=2, padx=(0, 18), pady=12)

        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["slate_light"],
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=22, pady=(16, 8))
        self.content.grid_columnconfigure(0, weight=1)
        self._montar()

        footer = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        self.feedback = ctk.CTkLabel(
            footer,
            text="",
            font=app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
        )
        self.feedback.grid(row=0, column=0, sticky="w", padx=22, pady=14)
        ctk.CTkButton(
            footer,
            text="Copiar mensagem",
            command=self.copiar_mensagem,
            width=130,
            height=34,
            corner_radius=8,
            font=app.fonts.button_small,
            **button_style("secondary"),
        ).grid(row=0, column=1, padx=4, pady=12)
        ctk.CTkButton(
            footer,
            text="WhatsApp",
            command=self.abrir_whatsapp,
            width=100,
            height=34,
            corner_radius=8,
            font=app.fonts.button_small,
            **button_style("secondary"),
        ).grid(row=0, column=2, padx=4, pady=12)
        ctk.CTkButton(
            footer,
            text="Abrir PDF",
            command=self.abrir_pdf,
            width=100,
            height=34,
            corner_radius=8,
            font=app.fonts.button_small,
            **button_style("secondary"),
        ).grid(row=0, column=3, padx=4, pady=12)
        ctk.CTkButton(
            footer,
            text="Gerar PDF",
            command=self.gerar_pdf,
            width=110,
            height=34,
            corner_radius=8,
            font=app.fonts.button_small,
            **button_style("primary"),
        ).grid(row=0, column=4, padx=(4, 18), pady=12)

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.deiconify()
        self.after_idle(self._activate)

    def _center(self, parent, width: int, height: int) -> None:
        try:
            largura, altura = parent.winfo_width(), parent.winfo_height()
            if largura <= 1 or altura <= 1:
                x = max(0, (self.winfo_screenwidth() - width) // 2)
                y = max(0, (self.winfo_screenheight() - height) // 2)
            else:
                x = parent.winfo_rootx() + max(0, (largura - width) // 2)
                y = parent.winfo_rooty() + max(0, (altura - height) // 2)
        except Exception:
            x = y = 50
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _activate(self) -> None:
        try:
            if not self.winfo_viewable():
                self.after(30, self._activate)
                return
            self.grab_set()
            self.focus_force()
        except Exception:
            pass

    def _montar(self) -> None:
        clear_children(self.content)
        oficina = self.app.context.oficinas.obter()
        ordem = self.ordem

        topo = Card(self.content)
        topo.pack(fill="x", pady=(0, 12))
        topo.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            topo,
            text=oficina.nome,
            font=self.app.fonts.h2,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 0))
        ctk.CTkLabel(
            topo,
            text=f"{oficina.cnpj} • {oficina.telefone_formatado}\n{oficina.endereco}",
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(2, 14))
        direita = ctk.CTkFrame(topo, fg_color="transparent")
        direita.grid(row=0, column=1, rowspan=2, sticky="e", padx=18, pady=14)
        ctk.CTkLabel(
            direita,
            text="RECIBO" if ordem.status.value == "FINALIZADA" else "ORÇAMENTO",
            font=self.app.fonts.tiny,
            text_color=COLORS["primary"],
            anchor="e",
        ).pack(anchor="e")
        ctk.CTkLabel(
            direita,
            text=f"OS {ordem.numero}",
            font=self.app.fonts.h2,
            text_color=COLORS["text"],
            anchor="e",
        ).pack(anchor="e")
        status_badge(direita, ordem.status, self.app).pack(anchor="e", pady=(4, 0))

        info = Card(self.content)
        info.pack(fill="x", pady=(0, 12))
        for col in range(3):
            info.grid_columnconfigure(col, weight=1)
        self._bloco_info(info, 0, "Cliente", ordem.cliente.nome, ordem.cliente.telefone_formatado, ordem.cliente.email or "")
        self._bloco_info(info, 1, "Veículo", f"{ordem.veiculo.marca} {ordem.veiculo.modelo}", ordem.veiculo.placa, f"{ordem.veiculo.ano} • {ordem.veiculo.km:,} km".replace(",", "."))
        self._bloco_info(info, 2, "Responsável técnico", ordem.mecanico.nome, ordem.mecanico.registro, ordem.mecanico.especialidade)

        itens = Card(self.content)
        itens.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            itens,
            text="Itens do serviço",
            font=self.app.fonts.h3,
            text_color=COLORS["text"],
            anchor="w",
        ).pack(fill="x", padx=18, pady=(14, 8))
        header = ctk.CTkFrame(itens, fg_color=COLORS["surface_alt"], corner_radius=0)
        header.pack(fill="x", padx=18)
        for col, (titulo, weight) in enumerate(
            [("Tipo", 1), ("Descrição", 4), ("Qtd/Horas", 1), ("Unitário", 1), ("Subtotal", 1)]
        ):
            header.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(
                header,
                text=titulo.upper(),
                font=self.app.fonts.tiny,
                text_color=COLORS["muted"],
                anchor="w",
            ).grid(row=0, column=col, sticky="w", padx=8, pady=7)
        for indice, item in enumerate(ordem.itens):
            linha = ctk.CTkFrame(itens, fg_color="transparent", corner_radius=0)
            linha.pack(fill="x", padx=18)
            for col, weight in enumerate([1, 4, 1, 1, 1]):
                linha.grid_columnconfigure(col, weight=weight)
            tipo = item.rotulo_tipo
            qtd = item.quantidade_formatada
            ctk.CTkLabel(linha, text=tipo, font=self.app.fonts.small, text_color=COLORS["muted"], anchor="w").grid(row=0, column=0, sticky="w", padx=8, pady=6)
            ctk.CTkLabel(linha, text=item.descricao, font=self.app.fonts.small, text_color=COLORS["text"], anchor="w").grid(row=0, column=1, sticky="w", padx=8, pady=6)
            ctk.CTkLabel(linha, text=qtd, font=self.app.fonts.small, text_color=COLORS["text"], anchor="w").grid(row=0, column=2, sticky="w", padx=8, pady=6)
            ctk.CTkLabel(linha, text=formatar_brl(item.valor_unitario), font=self.app.fonts.small, text_color=COLORS["text"], anchor="w").grid(row=0, column=3, sticky="w", padx=8, pady=6)
            ctk.CTkLabel(linha, text=formatar_brl(item.subtotal), font=self.app.fonts.small_bold, text_color=COLORS["text"], anchor="w").grid(row=0, column=4, sticky="w", padx=8, pady=6)
            if indice < len(ordem.itens) - 1:
                divider(itens).pack(fill="x", padx=18)

        resumo = Card(self.content)
        resumo.pack(fill="x", pady=(0, 12))
        resumo.grid_columnconfigure(0, weight=1)
        valores = ctk.CTkFrame(resumo, fg_color="transparent")
        valores.grid(row=0, column=1, sticky="e", padx=18, pady=12)
        for label, valor in (
            ("Peças", formatar_brl(ordem.subtotal_pecas)),
            ("Mão de obra", formatar_brl(ordem.subtotal_mao_obra)),
            ("Subtotal", formatar_brl(ordem.subtotal)),
            ("Desconto", formatar_brl(ordem.desconto)),
        ):
            SummaryRow(valores, self.app, label, valor).pack(fill="x", pady=1)
        divider(valores).pack(fill="x", pady=5)
        SummaryRow(valores, self.app, "Total", formatar_brl(ordem.total), strong=True).pack(fill="x")

        condicoes = Card(self.content)
        condicoes.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            condicoes,
            text="Condições",
            font=self.app.fonts.h3,
            text_color=COLORS["text"],
            anchor="w",
        ).pack(fill="x", padx=18, pady=(14, 4))
        ctk.CTkLabel(
            condicoes,
            text=(
                "Orçamento válido por 7 dias. A execução do serviço está condicionada à aprovação do cliente. "
                "Peças e insumos podem sofrer reajuste do fornecedor até o início dos serviços."
                if ordem.status.value != "FINALIZADA"
                else "Serviço finalizado. Documento emitido para conferência e comprovação do atendimento."
            ),
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
            justify="left",
            wraplength=660,
        ).pack(fill="x", padx=18, pady=(0, 14))

        historico = Card(self.content)
        historico.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            historico,
            text="Histórico de status",
            font=self.app.fonts.h3,
            text_color=COLORS["text"],
            anchor="w",
        ).pack(fill="x", padx=18, pady=(14, 4))
        for registro in ordem.historico:
            ctk.CTkLabel(
                historico,
                text=registro.descricao()
                + (f" • {registro.usuario}" if registro.usuario else "")
                + (f" • {registro.motivo}" if registro.motivo else ""),
                font=self.app.fonts.small,
                text_color=COLORS["muted"],
                anchor="w",
            ).pack(fill="x", padx=18, pady=1)
        ctk.CTkLabel(historico, text="", height=6).pack()

    def _bloco_info(self, master, col: int, titulo: str, linha1: str, linha2: str, linha3: str) -> None:
        bloco = ctk.CTkFrame(master, fg_color="transparent")
        bloco.grid(row=0, column=col, sticky="nw", padx=18, pady=14)
        ctk.CTkLabel(bloco, text=titulo.upper(), font=self.app.fonts.tiny, text_color=COLORS["muted"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(bloco, text=linha1, font=self.app.fonts.body_bold, text_color=COLORS["text"], anchor="w").pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(bloco, text=linha2, font=self.app.fonts.small, text_color=COLORS["muted"], anchor="w").pack(anchor="w")
        if linha3:
            ctk.CTkLabel(bloco, text=linha3, font=self.app.fonts.small, text_color=COLORS["muted"], anchor="w").pack(anchor="w")

    def gerar_pdf(self) -> None:
        try:
            self.configure(cursor="watch")
            self.feedback.configure(text="Gerando PDF...", text_color=COLORS["muted"])
            self.update_idletasks()
            self.pdf_path = self.app.context.orcamento_service.gerar_pdf(self.ordem.numero)
            self.feedback.configure(
                text=f"PDF gerado em {self.pdf_path}",
                text_color=COLORS["success"],
            )
            self.app.notify(f"PDF gerado: {self.pdf_path}")
        except Exception as exc:
            messagebox.showerror("Não foi possível gerar o PDF", str(exc), parent=self)
        finally:
            self.configure(cursor="")

    def abrir_pdf(self) -> None:
        try:
            if self.pdf_path is None or not Path(self.pdf_path).exists():
                self.gerar_pdf()
            if self.pdf_path and Path(self.pdf_path).exists():
                abrir_arquivo(self.pdf_path)
        except Exception as exc:
            messagebox.showerror("Não foi possível abrir o PDF", str(exc), parent=self)

    def abrir_whatsapp(self) -> None:
        try:
            link = self.app.context.orcamento_service.link_whatsapp(self.ordem.numero)
            abrir_url(link)
            self.app.notify("WhatsApp aberto no navegador.")
        except Exception as exc:
            messagebox.showerror("Não foi possível abrir o WhatsApp", str(exc), parent=self)

    def copiar_mensagem(self) -> None:
        try:
            mensagem = self.app.context.orcamento_service.mensagem_whatsapp(self.ordem.numero)
            self.clipboard_clear()
            self.clipboard_append(mensagem)
            self.feedback.configure(text="Mensagem copiada para a área de transferência.", text_color=COLORS["success"])
        except Exception as exc:
            messagebox.showerror("Não foi possível copiar", str(exc), parent=self)
