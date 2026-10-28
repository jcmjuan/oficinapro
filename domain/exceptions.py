"""Exceções de domínio do OficinaPro."""


class OficinaProError(Exception):
    """Erro base do sistema."""


class ValidacaoError(OficinaProError):
    """Dado inválido informado pelo usuário ou pela camada de aplicação."""


class RegraNegocioError(OficinaProError):
    """Operação viola uma regra de negócio."""


class TransicaoInvalida(RegraNegocioError):
    """Transição de status não permitida."""


class NaoEncontradoError(OficinaProError):
    """Entidade não encontrada."""


class DuplicadoError(OficinaProError):
    """Registro duplicado (CPF/CNPJ, placa, número de OS etc.)."""


class PdfError(OficinaProError):
    """Falha ao gerar um documento PDF."""
