/**
 * proxy.ts — Camada de redirecionamento por perfil (Next.js 16).
 *
 * Antigo `middleware.ts`, renomeado na v16. Executa no Edge antes de qualquer
 * render, lendo o cookie leve `clinica_perfil` (gravado por api.ts no login).
 *
 * Regras (RF18 / RN12):
 *
 *  | cookie      | rota pública  | → home do perfil                 |
 *  | cookie      | rota protegida do perfil correto | → next()        |
 *  | cookie      | rota do perfil errado | → home do próprio perfil   |
 *  | cookie      | rota desconhecida | → home do perfil              |
 *  | sem cookie  | rota pública  | → next()                         |
 *  | sem cookie  | rota protegida | → /login                        |
 *
 * AVISO: a autorização real é do backend (RN12). Este proxy é apenas UX.
 */

import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

import { HOME_POR_PERFIL } from '@/lib/rotas';
import type { TipoUsuario } from '@/types/dominio';

// ---------------------------------------------------------------------------
// Mapa de rotas por perfil — manter sincronizado com src/app/
// ---------------------------------------------------------------------------

const ROTAS_ATENDENTE = new Set([
  '/gerenciar-consultas',
  '/especialidades',
  '/medicos',
  '/pacientes',
  '/agenda',
]);

const ROTAS_PACIENTE = new Set(['/consultas', '/meus-dados', '/buscar-medicos', '/agendar']);

/** Rotas acessíveis sem autenticação. "/" não está aqui: ela redireciona todos (ver bloco de rota desconhecida). */
const ROTAS_PUBLICAS = new Set(['/login', '/primeiro-acesso']);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Extrai o primeiro segmento do pathname: "/gerenciar-consultas/123" → "/gerenciar-consultas" */
function segmentoRaiz(pathname: string): string {
  const partes = pathname.split('/');
  return '/' + (partes[1] ?? '');
}

function eRotaProtegida(raiz: string): boolean {
  return ROTAS_ATENDENTE.has(raiz) || ROTAS_PACIENTE.has(raiz);
}

function eRotaDoGrupo(raiz: string, perfil: string): boolean {
  if (perfil === 'ATENDENTE') return ROTAS_ATENDENTE.has(raiz);
  if (perfil === 'PACIENTE') return ROTAS_PACIENTE.has(raiz);
  return false;
}

// ---------------------------------------------------------------------------
// Proxy (exportação obrigatória no Next 16)
// ---------------------------------------------------------------------------

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const raiz = segmentoRaiz(pathname);

  const perfil = request.cookies.get('clinica_perfil')?.value ?? null;
  const autenticado = perfil !== null;

  // 1. Rota pública + autenticado → home do perfil
  if (ROTAS_PUBLICAS.has(raiz) && autenticado) {
    const home = HOME_POR_PERFIL[perfil as TipoUsuario] ?? '/login';
    return NextResponse.redirect(new URL(home, request.url));
  }

  // 2. Rota pública sem autenticação → deixa passar
  if (ROTAS_PUBLICAS.has(raiz)) {
    return NextResponse.next();
  }

  // 3. Rota protegida sem autenticação → /login
  if (eRotaProtegida(raiz) && !autenticado) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // 4. Rota protegida do perfil correto → deixa passar
  if (eRotaProtegida(raiz) && autenticado && eRotaDoGrupo(raiz, perfil)) {
    return NextResponse.next();
  }

  // 5. Rota protegida do perfil errado → home do próprio perfil
  if (eRotaProtegida(raiz) && autenticado && !eRotaDoGrupo(raiz, perfil)) {
    const home = HOME_POR_PERFIL[perfil as TipoUsuario] ?? '/login';
    return NextResponse.redirect(new URL(home, request.url));
  }

  // 6. Rota desconhecida + autenticado → home do perfil
  if (autenticado) {
    const home = HOME_POR_PERFIL[perfil as TipoUsuario] ?? '/login';
    return NextResponse.redirect(new URL(home, request.url));
  }

  // 7. Rota desconhecida sem autenticação → /login
  return NextResponse.redirect(new URL('/login', request.url));
}

// ---------------------------------------------------------------------------
// Matcher: exclui assets estáticos, imagens e _next internals
// ---------------------------------------------------------------------------

export const config = {
  matcher: [
    /*
     * Intercepta todos os caminhos EXCETO:
     *   - api            (rewrite para o backend — ver next.config.mjs; a
     *                      autorizacao real e do JWT/RN12, o proxy nao deve
     *                      redirecionar chamadas de API para /login)
     *   - _next/static  (bundle JS/CSS gerado)
     *   - _next/image   (otimizador de imagens)
     *   - favicon.ico
     *   - qualquer arquivo com extensão (ex.: .png, .svg, .woff2)
     */
    '/((?!api/|_next/static|_next/image|favicon\\.ico|.*\\..*).*)',
  ],
};
