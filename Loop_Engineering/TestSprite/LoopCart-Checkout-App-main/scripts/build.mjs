import { cp, mkdir, rm } from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const dist = path.join(root, 'dist');

await rm(dist, { recursive: true, force: true });
await mkdir(path.join(dist, 'src'), { recursive: true });
await cp(path.join(root, 'index.html'), path.join(dist, 'index.html'));
await cp(path.join(root, 'styles.css'), path.join(dist, 'styles.css'));
await cp(path.join(root, 'src'), path.join(dist, 'src'), { recursive: true });
console.log('Built static site in dist/');
