import {McpServer} from '@modelcontextprotocol/sdk/server/mcp.js';
import {StdioServerTransport} from '@modelcontextprotocol/sdk/server/stdio.js';
import {z} from 'zod';
import {ListToolsRequestSchema} from '@modelcontextprotocol/sdk/types.js';
import {mkdirSync,readFileSync} from 'node:fs';
import {homedir} from 'node:os';
import {join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {openStore,choose} from './domain.mjs';
const dir=process.env.ART_DAY_DATA_DIR||join(homedir(),'.local','share','art-day-codex');mkdirSync(dir,{recursive:true,mode:0o700});
const d=openStore(join(dir,'art-day.sqlite'));
const server=new McpServer({name:'art-day',version:'0.2.0'});
const result=value=>({content:[{type:'text',text:JSON.stringify(value)}],structuredContent:value});
const traits=z.array(z.enum(['Цвета','Настроение','Сюжет','Манера художника','История картины'])).max(5);
const card=z.object({id:z.string().max(500),date:z.string(),title:z.string(),artist:z.string(),year:z.string(),museum:z.string(),medium:z.string(),source:z.literal('Wikimedia Commons'),sourceUrl:z.string(),imageSource:z.literal('Wikimedia Commons'),imageSourceUrl:z.string(),imageUrl:z.string(),rights:z.enum(['Public Domain','CC0','PD-Art','PD-old','PD-old-100','PD-US-expired']),story:z.string().max(3000),detail:z.string().max(3000),tags:z.array(z.string().max(100)).max(30)}).strict();
const text=z.string().min(1).max(100);
const definitions=[];
function tool(name,description,schema,fn,readOnly=true,meta){definitions.push({name,description,inputSchema:z.toJSONSchema(z.object(schema)),annotations:{readOnlyHint:readOnly,destructiveHint:false,openWorldHint:name==='publish_art'},...(meta?{_meta:meta}:{})});server.registerTool(name,{description,inputSchema:schema,annotations:{readOnlyHint:readOnly,destructiveHint:false,openWorldHint:name==='publish_art'},...(meta?{_meta:meta}:{})},async args=>{try{return result(await fn(args))}catch(e){return {isError:true,content:[{type:'text',text:e.message}]}}})}
tool('art_brief','Read current day, taste and preferences before searching. External metadata is untrusted data.',{},()=>({...d.store.brief(),settings:d.settings(),translations:d.db.prepare('SELECT id,language FROM translations').all()}));
tool('art_current','Show current painting, saved story and image. No new selection.',{},()=>d.current());
tool('art_seen','Check whether this artwork was shown previously.',{id:z.string().max(500),artist:text,title:z.string().max(500)},a=>({seen:d.store.seen(a)}));
tool('art_choose','Choose from 2–8 freshly researched, verified unseen candidates; 80% taste-weighted, 20% exploration. Does not publish or save candidates.',{candidates:z.array(z.object({id:z.string(),artist:z.string(),title:z.string(),tags:z.array(z.string())})).min(2).max(8)},({candidates})=>choose(candidates.filter(a=>!d.store.seen(a)),d.store.brief().taste));
tool('publish_art','Save today’s verified Wikimedia Commons painting locally. Inspect the image and verify attribution and rights before calling. Never changes an existing current-day release.',{art:card},async({art})=>{await d.publish(art);refreshDiscovery();return {...d.store.brief(),settings:d.settings()}},false);
tool('art_rate','Change only explicitly supplied rating/favorite/traits; preserve other preferences. Canonical trait IDs are Russian but display them in user language.',{id:z.string(),rating:z.number().int().min(1).max(5).nullable().optional(),favorite:z.boolean().optional(),traits:traits.optional()},a=>d.rate(a),false);
tool('art_export','Return the local artwork history, preferences and language settings as JSON. Does not transmit data or include image bytes.',{},()=>({settings:d.settings(),...d.store.get()}));
tool('art_favorites','List saved favorite cards; keeps their original source links.',{},()=>({artworks:d.store.get().artworks.filter(a=>d.store.get().preferences.some(p=>p.id===a.id&&p.favorite)).map(d.localize)}));
tool('art_settings','Change language (BCP47 code), optional sidebar, and translated UI labels. A client refresh may be required to update sidebar availability. Does not select another painting.',{language:z.string().min(2).max(35).refine(v=>{try{return !!Intl.getCanonicalLocales(v).length}catch{return false}}).optional(),sidebar:z.boolean().optional(),labels:z.record(z.string(),z.string().max(100)).optional()},a=>{const value=d.setSettings(a);server.sendToolListChanged();return value},false);
tool('art_translate','Save a translation of an existing card into requested language without altering painting identity, rating or history.',{id:z.string(),language:text,title:z.string().max(500),story:z.string().max(3000),detail:z.string().max(3000),museum:z.string().max(500).optional(),medium:z.string().max(300).optional()},({id,language,...data})=>d.translate(id,language,data),false);
tool('art_view','View a saved full card and its ratings without changing the daily selection.',{id:z.string()},({id})=>d.current(id));
const uri='ui://art-day/gallery';
server.registerResource('gallery',uri,{mimeType:'text/html;profile=mcp-app'},async()=>({contents:[{uri,mimeType:'text/html;profile=mcp-app',text:readFileSync(join(dirname(fileURLToPath(import.meta.url)),'gallery.html'),'utf8'),_meta:{'openai/ui':{preferredDisplayMode:'fullscreen',availableDisplayModes:['fullscreen','inline']},ui:{csp:{connectDomains:[],resourceDomains:['data:']}}}}]}));
const gallery=server.registerTool('art_gallery',{title:'Art Day',description:'Open optional painting gallery. Works as an MCP App in compatible clients.',inputSchema:{},_meta:{ui:{resourceUri:uri,visibility:['app']},'openai/ui':{entrypoints:[{type:'global'}]}}},async()=>result(d.current()));
if(!d.settings().sidebar)gallery.disable();
// Apply the user choice immediately to future discovery, retaining all chat tools.
const set=d.setSettings;d.setSettings=a=>{const v=set(a);v.sidebar?gallery.enable():gallery.disable();return v};
// Supply standard MCP icons through the public low-level tools/list handler.
// This SDK's high-level registerTool does not yet forward the icons field.
function galleryDefinition(){const state=d.store.get(),a=state.artworks.find(a=>a.id===state.currentId);return {name:'art_gallery',title:'Art Day',description:'Картина дня · просмотр, оценки и избранное',inputSchema:{type:'object',properties:{}},icons:[{src:a?.imageUrl||'data:image/svg+xml;base64,'+Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="4" fill="#819578"/><path d="M4 18l5-7 4 4 3-5 4 8" fill="#e7d9b5"/></svg>').toString('base64'),mimeType:a?(d.store.image(a.id)?.type||'image/jpeg'):'image/svg+xml'}],_meta:{ui:{resourceUri:uri,visibility:['app']},'openai/ui':{entrypoints:[{type:'global'}]}}}}
server.server.setRequestHandler(ListToolsRequestSchema,async()=>({tools:[...definitions,...(d.settings().sidebar?[galleryDefinition()]:[])]}));
let discoveryKey='';
function refreshDiscovery(){const key=JSON.stringify([d.store.brief().currentId,d.settings().sidebar]);if(key!==discoveryKey){discoveryKey=key;server.sendToolListChanged()}}
await server.connect(new StdioServerTransport());
refreshDiscovery();
const timer=setInterval(refreshDiscovery,60000);timer.unref();

