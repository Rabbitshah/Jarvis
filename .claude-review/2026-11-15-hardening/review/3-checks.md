# Checks
| Check | Expected | Actual | Result |
|---|---|---|---|
| scripts/test.sh | green | 249 Python, 23 Vitest | PASS |
| Clean clone (macOS) | pytest + npm ci/test/build ok | 193 passed (before items 2-5), 17 web, build ok | PASS (items 2-5 not re-run in clean clone) |
| Probe before item 2 | show whether attack reaches app | Host/Origin evil: 200 and memory.md written; text/plain: 422 | PASS |
| Dev proxy via Vite | 404 with env, 403 without | 404 / 403 | PASS |
| jarvis --devices (real) | lists, marks selected | ok; bad name lists devices | PASS |
| curl: remember, /forget x2, evil origin | removed, nothing to undo, 403 | as expected | PASS |
| GitHub Actions run | green | cannot run here | UNVERIFIED |
| Real mic with input_device | records from chosen mic | not run | UNVERIFIED |
| Browser Undo click | button works | only Vitest | UNVERIFIED |
