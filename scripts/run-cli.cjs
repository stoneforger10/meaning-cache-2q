// Suppress CLI debug/receipt output; expose only public transaction hashes.
const {spawn}=require('node:child_process');
const path=require('node:path');
const args=process.argv.slice(2);
if(!['deploy','write'].includes(args[0]))throw Error('Only deploy/write supported');
const cli=process.env.CACHE_CLI_PATH||path.resolve(__dirname,'../../intent-firewall/node_modules/genlayer/dist/index.js');
const child=spawn(process.execPath,['--require',path.join(__dirname,'pin_cli_context.cjs'),
  '--require',path.join(__dirname,'broadcast_once.cjs'),cli,...args],
  {windowsHide:true,stdio:['ignore','pipe','pipe']});
child.stdout.resume(); // Never display raw SDK/Studio receipt debug output.
let carry='',known=false;
child.stderr.on('data',chunk=>{
  carry+=chunk.toString('utf8');
  const lines=carry.split(/\r?\n/);carry=lines.pop();
  if(carry.length>65536)carry='';
  for(const line of lines)if(/^BROADCAST_HASH 0x[0-9a-fA-F]{64}$/.test(line)){known=true;console.log(line);}
});
child.on('error',()=>{console.error('CLI process failed; no blind retries');process.exitCode=1;});
child.on('close',code=>{
  console.log(JSON.stringify({cli_exit:code,hash_observed:known}));
  if(code!==0||!known){console.error('Inspect receipt/history before retrying an uncertain broadcast');process.exitCode=1;}
});
