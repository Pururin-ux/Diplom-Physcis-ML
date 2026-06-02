# AI-Research-SKILLs integration audit

## Purpose

AI-Research-SKILLs were integrated as agent-side research aids only. They are
not part of the scientific contribution, not a project runtime dependency, and
not evidence for any physical claim.

## Commands used

Commands were run from `C:\Users\lalad\AppData\Local\Temp` or from the project
only for status checks:

```powershell
npx --yes @orchestra-research/ai-research-skills --help
npx --yes @orchestra-research/ai-research-skills list
npx --yes @orchestra-research/ai-research-skills install --help
npx --yes @orchestra-research/ai-research-skills list
```

The first `--help` command opened the interactive UI and exited without project
changes. The `install --help` command was not treated as help by the CLI; it
performed a global install. This is documented as an installation-safety issue.

## Installed location

- Canonical location: `C:\Users\lalad\.orchestra\skills`
- Codex agent location: `C:\Users\lalad\.codex\skills`
- Additional detected agent locations were reported by the installer for Claude
  Code and Cursor.
- The project repository did not receive local skill directories such as
  `.codex/skills`, `.claude/skills`, `.cursor/skills`, or
  `.orchestra-skills.json`.

The upstream documentation says the default global install stores skills under
`~/.orchestra/skills/` and links or copies them into agent config directories;
local install is a separate `--local` mode. The local mode was not used.

## Installed categories and skills

The final `list` command reported 95 installed skills under these categories:

- `0-autoresearch-skill`
- `01-model-architecture`
- `02-tokenization`
- `03-fine-tuning`
- `04-mechanistic-interpretability`
- `05-data-processing`
- `06-post-training`
- `07-safety-alignment`
- `08-distributed-training`
- `09-infrastructure`
- `10-optimization`
- `11-evaluation`
- `12-inference-serving`
- `13-mlops`
- `14-agents`
- `15-rag`
- `16-prompt-engineering`
- `17-observability`
- `18-multimodal`
- `19-emerging-techniques`
- `20-ml-paper-writing`
- `21-research-ideation`

The installer output and repository README differ in advertised totals
(`86`, `95`, and `98` appear in different places or command outputs). The
verified post-install state is the command output: 95 installed skills.

## Relevant skills for this project now

Potentially relevant as internal aids:

- autoresearch orchestration, only for planning and review;
- research ideation, only after respecting the current negative result;
- ML paper writing and academic plotting;
- evaluation and rigor review;
- lightweight optimization guidance;
- lightweight MLOps or experiment-tracking guidance;
- RAG or literature-workflow guidance, if source attribution is checked.

## Explicitly out of scope

The following categories or skills should not guide this physics project without
separate approval:

- fine-tuning;
- distributed training;
- inference serving;
- safety-alignment frameworks;
- multimodal generation;
- CNN/GNN/neural-operator directions;
- large MLOps stacks;
- LLM-engineering workflows that distract from the computational physics
  falsification problem.

## Project repository changes

Installing the skills did not modify the project repository. After installation,
`git status --short --branch` still showed a clean
`article-inverse-screening...origin/article-inverse-screening` branch.

The only intentional project-file changes from this task are:

- `ARTICLE_AGENTS.md`
- `reports/article_inverse_screening/skills_integration_audit.md`

No thesis chapters or thesis conclusions were modified.

## Restart requirement

The upstream welcome instructions state that a restart may be needed for newly
installed skills to be recognized by the agent. The current project policy is
usable immediately as documentation, but newly installed skills may not appear
in the active skill list until the Codex session is restarted.

## Effect on the inverse-screening result

The previous negative falsification result is unchanged.

No new direct Kwant computations were run. No surrogate model was retrained.
No baseline was changed. Therefore the answer to whether the new skills change
the previous negative result is: no.

## Scientific status after integration

The skills do not change the scientific status of the project. The current
article-extension result remains a negative one-shot falsification result: the
screening objective collapses to the isotropic same-`n` baseline, and no
candidate meaningfully beats the verified isotropic baseline.

The next scientifically justified action is not to write a positive
inverse-design claim. Either report the negative result honestly or revise the
scientific question with a new pre-registered objective and then perform new
direct Kwant verification.
