# LoopCart — TestSprite Loop Engineering Demo

A zero-dependency JavaScript checkout app with one intentional regression:

- `SAVE20` promises 20% off.
- The starter code applies 2% off.
- The visible result is `-$2.00` and `$98.00` instead of `-$20.00` and `$80.00`.

This gives a coding agent and TestSprite a clean closed-loop story:

`build → verify live app → inspect failure bundle → fix → deploy → rerun`

## Run locally

```bash
npm run dev
```

Open `http://localhost:5173`.

## Build

```bash
npm run build
```

## Deploy to Vercel

```bash
npx vercel --prod
```

Use the stable production URL when creating the TestSprite frontend project.

## Generate the TestSprite plan

After creating a TestSprite project, copy its `proj_...` ID and run:

```bash
npm run testsprite:plan -- proj_your_project_id
```

The generated file is `testsprite-plans/save20-discount.plan.json`.

## Presenter note

The manual solution is documented in `FIX_REFERENCE.md`, but the video is stronger when the coding agent finds it from TestSprite's failure bundle.




testsprite project create --type frontend --name "LoopCart proj" --url https://loopcart-testsprite-demo.vercel.app/



21b253bb-5cfd-49a9-8e98-63edadf2b8d7



npm run testsprite:plan -- proj_21b253bb-5cfd-49a9-8e98-63edadf2b8d7



testsprite test create --plan-from ./testsprite-plans/save20-discount.plan.json --run --wait --output json


4e2bd943-6977-4f34-8bd7-c6ba243a8adc




testsprite test failure get 4e2bd943-6977-4f34-8bd7-c6ba243a8adc --out .\.testsprite\failure



testsprite test rerun 4e2bd943-6977-4f34-8bd7-c6ba243a8adc --wait --output json