# External Access Retirement Policy

Status: `APPROVED / PERMANENT`

Date: 2026-07-03

Active branch: `docs/algorithm-audit`

Base branch: `feature/product-p1-release-candidate`

## 1. Decision

External-site access and external-institution contact are permanently removed from the active algorithm-development path.

The following activities are prohibited:

1. GitHub Actions access to lottery-result websites;
2. retrying an external-access workflow after failure or timeout;
3. contacting the lottery operator, broadcaster, manufacturer or other institution about ball size, humidity, equipment specifications or operational records;
4. treating an external-site response as a prerequisite for product or algorithm development;
5. repeated contact or access attempts to satisfy Product Gate P2 B2 through B5;
6. continued discovery of new official or unofficial data sources;
7. collecting physical variables that were not supplied by the user.

## 2. Repository treatment

Draft PR #45 is closed without merge.

Its branch, workflow runs, reports, hashes and locks are historical evidence. They must not be deleted, rewritten or represented as active development requirements.

No P2 external-access workflow is merged into `feature/product-p1-release-candidate` or `main`.

## 3. Active inputs

Future algorithm work may use only:

- the historical winning-number dataset already present in the repository;
- mathematical and statistical models already developed in the repository;
- physical-variable values explicitly supplied by the user;
- the user's stated hypotheses and decision framework;
- deterministic synthetic controls required to test implementation correctness.

Synthetic controls may verify code behavior but may not be presented as real-world predictive evidence.

## 4. Non-blocking status

External source availability, official reconciliation, B2 through B5 and institutional replies are no longer blocking conditions for algorithm research or product development.

This decision does not change or delete the historical `P2_QA_BLOCKED` evidence. It removes that external-access path from future work.

## 5. Next boundary

The next permitted activity is specification-only analysis of how to improve the already developed algorithm. Implementation, Walk-forward evaluation, HTML, CAL, SEALED, mobile work and `main` merge require separate user approval.
