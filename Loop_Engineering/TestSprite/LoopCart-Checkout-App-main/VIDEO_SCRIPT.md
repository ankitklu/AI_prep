# Ready-to-Record Video Script

## Suggested title
**Loop Engineering Explained: Make AI Coding Agents Verify and Fix Their Own Work**

## Target length
4–5 minutes

## 0:00–0:20 — Hook

**Disclosure:** Show a clear on-screen label: `Sponsored by TestSprite`.

**Visual:** On camera, then quickly show the LoopCart app with the wrong `$98.00` total.

**Script:**

Most developers are still asking, “Which model should I use?” or “How can I write a better prompt?” But when an AI coding agent can already write code, the bigger problem is different: how do you know the work is actually correct? That is where loop engineering becomes important—and the hardest part of the loop is the verifier.

**On-screen text:** `The model is not the bottleneck. The loop is.`

## 0:20–0:48 — Explain the shift

**Visual:** Simple diagram: Prompt Engineering → Context Engineering → Harness Engineering → Loop Engineering.

**Script:**

We moved from prompt engineering, to context engineering, then harness engineering, and now loop engineering. Instead of manually prompting the coding agent one turn at a time, we design a system that repeatedly acts, observes a real signal, decides what to do next, and continues until the goal condition is actually satisfied.

The important point is that TestSprite did not invent loop engineering. The idea should be attributed to the people who helped name and structure this shift, including Addy Osmani, Peter Steinberger, and Boris Cherny.

## 0:48–1:18 — The five blocks

**Visual:** Diagram with five blocks.

**Script:**

A useful coding loop normally has five blocks: a trigger, a written goal or stop condition, the agent doing the work, memory that survives across runs, and verification. Verification is the feedback gate. It is the only block that should be allowed to say, “No, this is not done yet.”

Without that gate, the agent can grade its own homework, see a few green checks, and still ship something broken for a real user.

## 1:18–1:48 — Introduce the demo bug

**Visual:** Open the deployed LoopCart app. Enter `SAVE20` and click **Apply coupon**.

**Script:**

Here is the project I will use. LoopCart is a small checkout application. The requirement is simple: this cart has a one-hundred-dollar subtotal, and the coupon SAVE20 must apply a twenty-percent discount. So the discount should be twenty dollars, and the final total should be eighty dollars.

But look at the live app. It confirms that SAVE20 was applied, yet it gives only two dollars off and shows a total of ninety-eight dollars. The interface looks fine, the button works, and the app does not crash—but the business behavior is wrong.

## 1:48–2:16 — Install TestSprite

**Visual:** Show the official TestSprite CLI GitHub repository and Apache-2.0 license, then terminal.

**Script:**

For the verifier, I am using the open-source TestSprite CLI. The important distinction is that the agent runs it against the live application like a real user. It is not just checking mocks or trusting what happened on the agent’s own machine.

I install the CLI, run setup, and then run the environment diagnostic.

**Terminal:**

```bash
npm install -g @testsprite/testsprite-cli
testsprite setup
testsprite doctor
```

## 2:16–2:48 — Create the project and test plan

**Visual:** Terminal. Replace the URL with the real deployment URL.

**Script:**

Now I create a frontend project using the public production URL. TestSprite returns a project ID. I pass that ID into the included helper script, which creates a plain-language verification plan for the SAVE20 requirement.

**Terminal:**

```bash
testsprite project create \
  --type frontend \
  --name "LoopCart Demo" \
  --url https://YOUR-LOOPCART-URL.vercel.app

npm run testsprite:plan -- proj_REPLACE_WITH_RETURNED_ID
```

**Visual:** Open `testsprite-plans/save20-discount.plan.json` and briefly highlight the assertions for `-$20.00` and `$80.00`.

**Script:**

Notice that I am not writing browser automation code. I am describing the behavior that must hold in the live product.

## 2:48–3:12 — Run and fail

**Visual:** Terminal.

**Script:**

Now the agent creates the test, runs it, and waits for the real result.

**Terminal:**

```bash
testsprite test create \
  --plan-from ./testsprite-plans/save20-discount.plan.json \
  --run \
  --wait \
  --output json
```

**Script:**

The test fails—and that is exactly what a good feedback gate should do. It refuses to accept a working-looking interface when the user-visible result is wrong.

## 3:12–3:42 — Show the failure bundle

**Visual:** Copy the returned test ID, then run:

```bash
testsprite test failure get test_REPLACE_WITH_RETURNED_ID \
  --out ./.testsprite/failure
```

Open the generated bundle in the editor. Show the failed step, screenshot or captured state, root-cause guidance, and recommended fix target available in your run.

**Script:**

This is the part that closes the loop. TestSprite gives the coding agent one failure bundle containing the evidence it needs: what step failed, what the user actually saw, the relevant artifacts, a root-cause hypothesis, and where the fix is likely needed.

It is not only saying “failed.” It is returning information the agent can act on.

## 3:42–4:12 — Let the agent fix and deploy

**Visual:** Give your coding agent this prompt:

```text
Read every artifact in .testsprite/failure. Explain the failed user-visible
behavior and its most likely code-level cause. Fix the smallest relevant part
of the application without changing or weakening the requirement. Run the
production build, deploy the updated app, and show the exact code change.
```

**Script:**

Now I hand the bundle to my coding agent. The agent traces the failure to the coupon rate in the pricing logic. SAVE20 is configured as zero-point-zero-two instead of zero-point-two-zero. It changes only that value, builds the application, and deploys the corrected version.

**Terminal, if the agent does not deploy automatically:**

```bash
npm run build
npx vercel --prod
```

## 4:12–4:34 — Rerun to green

**Visual:** Terminal, then the live app showing `-$20.00` and `$80.00`.

**Terminal:**

```bash
testsprite test rerun test_REPLACE_WITH_RETURNED_ID \
  --wait \
  --output json
```

**Script:**

I rerun the same test—not a weaker replacement. This time the live application shows a twenty-dollar discount and an eighty-dollar total, so the verifier returns a passing result. The agent did not simply write code. It received external feedback, corrected itself, and proved the goal condition on the live app.

## 4:34–4:55 — Show memory and close

**Visual:** Show run history.

```bash
testsprite test result test_REPLACE_WITH_RETURNED_ID --history
```

**Script:**

And this history becomes durable memory for the loop. The coding agent’s context window may eventually forget this feature, but the verification requirement remains available for future regression runs.

So when you design your next agent loop, do not start only with the model. Start with the block that is allowed to tell the agent, “No, not done.” For this workflow, that verifier is TestSprite. The open-source CLI is linked below.

**On-screen CTA:** `Close the loop with a real feedback gate.`
