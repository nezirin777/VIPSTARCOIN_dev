#ifndef QTUMUTILS_H
#define QTUMUTILS_H

#include <libdevcore/Common.h>
#include <libdevcore/FixedHash.h>

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
int eth_getChainId(int blockHeight, int shanghaiHeight, const std::string& chain);

/**
 * @brief eth_getChainId Get eth chain id and cache it
 * @param blockHeight Block height
 * @return chain id
 */
int eth_getChainId(int blockHeight);

}

#endif
