# Acceptance Evidence

- Change ID: TODO
- Acceptance owner: TODO
- Date/build: TODO
- Overall result: PENDING

| AC ID | Result | Evidence/test report | Defect/deviation | Reviewer |
|---|---|---|---|---|
| AC-001 | Pending | TODO | TODO | TODO |

## UI acceptance

> Acceptance relies primarily on machine evidence: `design/evidence/figma-layout-check.json` must be PASS. PAGES with no differences and not `UI-DERIVED` may be batch-signed off based on machine evidence, with `Acceptance method` written as "machine evidence sign-off"; only PAGES with differences, `UI-DERIVED`, or not covered by assertions require opening the running system UI side-by-side with the real Figma file/review draft for comparison, with `Acceptance method` written as "side-by-side verification". Screenshots are neither saved nor accepted as evidence.
> Per-PAGE rows must still be complete; if any PAGE is missing sign-off or its result is not ACCEPTED/DEVIATION_APPROVED, archiving must not proceed.

| PAGE | Result | Figma node | Running system entry (URL/route) | Difference/approval | Acceptance method | Reviewer |
|---|---|---|---|---|---|---|
| PAGE-001 | ACCEPTED | `3:2` | `http://127.0.0.1:5180/login` | None | machine evidence sign-off | Design owner |

## Open blockers and risks

TODO
