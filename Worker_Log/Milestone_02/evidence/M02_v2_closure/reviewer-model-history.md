# Recorded reviewer models

Checked the canonical audit logs and all historical Markdown audit/review log
paths in Git on 2026-10-02. Recorded labels are reported as written; prior
session routing metadata is unavailable in this checkout. A generic GPT-6
label cannot establish Astra, Sol or its exact version/reasoning setting.

| Review | Reviewer and recorded model | Reasoning | Evidence |
|---|---|---|---|
| CPU environment reproduction v2, 2026-10-01 | Codex, GPT-6 family; exact served build not exposed | Not exposed | [Retired audit at its delivery commit](https://github.com/georgpou/AToM_MLMM/blob/ef6ed3ab432c443d5e1c8dad5b9211cbd9a7d925/Worker_Log/Documentation/Cloud_CPU_Reproduction_v2_audit.md) |
| M00 v1, 2026-10-01 | `/root/m00_review`; exact model label/version not exposed | Not exposed | [M00 audit](../../../Milestone_00/Milestone_00_v1_audit.md) |
| M01 v1, 2026-10-01 | `/root/m01_review_fallback`; GPT-6 family, exact runtime model/version not exposed | Not exposed | [M01 v1 audit](../../../Milestone_01/Gate_01_v1_audit.md) |
| M01 v2, 2026-10-01 | Same `/root/m01_review_fallback`; GPT-6 family, exact runtime model/version not exposed | Not exposed | [M01 v2 audit](../../../Milestone_01/Gate_01_v2_audit.md) |
| G02/G03/combined M02 v1, 2026-10-02 | One `/root/m02_independent_audit`; GPT-6 family, exact runtime backend/model version not exposed | Not exposed | [G02 v1](../../Gate_02_v1_audit.md), [G03/M02 v1](../../Gate_03_v1_audit.md) |
| G02/G03/combined M02 v2, 2026-10-02 | `/root/m02_v2_independent_audit`; explicitly configured **gpt-6-astra**, deployed backend version not exposed | **High**, explicitly configured | [G02 v2](../../Gate_02_v2_audit.md), [G03/M02 v2](../../Gate_03_v2_audit.md) |

The M01 v1 log says its earlier reviewer failed before reviewing; it records
no model-specific audit evidence for that attempt. During this M02 v2 session,
an explicitly configured `gpt-6.1-sol / high` fallback was briefly started
after an Astra usage-limit interruption. It was interrupted when the user
specified Astra high, supplied no audit decision, and contributed no acceptance
evidence. The same Astra reviewer resumed and completed the review above.

The archived supplied `cleanup-audit.md` in the documentation v2 snapshot ZIP
contains no reviewer model or reasoning metadata. Historical audit-handout and
export worker logs are documentation deliveries, not additional independent
reviews. None of these records confirms the exact configured model used in
earlier sessions; their original metadata has been preserved.
