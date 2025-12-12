// courtesy of livewire
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import brotliSize from 'brotli-size';
import crypto from 'crypto';
import esbuild from 'esbuild';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Output to dist directory
const outDir = `dist/cotton-ui`;

build({
    entryPoints: [`js/cotton-ui.js`],
    outfile: `${outDir}/cotton-ui.js`,
    bundle: true,
    platform: 'browser',
    define: { CDN: true },
})

// CSS is built by Tailwind CLI, not esbuild
// build({
//     entryPoints: [`css/cotton-ui.css`],
//     outfile: `${outDir}/cotton-ui.css`,
//     bundle: true,
//     platform: 'browser',
//     define: { CDN: true },
// })

build({
    format: 'esm',
    entryPoints: [`js/cotton-ui.js`],
    outfile: `${outDir}/cotton-ui.esm.js`,
    bundle: true,
    platform: 'node',
    define: { CDN: true },
})

// build({
//     format: 'esm',
//     entryPoints: [`css/cotton-ui.css`],
//     outfile: `${outDir}/cotton-ui.esm.css`,
//     bundle: true,
//     platform: 'node',
//     define: { CDN: true },
// })

let jsHash = crypto.randomBytes(4).toString('hex');
let cssHash = crypto.randomBytes(4).toString('hex');

fs.writeFileSync(`${outDir}/manifest.json`, `
{"/cotton-ui.js":"${jsHash}", "/cotton-ui.css":"${cssHash}"}
`)

// Build a minified version.
build({
    entryPoints: [`js/cotton-ui.js`],
    outfile: `${outDir}/cotton-ui.min.js`,
    sourcemap: 'linked',
    bundle: true,
    minify: true,
    platform: 'browser',
    define: { CDN: true },
}).then(() => {
    outputSize(`${outDir}/cotton-ui.min.js`)
})


// build({
//     entryPoints: [`css/cotton-ui.css`],
//     outfile: `${outDir}/cotton-ui.min.css`,
//     sourcemap: 'linked',
//     bundle: true,
//     minify: true,
//     platform: 'browser',
//     define: { CDN: true },
// }).then(() => {
//     outputSize(`${outDir}/cotton-ui.min.css`)
// })

function build(options) {
    options.define || (options.define = {})

    // options.define['LIVEWIRE_VERSION'] = `'${getFromPackageDotJson('alpinejs', 'version')}'`
    options.define['process.env.NODE_ENV'] = process.argv.includes('--watch') ? `'production'` : `'development'`

    return esbuild.build({
        watch: process.argv.includes('--watch'),
        // external: ['alpinejs'],
        ...options,
    }).catch(() => process.exit(1))
}
function outputSize(file) {
    let size = bytesToSize(brotliSize.sync(fs.readFileSync(file)))

    console.log("\x1b[32m", `Bundle size: ${size}`)
}

function bytesToSize(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    if (bytes === 0) return 'n/a'
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)), 10)
    if (i === 0) return `${bytes} ${sizes[i]}`
    return `${(bytes / (1024 ** i)).toFixed(1)} ${sizes[i]}`
  }
