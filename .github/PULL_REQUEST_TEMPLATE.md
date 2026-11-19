## Summary

<!-- 2-3 sentence overview of what was built and why. -->

## Changes Made

<!-- Bulleted list of all files added or modified, and the reason for each. -->

## Test Evidence

<!-- Paste the test run output or link to CI results. -->

## Known Limitations

<!-- Anything marked Not Found, or explicitly out of scope. -->

## Reviewer Checklist

- [ ] Correctness — Does each component behave as specified in .cursor/artifacts/requirements-agent/requirements.md?
- [ ] Security — Are secrets excluded from output? Is user input validated?
- [ ] Error Handling — Are bad input, a missing hold, and an empty overdue list handled gracefully?
- [ ] Test Coverage — Do tests cover the happy path AND the 'Not Found' / missing-field edge cases?
- [ ] Code Clarity — Are function names self-explanatory? Is logic easy to follow without comments?
- [ ] DRY Principle — Is there duplicated logic that could be refactored into a shared function?
- [ ] Dependency Safety — Are any known-vulnerable package versions in use?
