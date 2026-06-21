import sys
import os

# --- 1. すべての変更箇所を強制的に「グループC（ロジック）」にするファイル ---
# （コンセンサスや通信プロトコルに直結するため、一切ハンク分解せずCにするもの）
FORCE_LOGIC_FILES = [
    'src/version.h',
    'src/protocol.cpp',
    'src/protocol.h',
    'src/net.cpp',
    'src/net.h',
    'src/net_processing.cpp',
    'src/validation.cpp',
    'src/validation.h',
    'src/chainparams.cpp',
    'src/chainparams.h',
    'src/chainparamsseeds.h',
    'src/checkpointsync.cpp',
    'src/checkpointsync.h',
    'src/pow.cpp',
    'src/pow.h',
    'src/pos.cpp',
    'src/pos.h',
    'src/wallet/wallet.cpp',
    'src/wallet/wallet.h',
    'src/miner.cpp',
    'src/miner.h',
    'src/consensus/params.h',
    'src/consensus/validation.h',
    'src/test/validation_tests.cpp',
    'src/txmempool.cpp',
    'src/qtum/qtumstate.cpp',
    'src/qtum/qtumstate.h',
    'src/qtum/qtumDGP.cpp',
    'src/qtum/qtumDGP.h',
    'src/cpp-ethereum',
    'src/util/strencodings.h',
    'src/logging.cpp',
    'src/logging.h',
]

# --- 2. 「名前変更(B)」と「ロジック(C)」が同居しており、ハンク単位で切り分けるファイル ---
HYBRID_FILES = [
    'src/Makefile.am',
    'src/init.cpp',
    'src/rpc/blockchain.cpp',
    'src/rpc/mining.cpp',
    'src/rpc/client.cpp',
    'src/wallet/rpcwallet.cpp',
    'src/wallet/rpcdump.cpp',
]

def get_filepath(diff_line):
    parts = diff_line.split()
    if len(parts) >= 3:
        filepath = parts[2].decode('utf-8', errors='ignore').strip()
        filepath = filepath.replace('\\', '/')
        if filepath.startswith('a/') or filepath.startswith('b/'):
            filepath = filepath[2:]
        filepath = filepath.strip('"\'')
        return filepath
    return ""

def is_pure_branding_hunk(hunk_lines, filepath):
    filepath = filepath.replace('\\', '/').strip('"\'')
    if filepath.startswith('a/') or filepath.startswith('b/'):
        filepath = filepath[2:]

    if filepath in FORCE_LOGIC_FILES:
        return False

    if filepath not in HYBRID_FILES:
        return True

    # --- ハイブリッドファイルのハンク内ロジック解析 ---
    logic_indicators = [
        'checkpointsync', 'nSubsidyHalvingInterval', 'MAX_MONEY', 'GetProofOfStakeReward',
        'GetBlockSubsidy', 'CalculateNextWorkRequired', 'NODE_ACP', 'hashCheckpoint',
        'DGP', 'nFixUTXOCacheHFHeight', 'estimatesmartfee', 'getwork', 'checkpoints',
        'stateVIPSTARCOIN', 'stateQtum', 'MiningRequiresPeers', 'nPosTargetTimespan',
        'nPowTargetTimespan', 'nPowTargetSpacing', 'nDiffAdjustChange', 'nDiffDamping',
        'pnSeed6_main', 'pnSeed6_test', 'nEnableHeaderSignatureHeight', 'GetPoWMHashPS',
        'GetEstimatedAnnualROI', 'estimatesmartfee', 'validation_tests', 'm_last_block_num_txs',
        'AttemptToAddContractToBlock', 'addPackageTxs', 'UpdateHashProof', 'AcceptBlock',
        'ProcessNewBlock', 'CheckWork', 'FormatHashBuffers', 'ByteReverse', 'GetProofOfStakeReward',
        'ac_cv_exeext', 'openssl', 'limits', 'qbytearraymatcher', 'submodule commit', 'BCLog::INDEX',
        'CheckInputsAndUpdateCoins', 'getcontractcode', 'sendcheckpoint', 'getcheckpoint',
        'LIBBITCOIN_SERVER'
    ]

    changed_lines = []
    for line in hunk_lines:
        if (line.startswith(b'+') and not line.startswith(b'+++')) or \
           (line.startswith(b'-') and not line.startswith(b'---')):
            try:
                changed_lines.append(line.decode('utf-8', errors='ignore'))
            except:
                changed_lines.append(str(line))

    for line in changed_lines:
        if any(indicator.lower() in line.lower() for indicator in logic_indicators):
            return False
        if '#include' in line and 'checkpointsync' in line:
            return False

    return True

