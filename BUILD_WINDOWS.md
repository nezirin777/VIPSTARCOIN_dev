# VIPSTARCOIN — Windows向けクロスコンパイル ビルド手順

WSL2 (Ubuntu 22.04) + MinGW で `vipstarcoin-qt.exe` / `vipstarcoind.exe` を生成する手順です。

> **対象ブランチ**: `tooling/phase6-baseline`

---

## 前提条件

- WSL2 (Ubuntu 22.04 / jammy)
- 以下のパッケージがインストール済みであること

```bash
sudo apt-get install -y \
  build-essential libtool autotools-dev automake pkg-config \
  bsdmainutils curl git cmake \
  g++-mingw-w64-x86-64 mingw-w64-tools \
  python3
```

---

## ビルド手順

### 1. クローンとブランチ切り替え

```bash
git clone https://github.com/nezirin777/VIPSTARCOIN_dev.git VIPSTARCOIN_dev
cd VIPSTARCOIN_dev
git checkout tooling/phase6-baseline
git submodule update --init --recursive
```

### 2. WSL2環境の前処理

**Windowsパス汚染の排除**（`/mnt/c/...` 等が混入するとビルドが壊れる）

```bash
export PATH=$(echo $PATH | tr ':' '\n' | grep -v '^/mnt/' | tr '\n' ':')
```

**システムクロックの同期**（スリープ復帰後などにズレが生じることがある）

```bash
sudo hwclock -s
find . -type f -exec touch {} +
```

### 3. 依存パッケージ（depends）のビルド

```bash
cd depends
make HOST=x86_64-w64-mingw32 -j$(nproc) 2>&1 | tee ../depends_build.log
cd ..
```

> **補足**: OpenSSL 1.0.2u の `no-rc4` 等の問題フラグはコミット `2001cf366b` で修正済みのため、
> 本ブランチではそのまま完走します。

### 4. Autotools 構成と configure

```bash
./autogen.sh

CONFIG_SITE=$PWD/depends/x86_64-w64-mingw32/share/config.site \
./configure --host=x86_64-w64-mingw32 --prefix=/
```

> ⚠️ **`--host=x86_64-w64-mingw32` は必須です。**
> 省略すると `AC_CONFIG_SUBDIRS` 経由でビルドされる `src/univalue` が
> ネイティブ Linux (ELF) でコンパイルされ、C++ ABI ミスマッチによるリンクエラーが発生します。

### 5. 本体ビルド

```bash
make -j$(nproc) 2>&1 | tee build.log
```

成功すると以下が生成されます。

```
src/vipstarcoind.exe
src/vipstarcoin-cli.exe
src/qt/vipstarcoin-qt.exe
```

---

## トラブルシューティング

### OpenSSL: `No rule to make target '../../include/openssl/rc4.h'`

本ブランチでは修正済みですが、他ブランチで再現した場合は
`depends/packages/openssl.mk` から以下の8行を削除してください。

```
no-rc4 / no-idea / no-mdc2 / no-camellia / no-seed / no-cast / no-comp / no-whirlpool
```

**技術的背景**: OpenSSL 1.0.2 のリリース tarball に含まれる Makefile は静的に生成済みで、
`no-X` フラグで暗号を無効化しても、`crypto/engine/` や `crypto/evp/` の
依存定義にそのヘッダーへの参照が残ったままになるため。

### UniValue リンクエラー: `undefined reference to 'UniValue::write[abi:cxx11]'`

`--host` を省略して configure した場合に発生します。
以下で univalue のキャッシュを消してから、`--host` 付きで configure し直してください。

```bash
make -C src/univalue clean
rm -f src/univalue/libunivalue.la

CONFIG_SITE=$PWD/depends/x86_64-w64-mingw32/share/config.site \
./configure --host=x86_64-w64-mingw32 --prefix=/

make -j$(nproc) 2>&1 | tee build.log
```

**診断コマンド** — `libunivalue.a` が PE (Windows) か ELF (Linux) かを確認:

```bash
x86_64-w64-mingw32-objdump -f src/univalue/.libs/libunivalue.a | head -5
# 正常: file format pe-x86-64
# 異常: file format elf64-x86-64  ← --host が伝わっていない
```

### `configure: error: newly created file is older than distributed files!`

WSL2のクロック遅延が原因です。

```bash
sudo hwclock -s
find . -type f -exec touch {} +
```

---

## 補足: RPC エンドポイント (本ブランチ独自)

本ブランチには `getreplaybaseline <height>` RPC が追加されています。
フルブロックリプレイ用のベースラインデータ抽出に使用します。

```bash
# 動作確認
vipstarcoin-cli -rpcuser=nezirin -rpcpassword=eclipse getreplaybaseline 0
```

ベースラインデータの一括抽出は `extract_baseline.js` を使用してください。

```bash
RPC_USER=nezirin RPC_PASS=eclipse node extract_baseline.js
```
