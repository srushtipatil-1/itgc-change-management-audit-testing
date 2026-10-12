# Scoping Memo — ITGC Change-Management Control Testing

| Item | Detail |
| --- | --- |
| Prepared by | Srushti Patil |
| Date | 12 October 2026 |
| Control under test | CM-01 (see audit plan) |
| Audit period | 1 July 2026 to 30 September 2026 |

## 1. Purpose
Record which repositories were selected for testing, which were excluded, and why, against the selection criteria in section 9 of the audit plan.

## 2. Selection criteria
1. Public and actively maintained.
2. At least 50 merged pull requests in the audit period.
3. Uses GitHub pull-request reviews for approval.
4. Repositories with different scale or practices, so results can be compared.

## 3. Candidates assessed

| Repository | What it is | Merged PRs in audit period | Decision | Reason |
| --- | --- | --- | --- | --- |
| prowler-cloud/prowler | Open-source cloud security and compliance scanner | 734 | Selected | Meets all criteria; large, fast-moving codebase |
| aquasecurity/trivy | Open-source vulnerability scanner | 133 | Selected | Meets all criteria; smaller codebase for comparison |
| pallets/flask | Python web framework | 3 | Excluded | Below the minimum of 50 merged PRs; population too small for a reliable conclusion |

Counts were taken on 12 October 2026 using the GitHub search `is:pr is:merged merged:2026-07-01..2026-09-30`.

## 4. Business relevance
Both selected repositories are security tools used by many organisations. A weakness in their change control could allow an unreviewed or malicious change to reach every organisation that runs them. This makes change management a high-risk control for these projects and links the test to software supply-chain risk.

## 5. Walkthrough (design check)
Before testing, one change per repository was inspected to confirm the control exists.

| Repository | Pull request | Author | Approvers | Observation |
| --- | --- | --- | --- | --- |
| aquasecurity/trivy | #11319 | nikpivkin | knqyf263, DmitriyLewen | Reviews requested from code owners; two approvals; reviewer left substantive technical comments |
| prowler-cloud/prowler | #12913 | prowler-bot | Shown as "Approved" in the PR list | Approval status visible; author is an automated account |

Conclusion: a review-and-approval process is designed and in use in both repositories. Operating effectiveness is tested in the next phase.

## 6. Early observations to follow up
- Prowler's PR list shows some merged changes marked "Changes requested" or "Review required" (for example #12915, #12914, #12911). These will be examined during testing.
- Both repositories include changes authored by bots (prowler-bot, dependabot[bot]). Their treatment will be decided and documented before testing.

## 7. Limitations
Branch-protection settings and administrator bypass rights are not fully visible from public data. Results describe the public change records only and are not findings of non-compliance against the projects' own policies.
