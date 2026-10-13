# Management Letter — Change-Management Control Review

> **Illustrative letter.** Prepared as part of an independent portfolio project using public data. It has not been sent to, reviewed by, or endorsed by the maintainers of the projects named. The projects are not bound by control CM-01; observations compare their public change records with an illustrative control and are not findings of non-compliance.

| | |
| --- | --- |
| **To** | Maintainers, prowler-cloud/prowler and aquasecurity/trivy (illustrative addressees) |
| **From** | Srushti Patil, Independent Reviewer |
| **Date** | 13 October 2026 |
| **Subject** | Observations and recommendations — change-management control, Q3 2026 |

## 1. Introduction

We performed a review of the change-management process for two open-source security tools over the period 1 July to 30 September 2026. We tested all 867 changes merged during the period against control CM-01: changes are made through a pull request, approved by an independent human reviewer before merge, pass blocking automated checks, and are not modified after approval. The detailed approach is described in the audit plan, scoping memo and decisions log.

This letter summarises our observations, the associated risks and our recommendations. It does not express an audit opinion.

## 2. Summary

| Ref | Repository | Observation | Rating |
| --- | --- | --- | --- |
| 1 | Prowler | Changes merged without any approval, concentrated in release branches | High |
| 2 | Prowler | Bot approvals, including an AI review tool, accepted in place of human review | High |
| 3 | Prowler | Changes merged while blocking checks were failing | Medium |
| 4 | Trivy | Changes modified after approval without re-approval | Medium |

**Positive observations.** Trivy required an independent human approval for 100% of changes tested, including all 32 bot-authored dependency updates. Its use of code-owner review requests and a merge queue provides strong preventive control. Neither repository showed duplicate or out-of-period records, and the populations reconciled to source.

## 3. Detailed observations

### Observation 1 — Changes merged without approval (Prowler) — High

**Observation.** 95 of 734 changes (12.9%) were merged with no approving review. The rate was markedly higher on release branches: 65 of 181 release-branch changes (35.9%), compared with 30 of 553 default-branch changes (5.4%). Example: PR #11806, an automated dependency update for release 5.32.0, was merged into branch v5.32 with no reviews recorded, although 47 automated checks passed.

**Criteria.** Control CM-01; SOC 2 CC8.1 (changes are authorised before implementation); ISO/IEC 27001:2022 A.8.32 (change management).

**Risk.** Unreviewed changes may introduce errors or malicious code. Release branches are distributed directly to users, so a weakness there has the greatest potential impact — including on organisations that run the tool against their own cloud environments.

**Recommendation.** Apply branch-protection rules to release branches equivalent to the default branch, requiring at least one approval before merge. Where release automation must merge without review, document the exception, limit it to defined change types, and monitor it.

**Management response.** Not obtained (illustrative). *Suggested owner:* release engineering lead. *Suggested target:* next release cycle.

### Observation 2 — Bot approvals accepted in place of human review (Prowler) — High

**Observation.** 89 changes (12.1%) were approved only by an automated account. Example: PR #11763, which modified a CI workflow file (`.github/workflows/pr-conflict-checker.yml`), was approved only by coderabbitai[bot], an AI code-review tool, and was then merged by its author.

**Criteria.** Control CM-01 (independent human approval); ISO/IEC 27001:2022 A.5.3 (segregation of duties); decisions D-03 and D-06.

**Risk.** An automated reviewer cannot be held accountable for an approval, and the author effectively approved their own change. Changes to CI workflows are particularly sensitive because they control how software is built and tested.

**Recommendation.** Configure AI review tools to comment rather than approve, and require approval from a human code owner — at minimum for changes to CI/CD workflows and release configuration.

**Management response.** Not obtained (illustrative). *Suggested owner:* repository administrators. *Suggested target:* 30 days.

### Observation 3 — Merges with failing blocking checks (Prowler) — Medium

**Observation.** 174 changes (23.7%) were merged while at least one blocking check was failing on the final commit, such as end-to-end tests, SDK tests or container build-and-scan. Informational checks (coverage, changelog and title-format checks) were excluded from this count (decision D-07).

**Criteria.** Control CM-01 (changes pass blocking automated checks before merge); SOC 2 CC8.1 (changes are tested before implementation).

**Risk.** Defects or vulnerabilities detected by automated tests may reach users.

**Recommendation.** Define which checks are required, enforce them through branch protection, and document any override with a reason.

**Note.** Public data does not show which checks are configured as required. All checks not classified as informational were treated as blocking, so this figure may be overstated.

**Management response.** Not obtained (illustrative). *Suggested owner:* engineering lead. *Suggested target:* 60 days.

### Observation 4 — Changes modified after approval (Trivy) — Medium

**Observation.** 19 of 133 changes (14.3%) received further commits after the last approval and were merged without re-approval. Example: PR #10932 was approved on 8 July; two further commits were added before it was merged on 21 July.

**Criteria.** Control CM-01 (the approved version is the version merged); SOC 2 CC8.1.

**Risk.** Code added after review is not independently checked, which undermines the purpose of the approval.

**Recommendation.** Enable the branch-protection settings that dismiss stale approvals when new commits are pushed and require approval of the most recent push.

**Management response.** Not obtained (illustrative). *Suggested owner:* repository administrators. *Suggested target:* 30 days.

## 4. Limitations

This review relied on public GitHub data. It could not observe branch-protection configuration, required checks or administrator bypasses, and did not include interviews with maintainers. Testing results were validated by manual re-performance of selected items.

Thank you to the open-source maintainers whose public records made this exercise possible.

*Srushti Patil*
