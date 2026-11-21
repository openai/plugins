import {DatabaseSync} from 'node:sqlite';
import {createArtStore,fetchImage,validateArtwork} from './store.mjs';
export function openStore(file){
 const db=new DatabaseSync(file);db.exec('PRAGMA busy_timeout=5000; CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT); CREATE TABLE IF NOT EXISTS translations(id TEXT,language TEXT,data TEXT,PRIMARY KEY(id,language));');
 const store=createArtStore(db);
 const settings=()=>({language:'en',sidebar:true,...Object.fromEntries(db.prepare('SELECT * FROM settings').all().map(r=>[r.key,JSON.parse(r.value)]))});
 const setSettings=p=>{if(p.language&&p.language!==settings().language&&!p.labels)p={...p,labels:{}};for(const [k,v] of Object.entries(p))db.prepare('INSERT OR REPLACE INTO settings VALUES(?,?)').run(k,JSON.stringify(v));return settings()};
 const localize=a=>{const t=db.prepare('SELECT data FROM translations WHERE id=? AND language=?').get(a.id,settings().language);return t?{...a,...JSON.parse(t.data)}:a};
 function current(id){const s=store.get(),selected=id||s.currentId,a=s.artworks.find(a=>a.id===selected&&!a.compact);if(id&&!a)throw Error("Full card not available");const pref=s.preferences.find(p=>p.id===selected);const im=a?store.image(a.id):null;return {settings:settings(),stale:s.stale,date:store.brief().date,art:a?localize(a):null,preference:pref||null,image:im?`data:${im.type};base64,${Buffer.from(im.bytes).toString('base64')}`:null}}
 async function publish(a){validateArtwork(a);const im=await fetchImage(a);const r=store.publish(a,im.sha,im);if(r.changed)translate(a.id,settings().language,{title:a.title,story:a.story,detail:a.detail,museum:a.museum,medium:a.medium});return r}
 function rate(p){const old=store.get().preferences.find(x=>x.id===p.id);store.rate({id:p.id,rating:old?.rating??null,favorite:old?.favorite??false,traits:old?.traits??[],...p});return current()}
 function translate(id,language,data){if(!store.get().artworks.some(a=>a.id===id&&!a.compact))throw Error('Full card not available');db.prepare('INSERT OR REPLACE INTO translations VALUES(?,?,?)').run(id,language,JSON.stringify(data));return current()}
 return {db,store,settings,setSettings,current,publish,rate,translate,localize};
}
export function choose(candidates,taste,rng=Math.random){
 if(!candidates.length)throw Error('No fresh verified candidates');
 const exploratory=rng()<0.2;
 const weights=candidates.map(a=>exploratory?1:Math.exp(Math.max(-3,Math.min(3,((taste.artists.find(x=>x.name===a.artist)?.weight||0)+(a.tags||[]).reduce((s,t)=>s+(taste.tags.find(x=>x.name===t)?.weight||0),0))/4))));
 let n=rng()*weights.reduce((a,b)=>a+b,0),i=0;for(;i<weights.length-1;i++){n-=weights[i];if(n<0)break;}
 return {selected:candidates[i],mode:exploratory?'exploration':'taste-weighted',candidateCount:candidates.length};
}
