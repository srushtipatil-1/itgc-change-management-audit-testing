# Audit Decisions Log — Control CM-01

Key judgements made during the engagement, with the reasoning behind each.

| ID | Date | Decision | Reasoning |
| --- | --- | --- | --- |
| D-01 | 12 Oct 2026 | Audit period set to Q3 2026 (1 July – 30 September) | Most recent completed quarter, so the population is final and cannot change. |
| D-02 | 12 Oct 2026 | Prowler and Trivy selected; Flask excluded | See scoping memo. Flask had only 3 merged PRs, below the minimum of 50. |
| D-03 | 12 Oct 2026 | Bot-authored changes kept in scope; each must have at least one approval from a human reviewer before merge | Automated dependency updates are a known software supply-chain attack path. Excluding them would leave a blind spot. Bot results will also be reported separately. |
| D-04 | 12 Oct 2026 | Population accepted as complete and accurate | Extraction script confirmed counts match GitHub (734 and 133), no duplicates, and all merges within the period. File fingerprints recorded in `evidence/population/extraction-log.json`. |
| D-05 | 13 Oct 2026 | Scope extended to include merges into release branches (e.g. v5.32), not only the default branch | Found during testing (PR #11806). Release branches ship directly to users, so their changes are higher risk. Results will show default-branch and release-branch changes separately. |
| D-06 | 13 Oct 2026 | Approvals by AI review bots (e.g. coderabbitai[bot]) do not satisfy A3 | Consistent with D-03: an accountable human reviewer is required. AI review is treated as a supporting control, not an approval. |
| D-07 | 13 Oct 2026 | A4 refined: only blocking checks count as failures. Informational checks (coverage reports, changelog reminders, PR title format, labelling) are excluded; cancelled runs are not counted as failures | The first run flagged 76% of Prowler changes, mostly due to informational checks that do not test functionality or security. Any check not explicitly classified as informational is treated as blocking (conservative approach). Raw results are retained alongside refined results. |
| D-08 | 13 Oct 2026 | (1) Testing approach changed from a 25-item manual sample per repository to 100% automated testing, validated by manual re-performance of 4 items. (2) Release-branch results corrected: branches named v* are release branches; other non-default branches (35 changes) are feature/integration branches and reported separately. | (1) Full-population testing finds every exception instead of estimating. (2) Found on review: the first version grouped all non-default branches as release branches, which overstated the release-branch rate (35.9% corrected to 23.3%). |

## Population summary

| Repository | Total merged changes | Human-authored | Bot-authored |
| --- | --- | --- | --- |
| prowler-cloud/prowler | 734 | 715 | 19 |
| aquasecurity/trivy | 133 | 101 | 32 |
| **Total** | **867** | **816** | **51** |

## Items to follow up during testing

| Ref | Repository | Item | Why it matters |
| --- | --- | --- | --- |
| F-01 | Prowler | Some merged PRs show "Changes requested" or "Review required" in the PR list (e.g. #12915, #12914, #12911) | May indicate merges without a valid approval |
| F-02 | Trivy | PR #10912 changes who may approve Chart.yaml updates | A change to the approval rules is itself a high-risk change and needs strong review |
| F-03 | Trivy | PR #10931 refers to bypassing the merge queue rule | Any bypass of a control needs a documented justification |
| F-04 | Trivy | Some PRs were authored and merged by the same person (e.g. #10970, #10974) | Acceptable only if a different person approved before merge |
