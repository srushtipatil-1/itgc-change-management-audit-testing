# Results Summary — Control CM-01 (Change Management)

| Item | Detail |
| --- | --- |
| Prepared by | Srushti Patil |
| Audit period | 1 July 2026 – 30 September 2026 (Q3 2026) |
| Fieldwork | 12–13 October 2026 |
| Population | 867 merged changes (Prowler 734, Trivy 133) — 100% tested |
| Engagement type | Independent portfolio project using public data; not an audit engagement |

## 1. Control tested
Every change merged into a protected branch is made through a pull request, approved by an independent human reviewer before merge, passes blocking automated checks, and is not changed after approval (SOC 2 CC8.1; ISO/IEC 27001:2022 A.8.32, A.5.3).

## 2. Approach
1. Extracted the full population via the GitHub API and verified completeness (counts, duplicates, period).
2. Selected a reproducible random sample (seed 20261012) and tested items manually.
3. Tested 100% of the population with an automated script, validated against manual testing (4 of 4 items agreed).
4. Investigated exception patterns and root causes before concluding; refined the check criteria (decision D-07), which moved 306 Prowler changes from fail to pass.

## 3. Results

| Measure | Trivy | Prowler | Total |
| --- | --- | --- | --- |
| Changes tested | 133 | 734 | 867 |
| Passed all attributes | 114 (85.7%) | 438 (59.7%) | 552 (63.7%) |
| Exceptions | 19 (14.3%) | 296 (40.3%) | 315 (36.3%) |
| Merged with no approval | 0 | 95 | 95 |
| Approved only by a bot or the author | 0 | 89 | 89 |
| Merged with a blocking check failing | 0 | 174 | 174 |
| Code changed after the last approval | 19 | 1 | 20 |

Note: a change with no valid approval also fails "no change after approval"; the last row counts only changes that had a valid approval and were then modified.

### Release branches vs default branch (Prowler)

| Branch type | Changes | Exceptions | Merged with no approval |
| --- | --- | --- | --- |
| Default branch (master) | 553 | 204 (36.9%) | 30 (5.4%) |
| Release branches | 181 | 92 (50.8%) | 65 (35.9%) |

## 4. Key findings

| ID | Repository | Finding | Root cause (example) | Risk |
| --- | --- | --- | --- | --- |
| F1 | Prowler | 95 changes merged with no approval, concentrated in release branches | Release automation merged without recorded review (PR #11806) | High |
| F2 | Prowler | 89 changes approved only by a bot, including an AI review tool | AI reviewer approval accepted in place of human review (PR #11763) | High |
| F3 | Prowler | 174 changes merged while a blocking check was failing | Merges permitted despite failing functional or build checks | Medium |
| F4 | Trivy | 19 changes modified after approval without re-approval | Stale approvals not dismissed on new commits (PR #10932) | Medium |

## 5. Conclusions (against illustrative control CM-01)

| Repository | Conclusion |
| --- | --- |
| Trivy | Effective with exceptions. Independent human approval and blocking checks operated for 100% of changes, including all 32 bot-authored changes. A design deficiency allowed 19 changes to be modified after approval. |
| Prowler | Not effective. Exceptions were systemic (40.3%) across several attributes and highest in release branches, which ship directly to users. |

## 6. Limitations
- Public data does not show branch-protection settings, required checks or administrator bypasses. Checks not classified as informational were treated as blocking (conservative), so F3 may be overstated.
- The projects are not bound by control CM-01; results compare their public change records with an illustrative control and are not findings of non-compliance.
- Manual validation covered 4 items; results rely on the GitHub API's accuracy.
