# Copyright (c) 2023-present The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

function(generate_setup_nsi)
  set(abs_top_srcdir ${PROJECT_SOURCE_DIR})
  set(abs_top_builddir ${PROJECT_BINARY_DIR})
  set(CLIENT_URL ${PROJECT_HOMEPAGE_URL})
  # VIPS: URIスキーム名(qt/guiutil.cpp parseBitcoinURI)と一致させる
  set(CLIENT_TARNAME "vipstarcoin")
  # VIPS: 統合バイナリのブランド名称(Step5ゆう最終判断#5、src/CMakeLists.txt
  # のOUTPUT_NAMEと一致させる)
  set(BITCOIN_WRAPPER_NAME "vipstarcoin")
  set(BITCOIN_GUI_NAME "vipstarcoin-qt")
  set(BITCOIN_DAEMON_NAME "vipstarcoind")
  set(BITCOIN_CLI_NAME "vipstarcoin-cli")
  set(BITCOIN_TX_NAME "vipstarcoin-tx")
  set(BITCOIN_WALLET_TOOL_NAME "vipstarcoin-wallet")
  # VIPS: BITCOIN_TEST_NAMEはsetup.nsi.in内で未使用のため削除
  # (--disable-tests運用と整合、v27.1時代のsetup.nsi.inでも同様に削除済み)
  set(EXEEXT ${CMAKE_EXECUTABLE_SUFFIX})
  configure_file(${PROJECT_SOURCE_DIR}/share/setup.nsi.in ${PROJECT_BINARY_DIR}/qtum-win64-setup.nsi USE_SOURCE_PERMISSIONS @ONLY)
endfunction()
