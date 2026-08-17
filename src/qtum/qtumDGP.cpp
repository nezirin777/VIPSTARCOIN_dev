#include <qtum/qtumDGP.h>
#include <chainparams.h>

std::vector<uint32_t> createDataSchedule(const dev::eth::EVMSchedule& schedule)
{
    std::vector<uint32_t> tempData = {schedule.tierStepGas[0], schedule.tierStepGas[1], schedule.tierStepGas[2],
                                      schedule.tierStepGas[3], schedule.tierStepGas[4], schedule.tierStepGas[5],
                                      schedule.tierStepGas[6], schedule.tierStepGas[7], schedule.expGas,
                                      schedule.expByteGas, schedule.sha3Gas, schedule.sha3WordGas,
                                      schedule.sloadGas, schedule.sstoreSetGas, schedule.sstoreResetGas,
                                      schedule.sstoreRefundGas, schedule.jumpdestGas, schedule.logGas,
                                      schedule.logDataGas, schedule.logTopicGas, schedule.createGas,
                                      schedule.callGas, schedule.callStipend, schedule.callValueTransferGas,
                                      schedule.callNewAccountGas, schedule.selfdestructRefundGas, schedule.memoryGas,
                                      schedule.quadCoeffDiv, schedule.createDataGas, schedule.txGas,
                                      schedule.txCreateGas, schedule.txDataZeroGas, schedule.txDataNonZeroGas,
                                      schedule.copyGas, schedule.extcodesizeGas, schedule.extcodecopyGas,
                                      schedule.balanceGas, schedule.selfdestructGas, schedule.maxCodeSize};
    return tempData;
}

std::vector<uint32_t> scheduleDataForBlockNumber(unsigned int blockHeight)
{
    dev::eth::EVMSchedule schedule = globalSealEngine->chainParams().scheduleForBlockNumber(blockHeight);
    return createDataSchedule(schedule);
}

void QtumDGP::initDataSchedule(){
    dataSchedule = scheduleDataForBlockNumber(0);
}

bool QtumDGP::checkLimitSchedule(const std::vector<uint32_t>& defaultData, const std::vector<uint32_t>& checkData, int blockHeight){
    const Consensus::Params& consensusParams = Params().GetConsensus();

    if(defaultData.size() == 39 && (checkData.size() == 39 || (checkData.size() == 40 && blockHeight >= consensusParams.QIP7Height))) {
        for(size_t i = 0; i < defaultData.size(); i++){
            uint32_t max = defaultData[i] * 1000 > 0 ? defaultData[i] * 1000 : 1 * 1000;
            uint32_t min = defaultData[i] / 100 > 0 ? defaultData[i] / 100 : 1;
            if(checkData[i] > max || checkData[i] < min){
                return false;
            }
        }
        return true;
    }
    return false;
}

dev::eth::EVMSchedule QtumDGP::getGasSchedule(int blockHeight){
    clear();
    dataSchedule = scheduleDataForBlockNumber(blockHeight);

    return globalSealEngine->chainParams().scheduleForBlockNumber(blockHeight);
}

uint32_t QtumDGP::getBlockSize(unsigned int blockHeight){
    clear();
    return DEFAULT_BLOCK_SIZE_DGP / Params().GetConsensus().BlocktimeDownscaleFactor(blockHeight);
}

uint64_t QtumDGP::getMinGasPrice(unsigned int blockHeight){
    clear();
    return DEFAULT_MIN_GAS_PRICE_DGP;
}

uint64_t QtumDGP::getBlockGasLimit(unsigned int blockHeight){
    clear();
    return DEFAULT_BLOCK_GAS_LIMIT_DGP;
}
