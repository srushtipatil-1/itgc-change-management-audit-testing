# Exception Analysis — Control CM-01

Automated testing of 867 merged changes (Q3 2026) flagged 578 changes for analysis. This document records how exceptions were investigated before any conclusion was drawn.

## 1. Overview of raw results

| Repository | Tested | Pass | Flagged for analysis |
| --- | --- | --- | --- |
| aquasecurity/trivy | 133 | 112 | 21 |
| prowler-cloud/prowler | 734 | 177 | 557 |

Prowler's raw exception rate (76%) was judged implausible for an actively maintained project, so the results were analysed by pattern before conclusion (see `evidence/testing/exception-analysis.txt`).

## 2. Patterns identified

| Repository | Pattern | Count | Initial assessment |
| --- | --- | --- | --- |
| Trivy | A5 only (code changed after approval) | 19 | Potential control exception |
| Trivy | A4 only ("Validate PR title" failed) | 2 | Informational check; low risk |
| Prowler | A4 only (approval valid, a check failed) | 372 | Mostly informational checks (coverage, changelog, title format); requires check classification |
| Prowler | No approval before merge (A2) | 95 | Potential control exception |
| Prowler | Approved only by author or bot (A3) | 89 | Potential segregation-of-duties exception |

## 3. Root-cause investigation of selected exceptions

| PR | Pattern | Evidence observed | Root cause | Classification |
| --- | --- | --- | --- | --- |
| prowler #11763 | A3+A5 | Only approval by coderabbitai[bot] (AI review tool); author merged own change; change modified a CI workflow file; 38 checks passed | AI bot approval accepted in place of human review | Control exception — segregation of duties |
| prowler #11806 | A2+A3+A5 | Authored by prowler-bot; no reviews; merged by a maintainer into release branch v5.32; 3-line dependency update; 47 checks passed | Release automation merged without recorded approval | Control exception — lower risk (automated tests passed; small change) |
| trivy #10932 | A5 | Approved by knqyf263 on 8 Jul; author added 2 commits afterwards; merged 21 Jul without re-approval | Stale approvals not dismissed when new commits are pushed | Control exception — post-approval change |

## 4. Validation of the automated test

For every item reviewed manually (PR 10307, 11763, 11806, 10932), the manual result agreed with the script's result (4 of 4).

## 5. Next steps

- Classify failing checks as blocking (functional tests, build and security scans, release gates) or informational (coverage, changelog, title format), and re-evaluate A4.
- Report default-branch and release-branch changes separately (decision D-05).
- Complete manual re-performance of the remaining sample items.
