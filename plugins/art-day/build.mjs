import {build} from 'esbuild';import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
mkdirSync('dist',{recursive:true});
await build({entryPoints:['src/server.mjs','src/cli.mjs'],outdir:'dist',outExtension:{'.js':'.mjs'},bundle:true,platform:'node',format:'esm',packages:'bundle',banner:{js:"import {createRequire as __createRequire} from 'node:module'; const require=__createRequire(import.meta.url);"}});
const ui=await build({entryPoints:['src/ui.js'],bundle:true,platform:'browser',format:'iife',write:false});
writeFileSync('dist/gallery.html',readFileSync('src/gallery.html','utf8').replace('/*APP*/',()=>ui.outputFiles[0].text.replaceAll('</script','<\\/script')));
