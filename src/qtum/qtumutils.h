#ifndef QTUMUTILS_H
#define QTUMUTILS_H

#include <libdevcore/Common.h>
#include <libdevcore/FixedHash.h>
#include <libdevcore/Address.h>
#include <util/chaintype.h>

class CBlockIndex;

/**
 * qtumutils Provides utility functions to EVM for functionalities that already exist in qtum
 */
namespace qtumutils
{
/**
 * @brief btc_ecrecover Wrapper to CPubKey::RecoverCompact
 */
bool btc_ecrecover(dev::h256 const& hash, dev::u256 const& v, dev::h256 const& r, dev::h256 const& s, dev::h256 & key);


/**
 * @brief The ChainIdType enum Chain Id values for the networks
 *
 * VIPS: LEGACY is the pre-Shanghai chain id (Qtum-derived, 0x51/81),
 * returned for ALL networks while blockHeight < shanghaiHeight, to
 * preserve exact backward compatibility with VIPS mainnet's existing
 * on-chain history (unaffected by the fact that nShanghaiHeight is
 * currently disabled on mainnet/testnet). MAIN/TESTNET/REGTEST below are
 * VIPS-specific chain ids (BIP44 coin type 1919 for mainnet) that only
 * take effect once Shanghai activates for a given network (see
 * eth_getChainId()). They must never be returned for pre-Shanghai
 * blocks, or they would silently and retroactively change the CHAINID
 * opcode's result for already-mined blocks -- a consensus-breaking
 * change indistinguishable from a hard fork.
 */
enum ChainIdType
{
    LEGACY = 81,
    MAIN = 1919,
    TESTNET = 19191,
    REGTEST = 19192,
};

/**
 * @brief eth_getChainId Get eth chain id
 * @param blockHeight Block height
 * @param shanghaiHeight Shanghai fork height
 * @param chain Network ID
 * @return chain id
 */
int eth_getChainId(int blockHeight, int shanghaiHeight, const ChainType& chain);

/**
 * @brief eth_getChainId Get eth chain id and cache it
 * @param blockHeight Block height
 * @return chain id
 */
int eth_getChainId(int blockHeight);

/**
 * @brief eth_getHistoryStorageAddress Get eth history storage address
 * @return Return history storage address
 */
dev::Address eth_getHistoryStorageAddress();

/**
 * @brief The HistoricalHashes class Store the historical hashes
 */
class HistoricalHashes
{
public:
    /**
     * @brief instance Get instance from the historical hashages storage
     * @return Instance of the storage
     */
    static HistoricalHashes& instance();

    /**
     * @brief set Set the most recent block index
     * @param tip Block index for the tip
     */
    void set(CBlockIndex* tip);

    /**
     * @brief get Get the block hash from the history window
     * @param blockHeight Input block height
     * @param hash Output hash
     * @return true if found the hash, false if not found
     */
    bool get(const dev::u256& blockHeight, dev::h256& hash);

private:
    // Private constructor, copy constructor and operator equal for singleton
    HistoricalHashes();
    HistoricalHashes(const HistoricalHashes&) = delete;
    HistoricalHashes& operator=(const HistoricalHashes&) = delete;

private:
    /**
     * @brief clear Clear the hashes
     */
    void clear();

    /**
     * @brief update Update the hashes from the tip
     */
    void update();

    /**
     * @brief needUpdate Check if update is needed
     * @return true if needed, otherwise false
     */
    bool needUpdate();

private:
    const static int m_historyWindow = 8191;
    std::map<int, dev::h256> m_hashes;
    CBlockIndex* m_tip = 0;
};

}

#endif
