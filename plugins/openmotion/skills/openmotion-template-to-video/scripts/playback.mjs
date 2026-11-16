import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { readFile, realpath, stat, writeFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export function byteRange(header, size) {
  if (header === undefined) return { start: 0, end: size - 1, status: 200 };
  const match = /^bytes=(\d*)-(\d*)$/.exec(header);
  if (!match || (!match[1] && !match[2])) return null;
  let start = match[1] ? Number(match[1]) : Math.max(0, size - Number(match[2]));
  let end = match[1] && match[2] ? Math.min(size - 1, Number(match[2])) : size - 1;
  if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start >= size || end < start || (!match[1] && Number(match[2]) === 0)) return null;
  return { start, end, status: 206 };
}
function page() {
  return `<!doctype html><meta charset="utf-8"><title>OpenMotion final-file playback check</title>
<video id="video" width="640" controls preload="auto" src="/video.mp4"></video>
<button id="start">Start playback check</button><pre id="result">Ready</pre>
<script>
const video=document.querySelector('video'), result=document.querySelector('#result'), button=document.querySelector('#start');
const timeout=(promise,ms=10000)=>Promise.race([promise,new Promise((_,reject)=>setTimeout(()=>reject(Error('Media operation timed out')),ms))]);
const event=name=>new Promise((resolve,reject)=>{video.addEventListener(name,resolve,{once:true});video.addEventListener('error',()=>reject(Error(video.error?.message||'Media error')),{once:true});});
async function seek(time){video.pause();if(Math.abs(video.currentTime-time)>0.001){const done=event('seeked');video.currentTime=time;await timeout(done);}if(video.readyState<2)await timeout(event('loadeddata'));return {requested:time,actual:video.currentTime,readyState:video.readyState};}
button.onclick=async()=>{button.disabled=true;const report={status:'running',scope:'final-file-playback',startedAt:new Date().toISOString(),observations:[],subjectiveAudioReview:'not_run',creativeAcceptance:'not_run'};try{
if(video.readyState<1)await timeout(event('loadedmetadata'));
report.duration=video.duration;report.width=video.videoWidth;report.height=video.videoHeight;
if(!Number.isFinite(video.duration)||video.duration<=0)throw Error('Invalid media duration');
video.loop=false;video.playbackRate=1;await seek(0);const began=performance.now(), ended=event('ended');await video.play();
result.textContent='Playing the complete final file at normal speed';await timeout(ended,Math.max(15000,(video.duration+15)*1000));
report.fullPlayback={ended:video.ended,currentTime:video.currentTime,elapsedSeconds:(performance.now()-began)/1000};
if(!video.ended||report.fullPlayback.elapsedSeconds<video.duration*0.8)throw Error('Full playback did not finish at normal speed');
for(const time of [0,video.duration/2,Math.max(0,video.duration-1)]){const observation=await seek(time);report.observations.push(observation);if(Math.abs(observation.actual-time)>0.15||observation.readyState<2)throw Error('Seek failed');}
await seek(0);await video.play();await timeout(new Promise(resolve=>{const check=()=>{if(video.currentTime>=Math.min(0.2,video.duration/2)){video.removeEventListener('timeupdate',check);resolve();}};video.addEventListener('timeupdate',check);}));
report.replay={currentTime:video.currentTime,paused:video.paused};await seek(0);report.finalState={currentTime:video.currentTime,paused:video.paused};report.status='passed';
}catch(error){report.status='failed';report.error=error.message;video.pause();}
report.completedAt=new Date().toISOString();result.textContent=JSON.stringify(report,null,2);const response=await fetch('/report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(report)});if(!response.ok)result.textContent+='\\nReport save failed: '+response.status;};
</script>`;
}
export async function playbackServer(videoPath, reportPath) {
  assert(path.isAbsolute(videoPath) && path.isAbsolute(reportPath) && videoPath !== reportPath, 'ABSOLUTE_DISTINCT_PATHS_REQUIRED');
  const info = await stat(videoPath); assert(info.isFile() && info.size > 0, 'VIDEO_MISSING');
  const hash = createHash('sha256').update(await readFile(videoPath)).digest('hex');
  const html = Buffer.from(page());
  const server = createServer(async (request, response) => {
    try {
      const address = server.address(), origin = 'http://127.0.0.1:' + address.port;
      if (request.headers.host !== '127.0.0.1:' + address.port) { response.writeHead(403).end(); return; }
      const url = new URL(request.url, origin);
      response.setHeader('Cache-Control', 'no-store');
      if (url.pathname === '/report' && request.method === 'POST') {
        if (request.headers.origin !== origin || request.headers['content-type'] !== 'application/json') { response.writeHead(403).end(); return; }
        let body = ''; for await (const chunk of request) { body += chunk; if (body.length > 128 * 1024) { response.writeHead(413).end(); return; } }
        const report = JSON.parse(body); assert(['passed', 'failed'].includes(report.status), 'Invalid report status');
        const current = await stat(videoPath); assert(current.size === info.size && current.mtimeMs === info.mtimeMs, 'VIDEO_CHANGED');
        await writeFile(reportPath, JSON.stringify({ ...report, file: videoPath, sha256: hash }, null, 2) + '\n', { flag: 'wx' });
        response.writeHead(201).end(); return;
      }
      if (!['GET', 'HEAD'].includes(request.method)) { response.writeHead(405).end(); return; }
      if (url.pathname === '/' || url.pathname === '/playback.html') {
        response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Content-Length': html.length });
        response.end(request.method === 'HEAD' ? undefined : html); return;
      }
      if (url.pathname !== '/video.mp4') { response.writeHead(404).end(); return; }
      const range = byteRange(request.headers.range, info.size);
      if (!range) { response.writeHead(416, { 'Content-Range': 'bytes */' + info.size }).end(); return; }
      const { start, end, status } = range;
      const headers = { 'Content-Type': 'video/mp4', 'Accept-Ranges': 'bytes', 'Content-Length': end - start + 1 };
      if (status === 206) headers['Content-Range'] = 'bytes ' + start + '-' + end + '/' + info.size;
      response.writeHead(status, headers);
      if (request.method === 'HEAD') response.end(); else createReadStream(videoPath, { start, end }).on('error', () => response.destroy()).pipe(response);
    } catch (error) { response.writeHead(400, { 'Content-Type': 'text/plain' }).end(error.message); }
  });
  return server;
}
async function main() {
  const args = process.argv.slice(2);
  if (args.includes('--help')) { console.log('playback.mjs --video /absolute/final.mp4 --report /new/absolute/report.json'); return; }
  assert(args.length === 4 && args[0] === '--video' && args[2] === '--report', 'Use --help for arguments.');
  const server = await playbackServer(args[1], args[3]);
  server.listen(0, '127.0.0.1', () => console.log(JSON.stringify({ url: 'http://127.0.0.1:' + server.address().port + '/playback.html', report: args[3] })));
  const close = () => server.close(() => process.exit(0)); process.once('SIGTERM', close); process.once('SIGINT', close);
}
if (process.argv[1] && import.meta.url === pathToFileURL(await realpath(process.argv[1])).href) main().catch(error => { console.error(error.message); process.exitCode = 1; });
