# Interrupted first independent software review

Actual reviewer `/root/g05_software_audit_v1`, dispatched as
gpt-6-astra/high/fresh context, inspected exact detached snapshot
`a7768e375476667139db374dc0091999263a37de`. The user requested a quota pause
before the reviewer completed its audit. **No review verdict or acceptance
exists for this first process.** The following completed captures are preserved:

| Capture | Actual result |
|---|---|
| frozen-full.json | Exit 1; 285 passed, two failed for missing quantum references before model comparison |
| frozen-analytic.json | Exit 0; 265 passed, 22 deselected |
| strict-environment.json | Exit 0; nine environment checks passed |

`run_capture.py` records commands, exact HEAD, times, exits and full output.
`full-numerics/` retains numerical data from that full run. Test temporary
fixtures are retained in a checked archive and an external run directory as
described by `temporary-fixtures-manifest.json`; they are not scientific
acceptance evidence. The second fresh-context reviewer is separately attributed
in `../G05_v1_independent_r2/`. These results do not supply chemical or full-G05
qualification.
