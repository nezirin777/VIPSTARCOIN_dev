import sys
import os

def get_group(filepath):
    # a/ や b/ のプレフィックスを除去してパスを標準化
    filepath = filepath.strip()
    if filepath.startswith('a/') or filepath.startswith('b/'):
        filepath = filepath[2:]

    # --- グループA：100%名前変更・メタ情報（無視してOK） ---
    group_a_dirs = ['.github', 'contrib', 'depends', 'share', 'doc']
    group_a_files = ['.gitignore', 'README.md', 'Makefile.am', 'configure.ac']

    if any(filepath.startswith(d + '/') for d in group_a_dirs):
        return 'A'
    if filepath in group_a_files:
        return 'A'
    if filepath.endswith('Makefile.am') or filepath.endswith('Makefile.qt.include'):
        return 'A'

    # --- グループC：本質的なプログラムロジック（最重要） ---
    # 難易度調整、プレマイン、PoS報酬、同期チェックポイントなど
    group_c_files = [
        'src/rpc/blockchain.cpp',
        'src/rpc/mining.cpp',
        'src/rpc/rawtransaction_util.cpp',
        'src/amount.h',
        'src/chainparams.cpp',
        'src/chainparams.h',
        'src/chainparamsbase.cpp',
        'src/chainparamsbase.h',
        'src/chainparamsseeds.h',
        'src/checkpointsync.cpp',
        'src/checkpointsync.h',
        'src/pow.cpp',
        'src/pow.h',
        'src/pos.cpp',
        'src/pos.h',
        'src/validation.cpp',
        'src/validation.h',
        'src/wallet/wallet.cpp',
        'src/wallet/wallet.h',
        'src/miner.cpp',
        'src/miner.h',
        'src/consensus/consensus.cpp',
        'src/consensus/consensus.h',
        'src/consensus/params.h',
        'src/consensus/validation.h',
        'src/txdb.cpp',
        'src/txdb.h',
        'src/net_processing.cpp',
        'src/init.cpp',
    ]
    if filepath in group_c_files:
        return 'C'

    # --- グループB：C++コードだが、中身は表示名やUIの書き換え ---
    # src/ 以下の残りのファイル（formsや表示用テキストなど）はグループBへ
    if filepath.startswith('src/'):
        return 'B'

    # それ以外の例外は念のためグループAに分類
    return 'A'

def split_patch(patch_file):
    if not os.path.exists(patch_file):
        print(f"Error: {patch_file} が見つかりません。")
        return

    with open(patch_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    current_group = 'A'
    current_block = []
    files_count = {'A': 0, 'B': 0, 'C': 0}

    # 出力ファイルのオープン
    f_a = open('vips_group_a_meta.patch', 'w', encoding='utf-8')
    f_b = open('vips_group_b_branding.patch', 'w', encoding='utf-8')
    f_c = open('vips_group_c_logic.patch', 'w', encoding='utf-8')

    def write_block(group, block):
        if not block:
            return
        if group == 'A':
            f_a.writelines(block)
        elif group == 'B':
            f_b.writelines(block)
        elif group == 'C':
            f_c.writelines(block)
        files_count[group] += 1

    for line in lines:
        if line.startswith('diff --git '):
            # 直前までためていたブロックを出力
            write_block(current_group, current_block)
            current_block = [line]

            # diff --git a/path/to/file b/path/to/file からファイルパスを判定
            parts = line.split()
            if len(parts) >= 3:
                filepath_a = parts[2]
                current_group = get_group(filepath_a)
            else:
                current_group = 'A'
        else:
            current_block.append(line)

    # 最後のブロックを出力
    write_block(current_group, current_block)

    f_a.close()
    f_b.close()
    f_c.close()

    print("分割処理が正常に完了しました！")
    print(f"📁 グループA（メタ/ビルド） : vips_group_a_meta.patch ({files_count['A']} ファイル)")
    print(f"📁 グループB（UI/ブランド名）: vips_group_b_branding.patch ({files_count['B']} ファイル)")
    print(f"📁 グループC（本質ロジック） : vips_group_c_logic.patch ({files_count['C']} ファイル)")

if __name__ == '__main__':
    target = 'vips_custom.patch'  # デフォルトの入力ファイル名
    if len(sys.argv) > 1:
        target = sys.argv[1]
    split_patch(target)
