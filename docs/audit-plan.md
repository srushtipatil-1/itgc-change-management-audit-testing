# Audit Plan — ITGC Change-Management Control Testing

| Item | Detail |
| --- | --- |
| Prepared by | Srushti Patil |
| Version | 1.0 |
| Status | Draft — approved for fieldwork |
| Engagement type | Independent portfolio project using public data (not an audit engagement) |

## 1. Objective
Evaluate whether a change-management control operated effectively over a defined period, using real change records from public open-source GitHub repositories, and document the work the way an IT audit team would.

## 2. Control under test

| Field | Detail |
| --- | --- |
| Control ID | CM-01 |
| ITGC domain | Program changes (change management) |
| Control statement | Every change merged into the default branch is made through a pull request, reviewed and approved by a person other than the author, and passes automated checks before merge. |
| Control type | Preventive; automated (branch protection) with a manual review element |
| Frequency | Multiple times per day (each change) |
| Framework references | SOC 2 CC8.1; ISO/IEC 27001:2022 A.8.32 (change management) and A.5.3 (segregation of duties) |

## 3. Scope
- Repositories: 2–3 public open-source repositories (selection criteria in section 9).
- Branch: each repository's default branch.
- Audit period: 1 July 2026 to 30 September 2026.

## 4. Population definition
All commits that landed on the default branch during the audit period, including commits from merged pull requests and any direct pushes.

## 5. Test attributes

| ID | Attribute | Evidence source |
| --- | --- | --- |
| A1 | Change entered the default branch through a pull request (no direct push) | Commit to pull-request association (GitHub API) |
| A2 | Pull request had at least one approving review before merge | Review records and merge timestamp |
| A3 | Approver is not the author (segregation of duties) | Review author vs pull-request author |
| A4 | Automated checks passed on the merged commit | Check runs / commit status |
| A5 | Approval covers the final version (no unreviewed commits pushed after approval) | Commit timestamps vs approval timestamp |

## 6. Sampling approach
1. Manual sample: a random sample of 25 changes per repository, selected with a recorded random seed so the selection can be reproduced.
2. Full-population test: a script tests 100% of the population on the same attributes.
3. Comparison: results of the manual sample and the automated test are reconciled; any differences are investigated.

## 7. Exception handling
Each failed attribute is recorded and classified as one of:
- Control exception — the control did not operate as defined.
- Explained deviation — for example, an automated bot change or a documented emergency change; reasoning recorded.
- Data limitation — the public data cannot show whether the control operated.

Exceptions are assessed for root cause and potential impact before a conclusion is reached.

## 8. Conclusion criteria
- Effective: no control exceptions in the sample.
- Effective with exceptions: isolated exceptions with an identified root cause and low impact.
- Not effective: repeated or systemic exceptions.

## 9. Repository selection criteria
- Public, actively maintained, at least 50 merged changes in the audit period.
- Uses GitHub pull-request reviews for approval.
- Repositories with different practices are chosen so results can be compared.

## 10. Limitations and ethics
- Only public data is used; no private systems are accessed.
- The repositories' maintainers are not bound by control CM-01. Results describe how their public change records compare with an illustrative control. They are not findings of non-compliance.
- Branch-protection settings and administrator bypasses are not fully visible through public data; this is recorded as a data limitation where relevant.

## 11. Deliverables
Audit plan (this document), population extracts, sample selection, test workpaper, exceptions log, management letter, and a summary of results.
