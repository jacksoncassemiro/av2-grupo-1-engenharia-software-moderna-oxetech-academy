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


class CrmDuplicado(RegraDeNegocioViolada):
    """US-02 / CA3."""

    status_code = 409
    mensagem = "CRM ja cadastrado"


class HorarioIndisponivel(RegraDeNegocioViolada):
    """RN03."""

    status_code = 409
    mensagem = "Horario indisponivel"


class CancelamentoNaoPermitido(RegraDeNegocioViolada):
    """RN04. O prazo vem de settings.CANCELAMENTO_ANTECEDENCIA_HORAS - nunca hardcoded."""

    status_code = 422
    mensagem = "Cancelamento indisponivel: fora do prazo minimo de antecedencia"


class MedicoInativo(RegraDeNegocioViolada):
    """RN16 - medico inativado nao recebe consulta nova."""

    status_code = 409
    mensagem = "Medico indisponivel para novos agendamentos"


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
    """US-00 / CA7 - mensagem generica de proposito: nao revela se o login existe."""

    status_code = 401
    mensagem = "Login ou senha invalidos"


class LoginJaAtivo(RegraDeNegocioViolada):
    """US-00 / CA6 - conflito de estado, nao falha de credencial."""

    status_code = 409
    mensagem = "Este CPF ja possui login ativo. Use a tela de login."


class DadosDeAutoCadastroIncompletos(RegraDeNegocioViolada):
    """US-00 / CA5 - campos exigidos so quando o CPF ainda nao tem cadastro."""

    status_code = 422
    mensagem = "Nome e telefone sao obrigatorios no auto-cadastro"
