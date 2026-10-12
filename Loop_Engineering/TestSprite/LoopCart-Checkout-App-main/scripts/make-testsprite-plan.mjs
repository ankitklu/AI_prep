import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const projectId = process.argv[2];

if (!projectId || !projectId.startsWith('proj_')) {
  console.error('Usage: npm run testsprite:plan -- proj_your_project_id');
  process.exit(1);
}

const plan = {
  projectId,
  type: 'frontend',
  name: 'SAVE20 applies the promised 20 percent discount',
  planSteps: [
    {
      type: 'action',
      description: 'Open the LoopCart home page and confirm the cart subtotal is $100.00.',
    },
    {
      type: 'action',
      description: 'Enter SAVE20 in the Coupon code field and click Apply coupon.',
    },
    {
      type: 'assertion',
      description: 'Verify the page confirms that coupon SAVE20 was applied.',
    },
    {
      type: 'assertion',
      description: 'Verify the Discount value is -$20.00.',
    },
    {
      type: 'assertion',
      description: 'Verify Shipping is Free and the final Total is $80.00.',
    },
  ],
};

const outputDir = path.resolve('testsprite-plans');
const outputPath = path.join(outputDir, 'save20-discount.plan.json');
await mkdir(outputDir, { recursive: true });
await writeFile(outputPath, `${JSON.stringify(plan, null, 2)}\n`, 'utf8');
console.log(`Created ${outputPath}`);
