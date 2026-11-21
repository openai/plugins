import test from 'node:test';import assert from 'node:assert/strict';import {mkdtempSync,rmSync} from 'node:fs';import {tmpdir} from 'node:os';import {join,resolve} from 'node:path';import {Client} from '@modelcontextprotocol/sdk/client/index.js';import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
test('bundled MCP starts, tools work, gallery resource and optional entrypoint work',async()=>{const dir=mkdtempSync(join(tmpdir(),'art-day-test-'));const c=new Client({name:'test',version:'1'});try{await c.connect(new StdioClientTransport({command:process.execPath,args:[resolve('dist/server.mjs')],env:{...process.env,ART_DAY_DATA_DIR:dir},stderr:'pipe'}));let list=await c.listTools();assert.ok(list.tools.some(t=>t.name==='art_gallery'));const brief=await c.callTool({name:'art_brief',arguments:{}});assert.equal(brief.structuredContent.historyCount,0);let r=await c.callTool({name:'art_settings',arguments:{language:'fr',sidebar:false}});assert.equal(r.isError,undefined);assert.equal(r.structuredContent.language,'fr');list=await c.listTools();assert.ok(!list.tools.some(t=>t.name==='art_gallery'));await c.callTool({name:'art_settings',arguments:{sidebar:true}});assert.ok((await c.listTools()).tools.some(t=>t.name==='art_gallery'));const resource=await c.readResource({uri:'ui://art-day/gallery'});assert.ok(resource.contents[0].text.includes('Art Day'));r=await c.callTool({name:'art_rate',arguments:{id:'missing',rating:5}});assert.equal(r.isError,true)}finally{await c.close();rmSync(dir,{recursive:true,force:true})}});

test('sidebar exposes daily image; gallery ratings and favorites stay attached to viewed artwork',async()=>{
 const {openStore}=await import('../src/domain.mjs');const {artDate}=await import('../src/store.mjs');
 const dir=mkdtempSync(join(tmpdir(),'art-day-gallery-'));const d=openStore(join(dir,'art-day.sqlite'));
 const a={id:'test-painting',date:artDate(),title:'Test',artist:'Test Artist',year:'1899',museum:'Museum',medium:'Oil',source:'Wikimedia Commons',sourceUrl:'https://commons.wikimedia.org/wiki/File:Test.jpg',imageSource:'Wikimedia Commons',imageSourceUrl:'https://commons.wikimedia.org/wiki/File:Test.jpg',imageUrl:'https://upload.wikimedia.org/test.jpg',rights:'Public Domain',story:'A verified test description long enough for validation.',detail:'A detail used only for this isolated test.',tags:['green']};
 d.store.publish(a,'test-sha',{bytes:Buffer.from([255,216,255,217]),type:'image/jpeg',sha:'test-sha'});
 const c=new Client({name:'test',version:'1'});
 try{
 await c.connect(new StdioClientTransport({command:process.execPath,args:[resolve('dist/server.mjs')],env:{...process.env,ART_DAY_DATA_DIR:dir},stderr:'pipe'}));
 const tool=(await c.listTools()).tools.find(t=>t.name==='art_gallery');
 assert.equal(tool.icons[0].src,a.imageUrl);assert.equal(tool._meta['openai/ui'].entrypoints[0].type,'global');
 assert.deepEqual(tool._meta.ui.visibility,['app']);
 for(const arguments_ of [{id:a.id,rating:5},{id:a.id,favorite:true}]){const r=await c.callTool({name:'art_rate',arguments:arguments_});assert.equal(r.isError,undefined)}
 const view=(await c.callTool({name:'art_view',arguments:{id:a.id}})).structuredContent;
 assert.equal(view.preference.rating,5);assert.equal(view.preference.favorite,true);assert.ok(view.image.startsWith('data:image/jpeg'));
 assert.equal((await c.callTool({name:'art_favorites',arguments:{}})).structuredContent.artworks[0].id,a.id);
 assert.equal((await c.callTool({name:'art_brief',arguments:{}})).structuredContent.currentId,a.id);
 const html=(await c.readResource({uri:'ui://art-day/gallery'})).contents[0];assert.equal(html._meta['openai/ui'].preferredDisplayMode,'fullscreen');
 }finally{await c.close();d.db.close();rmSync(dir,{recursive:true,force:true})}
});

test('bundled gallery script remains valid after HTML embedding',async()=>{const {readFileSync}=await import('node:fs');const vm=await import('node:vm');const html=readFileSync('dist/gallery.html','utf8');new vm.Script(html.split('<script>')[1].split('</script>')[0]);});


test('launches from the plugin manifest with cwd resolved against plugin root',async()=>{
 const {readFileSync}=await import('node:fs');const config=JSON.parse(readFileSync('.mcp.json','utf8')).mcpServers['art-day'];
 const dir=mkdtempSync(join(tmpdir(),'art-day-manifest-'));const c=new Client({name:'manifest-test',version:'1'});
 try{await c.connect(new StdioClientTransport({...config,cwd:resolve(config.cwd),env:{...process.env,ART_DAY_DATA_DIR:dir},stderr:'pipe'}));
 const list=await c.listTools();assert.ok(list.tools.find(t=>t.name==='art_gallery').icons.length);assert.equal((await c.callTool({name:'art_brief',arguments:{}})).isError,undefined);
 }finally{await c.close();rmSync(dir,{recursive:true,force:true})}
});
