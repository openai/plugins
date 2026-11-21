// Local scheduler fallback when the host has not refreshed MCP tool discovery.
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const name=process.argv[2]||'art_brief';
const args=process.argv.includes('--stdin')?JSON.parse(readFileSync(0,'utf8')):{};
const client=new Client({name:'art-day-local-cli',version:'0.2.0'});
try{
 await client.connect(new StdioClientTransport({command:process.execPath,args:[fileURLToPath(new URL('./server.mjs',import.meta.url))],stderr:'inherit'}));
 const r=await client.callTool({name,arguments:args});
 if(r.isError)throw Error(r.content?.[0]?.text||'Art Day failed');
 const value=r.structuredContent||JSON.parse(r.content[0].text);
 if(value.image)value.image='[image retained in local database; inspect art.imageUrl]';
 console.log(JSON.stringify(value,null,2));
}catch(e){console.error(e.message);process.exitCode=1}finally{await client.close()}
