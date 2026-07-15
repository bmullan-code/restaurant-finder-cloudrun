// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import {test, expect} from 'vitest';

/**
 * Smoke test to ensure that the Vite dev server compilation pipeline correctly
 * transpiles Lit decorators. In Vite 8, a target compilation bug can cause
 * esbuild to serve uncompiled Stage-3 class decorators raw to the browser,
 * resulting in runtime SyntaxErrors.
 */
test('a2ui-shell compiles and registers without syntax errors', async () => {
  const mod = await import('../app.js');
  expect(mod.A2UILayoutEditor).toBeDefined();
  expect(customElements.get('a2ui-shell')).toBeDefined();
});

test('a2ui-shell toggles the A2UI JSON split view', async () => {
  await import('../app.js');
  Object.defineProperty(document, 'adoptedStyleSheets', {
    configurable: true,
    value: [],
    writable: true,
  });
  const element = document.createElement('a2ui-shell') as HTMLElement & {
    updateComplete: Promise<boolean>;
  };
  document.body.append(element);
  await element.updateComplete;

  const toggle = element.shadowRoot?.querySelector<HTMLInputElement>('.json-toggle input');
  expect(toggle).toBeDefined();
  expect(element.shadowRoot?.querySelector('.workspace')?.classList.contains('split')).toBe(false);

  toggle?.click();
  await element.updateComplete;

  expect(element.shadowRoot?.querySelector('.workspace')?.classList.contains('split')).toBe(true);
  expect(element.shadowRoot?.querySelector('.json-inspector')).not.toBeNull();
  expect(element.shadowRoot?.querySelector('.json-empty')?.textContent).toContain(
    'Send a request to see the A2UI JSON',
  );

  (element as unknown as {_lastMessages: unknown[]})._lastMessages = [
    {
      version: 'v0.9.1',
      createSurface: {surfaceId: 'main'},
    },
  ];
  await element.updateComplete;

  expect(element.shadowRoot?.querySelector('.segment-count')?.textContent).toContain('1 segment');
  expect(element.shadowRoot?.querySelector('.json-segment code')?.textContent).toContain(
    '"createSurface": {\n    "surfaceId": "main"',
  );

  element.remove();
});
