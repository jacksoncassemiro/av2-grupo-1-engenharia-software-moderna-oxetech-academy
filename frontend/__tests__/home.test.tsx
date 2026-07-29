import { describe, expect, it } from 'vitest';

import { render, screen } from '@test-utils';

import HomePage from '@/app/page';

describe('HomePage', () => {
  it('renderiza o titulo do MVP', () => {
    render(<HomePage />);
    expect(screen.getByRole('heading', { level: 1, name: /Clinica Medica/i })).toBeInTheDocument();
  });

  it('oferece os dois pontos de entrada da US-00', () => {
    render(<HomePage />);
    expect(screen.getByRole('link', { name: '/login' })).toHaveAttribute('href', '/login');
    expect(screen.getByRole('link', { name: '/primeiro-acesso' })).toHaveAttribute(
      'href',
      '/primeiro-acesso'
    );
  });
});
