# Online Demo TDD Evidence

## User journey

As an HR visitor, I want to open Memex AI without configuring an API key or database, so that I can quickly understand and experience the product.

## RED

- Test file: `frontend/test/demo-api.test.js`
- Command: `node --test test/demo-api.test.js`
- Result: failed because `frontend/src/api/demo.js` did not exist yet.
- Checkpoint: `2ceb46b test: add online demo data contracts`

## GREEN

- Implemented `frontend/src/api/demo.js` and `VITE_DEMO_MODE` branches in `frontend/src/api/index.js`.
- Demo mode now covers knowledge answers with sources, weekly report content, document additions, and profile updates.
- Command: `npm test`
- Result: 3 tests passed, 0 failed.
- Command: `npm run build -- --outDir .tmp-build`
- Result: production build passed.
- Command: `VITE_DEMO_MODE=true npm run build -- --base=/memex-ai/`
- Result: public demo build passed.

## Guarantees

| # | Guarantee | Test | Result |
|---|---|---|---|
| 1 | Knowledge questions return a relevant answer and a cited source. | `frontend/test/demo-api.test.js` | PASS |
| 2 | Weekly report questions expose a Markdown report for download. | `frontend/test/demo-api.test.js` | PASS |
| 3 | Demo visitors can add documents and save/delete personal context. | `frontend/test/demo-api.test.js` | PASS |
| 4 | The real frontend still produces a production build without demo mode. | `npm run build -- --outDir .tmp-build` | PASS |
| 5 | The public `/memex-ai/` bundle builds with the correct base path. | `VITE_DEMO_MODE=true npm run build -- --base=/memex-ai/` | PASS |

## Known gaps

- The public mode is intentionally demo data only; it does not connect to DeepSeek, PostgreSQL, ChromaDB, or the local filesystem.
- Browser screenshot/E2E coverage was not available because the Playwright Chrome extension is not installed in this environment.
- No coverage runner is configured in the existing frontend package; the current tests are fast Node unit tests.
