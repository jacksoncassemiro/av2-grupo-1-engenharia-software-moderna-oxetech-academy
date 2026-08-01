"""Excecoes de dominio tipadas.

Clean Code (pratica 3): usar excecoes com significado em vez de retornar codigos
de erro / None. Cada excecao carrega o codigo HTTP que o handler deve devolver,
mantendo as regras de negocio ignorantes de HTTP.
"""


class RegraDeNegocioViolada(Exception):
    """Base de todas as violacoes de regra de negocio."""

    status_code: int = 400
    mensagem: str = "Regra de negocio violada"

    def __init__(self, mensagem: str | None = None):
        self.mensagem = mensagem or self.mensagem
        super().__init__(self.mensagem)


class CpfDuplicado(RegraDeNegocioViolada):
    """RN01."""

    status_code = 409
    mensagem = "CPF ja cadastrado"


class EmailDuplicado(RegraDeNegocioViolada):
    """RN02."""

    status_code = 409
    mensagem = "E-mail em uso"


class EspecialidadeDuplicada(RegraDeNegocioViolada):
    """US-01 / CA2."""

    status_code = 409
    mensagem = "Especialidade ja cadastrada"


class HorarioIndisponivel(RegraDeNegocioViolada):
    """RN03."""

    status_code = 409
    mensagem = "Horario indisponivel"


class CancelamentoNaoPermitido(RegraDeNegocioViolada):
    """RN04."""

    status_code = 422
    mensagem = "Cancelamento indisponivel. Prazo de antecedencia menor que 24 horas"


class MedicoJaAlocado(RegraDeNegocioViolada):
    """RN05."""

    status_code = 409
    mensagem = "Medico ja possui consulta agendada para este horario"


class TransicaoDeStatusInvalida(RegraDeNegocioViolada):
    """RN06 / RN10."""

    status_code = 422
    mensagem = "Transicao de status nao permitida"


class RecursoNaoEncontrado(RegraDeNegocioViolada):
    status_code = 404
    mensagem = "Recurso nao encontrado"


class CredenciaisInvalidas(RegraDeNegocioViolada):
    status_code = 401
    mensagem = "Login ou senha invalidos"
