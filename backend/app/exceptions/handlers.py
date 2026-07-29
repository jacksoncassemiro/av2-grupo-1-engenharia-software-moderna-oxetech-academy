"""Traduz excecoes de dominio em respostas HTTP - unico ponto de acoplamento."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.dominio import RegraDeNegocioViolada


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(RegraDeNegocioViolada)
    async def _handler(_: Request, erro: RegraDeNegocioViolada) -> JSONResponse:
        return JSONResponse(
            status_code=erro.status_code,
            content={"detail": erro.mensagem, "erro": type(erro).__name__},
        )
