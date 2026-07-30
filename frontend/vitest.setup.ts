// Setup do Vitest.
//
// O import abaixo faz DUAS coisas:
//   1. registra os matchers do jest-dom em runtime (toBeInTheDocument, toHaveAttribute...)
//   2. aumenta a interface `Assertion` do Vitest com os TIPOS desses matchers
//
// O item 2 só funciona se este arquivo for TypeScript e estiver no `include` do
// tsconfig. Enquanto era `vitest.setup.mjs`, o `tsc --noEmit` falhava com
// "Property 'toBeInTheDocument' does not exist on type 'Assertion<HTMLElement>'".
import '@testing-library/jest-dom/vitest';

import { vi } from 'vitest';

// Mocks de APIs de browser que o jsdom não implementa e vários componentes
// do Mantine exigem. Fonte: https://mantine.dev/guides/vitest/
const { getComputedStyle } = window;
window.getComputedStyle = (element) => getComputedStyle(element);
window.HTMLElement.prototype.scrollIntoView = () => {};

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

if (!document.fonts) {
  Object.defineProperty(document, 'fonts', {
    writable: true,
    value: { addEventListener: vi.fn(), removeEventListener: vi.fn() },
  });
}

class ResizeObserverMock implements ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserverMock;
