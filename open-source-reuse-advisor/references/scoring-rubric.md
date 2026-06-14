# Scoring Rubric

Use this file when ranking candidates or writing a formal comparison.

## Similarity Score

Score each candidate from 0 to 100:

- 35 points: Core feature overlap
- 15 points: Matching platform, language, framework, or deployment model
- 15 points: Extensibility and forkability
- 10 points: Maintenance health
- 10 points: Documentation and examples
- 10 points: License fit
- 5 points: Ecosystem fit, package availability, or integrations

Suggested bands:

- 85-100: Very close; likely reuse or fork first
- 70-84: Strong partial match; good candidate for adaptation
- 50-69: Useful reference or component, but not a full solution
- 30-49: Shares domain vocabulary, limited practical overlap
- 0-29: Not meaningfully related

## Maintenance Signals

Use current metadata when possible:

- Last push or release within 12 months: positive
- Active issue/PR handling: positive
- Clear releases, changelog, tests, examples: positive
- Archived repository, no license, abandoned dependencies: negative
- Single-maintainer projects are not bad by default, but mention continuity risk

## License Notes

Keep license advice concise and non-legal:

- MIT/BSD/Apache-2.0: usually easier for reuse; Apache-2.0 includes explicit patent license.
- GPL/LGPL/MPL: check distribution and linking obligations.
- AGPL: high caution for network services.
- No license: do not assume reuse rights.
- Custom/commercial license: inspect terms before using.

## Final Decision Matrix

Use a compact table when there are 3 or more candidates:

| 项目 | 重合度 | 主要相同点 | 主要缺口 | License | 活跃度 | 建议 |
| --- | ---: | --- | --- | --- | --- | --- |

Follow the table with a short decision paragraph:

1. If the user's goal is speed, recommend the easiest path.
2. If the user's goal is control or differentiation, recommend fork or architecture borrowing.
3. If license risk dominates, explicitly separate technical fit from legal fit.
4. If search coverage is weak, name the blind spots and suggest the next search expansion.