def parse_patch(lines):
    files = []
    current_file = None
    current_hunk = None

    for line in lines:
        if line.startswith(b'diff --git '):
            current_file = {
                'diff_line': line,
                'headers': [],
                'hunks': []
            }
            files.append(current_file)
            current_hunk = None
        elif current_file is None:
            continue
        elif line.startswith(b'@@ '):
            current_hunk = {
                'hunk_header': line,
                'lines': []
            }
            current_file['hunks'].append(current_hunk)
        elif current_hunk is not None:
            current_hunk['lines'].append(line)
        else:
            current_file['headers'].append(line)

    return files

def split_patch(patch_file):
    if not os.path.exists(patch_file):
        print(f"Error: {patch_file} が見つかりません。")
        return

    with open(patch_file, 'rb') as f:
        content = f.read()

    lines = content.split(b'\n')
    lines = [line + b'\n' for line in lines]
    if lines and lines[-1] == b'\n':
        lines.pop()

    parsed_files = parse_patch(lines)

    f_b = open('vips_group_b_branding_hunks.patch', 'wb')
    f_c = open('vips_group_c_logic_hunks.patch', 'wb')

    count_b = 0
    count_c = 0

    for file in parsed_files:
        filepath = get_filepath(file['diff_line'])

        if filepath in FORCE_LOGIC_FILES:
            print(f"[FORCE LOGIC (C)] {filepath}")
            f_c.write(file['diff_line'])
            f_c.writelines(file['headers'])
            for hunk in file['hunks']:
                f_c.write(hunk['hunk_header'])
                f_c.writelines(hunk['lines'])
            count_c += 1
            continue

        if filepath not in HYBRID_FILES:
            f_b.write(file['diff_line'])
            f_b.writelines(file['headers'])
            for hunk in file['hunks']:
                f_b.write(hunk['hunk_header'])
                f_b.writelines(hunk['lines'])
            count_b += 1
            continue

        print(f"[HYBRID SPLIT (B/C)] {filepath}")

        written_header_b = False
        written_header_c = False

        for hunk in file['hunks']:
            is_b = is_pure_branding_hunk(hunk['lines'], filepath)

            if is_b:
                if not written_header_b:
                    f_b.write(file['diff_line'])
                    f_b.writelines(file['headers'])
                    written_header_b = True
                f_b.write(hunk['hunk_header'])
                f_b.writelines(hunk['lines'])
            else:
                if not written_header_c:
                    f_c.write(file['diff_line'])
                    f_c.writelines(file['headers'])
                    written_header_c = True
                f_c.write(hunk['hunk_header'])
                f_c.writelines(hunk['lines'])

        if written_header_b:
            count_b += 1
        if written_header_c:
            count_c += 1

    f_b.close()
    f_c.close()

    original_lines = len(lines)
    with open('vips_group_b_branding_hunks.patch', 'rb') as fb, open('vips_group_c_logic_hunks.patch', 'rb') as fc:
        split_lines = len(fb.readlines()) + len(fc.readlines())

    print(f"\n分割処理が完全に完了しました！")
    print(f"元ファイルの総行数: {original_lines} 行")
    print(f"分割後の合計行数  : {split_lines} 行")
    if original_lines == split_lines:
        print("✅ 1行の過不足もなく、完全に100%一致して分割されました。")
    else:
        print(f"⚠️ 警告: 行数不一致があります (差分: {original_lines - split_lines} 行)。")

if __name__ == '__main__':
    target = 'vips_custom.patch'
    if len(sys.argv) > 1:
        target = sys.argv[1]
    split_patch(target)
