# Software Code Review Practices

Code review serves two purposes: it catches defects before they reach production, and it spreads knowledge of the codebase across the team so no module is understood by only one person.

Review effectiveness depends strongly on change size. For an effective review, a pull request should stay under 400 lines of changed code. Beyond that size, reviewer detection of defects drops sharply because reviewers skim instead of reading carefully. Large changes are therefore split into a sequence of smaller pull requests that each make one understandable step.

Reviewers check a small set of things consistently: whether the change does what its description claims, whether tests cover the new behaviour and the obvious failure cases, whether names describe what things are, and whether the change introduces a security or data-loss risk. Style questions are deliberately left to automated formatters and linters so human attention stays on logic.

Turnaround time matters more than review depth for team flow. A team norm of a first response within one working day keeps authors unblocked, and small pull requests are the main mechanism that makes fast first responses possible.

Authors help reviewers by writing a description that explains why the change is needed, not only what changed, and by reviewing their own diff before requesting review. Self-review catches leftover debug output, accidental file changes, and missing tests before another person's time is spent.
