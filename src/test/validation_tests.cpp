// Copyright (c) 2014-2021 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <chainparams.h>
#include <consensus/amount.h>
#include <net.h>
#include <validation.h>

#include <test/util/setup_common.h>

#include <boost/test/unit_test.hpp>

// VIPS PoS Reward Function Declaration to prevent compile-time missing error
CAmount GetProofOfStakeReward(int nHeight, const Consensus::Params& consensusParams);

BOOST_FIXTURE_TEST_SUITE(validation_tests, TestingSetup)

BOOST_AUTO_TEST_CASE(block_subsidy_test)
{
    const auto chainParams = CreateChainParams(*m_node.args, CBaseChainParams::MAIN);
    Consensus::Params consensusParams = chainParams->GetConsensus();

    // VIPS PoW Block Subsidy (GetBlockSubsidy) Verification
    BOOST_CHECK_EQUAL(GetBlockSubsidy(1, consensusParams), 10000000000ULL * COIN);
    BOOST_CHECK_EQUAL(GetBlockSubsidy(2, consensusParams), 1 * COIN);
    BOOST_CHECK_EQUAL(GetBlockSubsidy(100, consensusParams), 10000000000ULL * COIN);
    BOOST_CHECK_EQUAL(GetBlockSubsidy(2000, consensusParams), 1 * COIN);
    BOOST_CHECK_EQUAL(GetBlockSubsidy(2001, consensusParams), 100 * COIN);
    BOOST_CHECK_EQUAL(GetBlockSubsidy(100000, consensusParams), 100 * COIN);

    // VIPS PoS Block Reward (GetProofOfStakeReward) Verification
    BOOST_CHECK_EQUAL(GetProofOfStakeReward(1, consensusParams), 9500 * COIN); // Will output 1 COIN inside actual ConnectBlock, but raw is 9500
    BOOST_CHECK_EQUAL(GetProofOfStakeReward(2000, consensusParams), 1 * COIN);
    BOOST_CHECK_EQUAL(GetProofOfStakeReward(2001, consensusParams), 3000 * COIN);
    BOOST_CHECK_EQUAL(GetProofOfStakeReward(28000, consensusParams), 3000 * COIN);
    BOOST_CHECK_EQUAL(GetProofOfStakeReward(28001, consensusParams), 9500 * COIN);

    // Halving schedule (every 525,600 blocks)
    BOOST_CHECK_EQUAL(GetProofOfStakeReward(500000, consensusParams), 9500 * COIN); // Year 1
    BOOST_CHECK_EQUAL(GetProofOfStakeReward(600000, consensusParams), 4750 * COIN); // Year 2
    BOOST_CHECK_EQUAL(GetProofOfStakeReward(1200000, consensusParams), 2375 * COIN); // Year 3
    BOOST_CHECK_EQUAL(GetProofOfStakeReward(5000000, consensusParams), 100 * COIN); // Hard floor-limit (100 VIPS)
}

BOOST_AUTO_TEST_CASE(subsidy_limit_test)
{
    // Verify maximum VIPS money supply limit
    BOOST_CHECK_EQUAL(MAX_MONEY, 70000000000ULL * COIN);
}

BOOST_AUTO_TEST_SUITE_END()
