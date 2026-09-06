# Network egress reality check (run before Phase 1)

This container's outbound HTTPS goes through a policy-enforcing egress proxy. Probed
2026-09-06 with `curl -sS -o /dev/null -w '%{http_code}'` and with the WebFetch tool.

## Reachable
| host | evidence |
|---|---|
| github.com (git clone, https) | `git clone --depth 1 https://github.com/teorth/erdosproblems.git` succeeded |
| raw.githubusercontent.com | `curl` -> http 200, 7109 bytes |
| pypi.org / files.pythonhosted.org | `pip install sympy` succeeded (in proxy `noProxy` list) |
| Ubuntu archive (apt) | `apt-get install z3 nauty` succeeded |
| WebSearch tool (Anthropic-side) | returns results for arbitrary queries |

## Blocked (CONNECT tunnel failed / EGRESS_BLOCKED)
| host | how it failed |
|---|---|
| www.erdosproblems.com | curl 403 CONNECT; WebFetch `EGRESS_BLOCKED` |
| export.arxiv.org, arxiv.org | curl 403 CONNECT |
| en.wikipedia.org | WebFetch `EGRESS_BLOCKED` |
| oeis.org | curl 403 CONNECT |
| www.openproblemgarden.org | curl 403 CONNECT |
| houseofgraphs.org | curl 403 CONNECT |
| users.cecs.anu.edu.au (Radziszowski/McKay data) | WebFetch `EGRESS_BLOCKED` |
| neilsloane.com, mathworld.wolfram.com, combinatorics.org | curl 403 CONNECT |

## Consequence for the harvest plan
Primary-source scraping of the canonical open-problem sites is impossible in this
container. The harvest is therefore **GitHub-mirror-first**: every cluster must ground
its entries in a file inside a repository we can clone (path + commit recorded), or in a
WebSearch result snippet whose URL is recorded. Anything that comes from model memory
alone is recorded with `"provenance": "model-knowledge-unverified"` and is **excluded
from the attack pool** unless it is independently reconstructible from a cloned file.
Per MISSION §8: sources unreachable -> shrink target, say so, keep going, never fabricate.

## Lean/T3 reachability (probed after the harvest launched)
| host | result |
|---|---|
| `releases.lean-lang.org` (elan's default toolchain source) | 403 CONNECT — `elan toolchain install` fails outright |
| `lakecache.blob.core.windows.net`, `mathlib4.blob.core.windows.net` | 403 CONNECT — **`lake exe cache get` is unavailable, mathlib oleans cannot be downloaded** |
| `reservoir.lean-lang.org`, `leanprover-community.github.io` | 403 CONNECT |
| `github.com/leanprover/lean4/releases/download/...` | **200/206 — release assets ARE reachable** |

Workaround used: elan was installed from `raw.githubusercontent.com`, then the toolchain
tarball was fetched directly from the GitHub release and unpacked into
`~/.elan/toolchains/leanprover--lean4---v4.34.0-rc2`, and `elan default` pointed at it.
`lean --version` -> 4.34.0-rc2; a hello-world compiles. So **core Lean 4 is available**.

mathlib is a separate question: its source clones fine from GitHub but its compiled-olean
cache is behind a blocked host, so mathlib must be **built from source** on 4 cores if it
is to be used at all. Attempted in the background at low priority; the report records
whether it finished and what T3 therefore looks like.
