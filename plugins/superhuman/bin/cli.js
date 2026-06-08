#!/usr/bin/env node
const { spawn } = require('child_process');

const child = spawn('npx', [
  'mcp-remote@latest',
  'https://mcp.mail.superhuman.com/mcp'
], { stdio: 'inherit' });

child.on('exit', (code) => process.exit(code ?? 0));
