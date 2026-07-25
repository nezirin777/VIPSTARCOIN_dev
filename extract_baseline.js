#!/usr/bin/env node
'use strict';

/**
 * Phase 6 全ブロックリプレイ基盤 — ベースライン抽出スクリプト
 *
 * 対象: tooling/phase6-baseline ブランチでビルドした一時ノード
 *       （getreplaybaseline RPCを追加したもの）
 * 注意: v1.2.4.1（保護ブランチ）そのものには絶対にこのRPCを追加しないこと。
 *
 * genesis〜現行高までの {height, hash, bits, hashStateRoot, hashUTXORoot, moneysupply}
 * を1行1ブロックのNDJSON形式で保存する。中断しても進捗ファイルから再開可能。
 *
 * 使い方:
 *   RPC_PORT=31916 RPC_USER=nezirin RPC_PASS=eclipse node extract_baseline.js
 *
 * 必要環境: Node.js 18+（グローバルfetch使用、Node 24で確認済み）
 */

const fs = require('fs');
const path = require('path');

const RPC_HOST = process.env.RPC_HOST || '127.0.0.1';
const RPC_PORT = process.env.RPC_PORT || '31916';
const RPC_USER = process.env.RPC_USER || 'nezirin';
const RPC_PASS = process.env.RPC_PASS || 'eclipse';
const CONCURRENCY = parseInt(process.env.CONCURRENCY || '32', 10);
const OUTPUT_PATH = process.env.OUTPUT_PATH || path.join(__dirname, 'baseline_v1.2.4.1.ndjson');
const PROGRESS_PATH = OUTPUT_PATH + '.progress';

const authHeader = 'Basic ' + Buffer.from(`${RPC_USER}:${RPC_PASS}`).toString('base64');
const rpcUrl = `http://${RPC_HOST}:${RPC_PORT}/`;

async function rpcCall(method, params) {
  const res = await fetch(rpcUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: authHeader,
    },
    body: JSON.stringify({ jsonrpc: '1.0', id: 'baseline', method, params }),
  });
  if (!res.ok && res.status !== 500) {
    throw new Error(`HTTP ${res.status}`);
  }
  const json = await res.json();
  if (json.error) throw new Error(JSON.stringify(json.error));
  return json.result;
}

function readResumeHeight() {
  if (fs.existsSync(PROGRESS_PATH)) {
    const h = parseInt(fs.readFileSync(PROGRESS_PATH, 'utf8').trim(), 10);
    if (!Number.isNaN(h)) return h + 1;
  }
  return 0;
}

async function main() {
  const info = await rpcCall('getblockchaininfo', []);
  const tip = info.blocks;
  const startHeight = readResumeHeight();

  console.log(`tip=${tip}, 再開高さ=${startHeight}`);
  if (startHeight > tip) {
    console.log('既に完了しています。');
    return;
  }

  const out = fs.createWriteStream(OUTPUT_PATH, { flags: startHeight === 0 ? 'w' : 'a' });

  let cursor = startHeight;
  let completed = startHeight;
  let inFlight = 0;
  let lastProgressWrite = Date.now();
  const pending = new Map(); // height -> JSON文字列（順序通りに書き出すためのバッファ）

  await new Promise((resolve) => {
    function flushReady() {
      while (pending.has(completed)) {
        out.write(pending.get(completed) + '\n');
        pending.delete(completed);
        completed++;

        if (Date.now() - lastProgressWrite > 5000) {
          fs.writeFileSync(PROGRESS_PATH, String(completed - 1));
          lastProgressWrite = Date.now();
        }
        if (completed % 50000 === 0) {
          console.log(`進捗: ${completed} / ${tip}`);
        }
      }
      if (completed > tip) {
        fs.writeFileSync(PROGRESS_PATH, String(tip));
        out.end(() => {
          console.log('完了:', OUTPUT_PATH);
          resolve();
        });
      }
    }

    function scheduleNext() {
      while (inFlight < CONCURRENCY && cursor <= tip) {
        const h = cursor++;
        inFlight++;
        rpcCall('getreplaybaseline', [h])
          .then((r) => {
            pending.set(h, JSON.stringify(r));
          })
          .catch((err) => {
            console.error(`height ${h} 失敗:`, err.message || err);
            pending.set(h, JSON.stringify({ height: h, error: String(err.message || err) }));
          })
          .finally(() => {
            inFlight--;
            flushReady();
            scheduleNext();
          });
      }
    }

    scheduleNext();
  });
}

main().catch((err) => {
  console.error('fatal:', err);
  process.exit(1);
});
