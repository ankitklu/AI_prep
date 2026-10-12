# Prompts to use during the recording

## Ask the agent to run the whole verification loop

> Use TestSprite to verify the SAVE20 checkout requirement in this project. Run the existing TestSprite plan, inspect the complete failure bundle if it fails, identify the root cause, fix only the relevant code, deploy the updated app to production, and rerun the same test until it passes. Do not weaken or change the requirement.

## Controlled version after downloading the failure bundle

> Read every artifact in `.testsprite/failure`. Explain the failed user-visible behavior and its most likely code-level cause. Fix the smallest relevant part of the application without changing the test expectation. Then run `npm run build` and show me the exact change.
