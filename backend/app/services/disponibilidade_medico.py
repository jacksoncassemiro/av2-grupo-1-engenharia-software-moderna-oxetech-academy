"""Quem pode receber consulta nova — RN16 e RN17 em um lugar só.

Duas telas diferentes precisam da mesma regra: a agenda (`AgendaService.listar_livres`,
que apenas deixa de oferecer horário) e a reserva (`ConsultaService._reservar_slot`, que
precisa dizer ao usuário qual dos dois lados barrou). Deixar a condição escrita nos dois
services faria a RN existir em duplicata — e é justamente a duplicata que a auditoria
encontrou entre inativar o médico e inativar a especialidade dele.

Decisão registrada no ADR-009.
"""

from app.exceptions.dominio import EspecialidadeInativa, MedicoInativo
from app.models.medico import Medico


def pode_receber_consulta(medico: Medico) -> bool:
    """RN16 (médico ativo) + RN17 (especialidade dele também ativa)."""
    return bool(medico.ativo) and bool(medico.especialidade.ativo)


def garantir_que_recebe_consulta(medico: Medico) -> None:
    """Mesma regra, com a exceção tipada que diz qual dos dois lados barrou."""
    if not medico.ativo:
        raise MedicoInativo  # RN16
    if not medico.especialidade.ativo:
        raise EspecialidadeInativa  # RN17
