import { describe, expect, it } from 'vitest';

import { render, screen } from '@test-utils';

import HomePage from '@/app/page';

describe('HomePage', () => {
  it('renderiza o titulo do MVP', () => {
    render(<HomePage />);
    expect(screen.getByRole('heading', { level: 1, name: /Clínica Médica/i })).toBeInTheDocument();
  });

  it('anuncia as rotas da US-00', () => {
    render(<HomePage />);
    expect(screen.getByText('/login')).toBeInTheDocument();
    expect(screen.getByText('/primeiro-acesso')).toBeInTheDocument();
  });
});
