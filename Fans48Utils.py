import time
import sys

import requests
from web3 import Web3
import json
from loguru import logger
from eth_account import Account
from web3.middleware import geth_poa_middleware
from GetIns import downloadInsData
logger.add(f'日志.txt',encoding='utf-8')
web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/bsc'))  # 最好是本地全节点
web3NodeReal = Web3(Web3.HTTPProvider('https://rpc.ankr.com/bsc')) # 此处要修改为 存档节点
web3.middleware_onion.inject(geth_poa_middleware, layer=0)
web3NodeReal.middleware_onion.inject(geth_poa_middleware, layer=0)


validateInput = '0x646174613a2c7b2270223a22626e622d3438222c226f70223a226d696e74222c227469636b223a2266616e73222c22616d74223a2231227d'

validator48 = web3.toChecksumAddress('0x72b61c6014342d914470eC7aC2975bE345796c2b')
minBlock = 34175786
maxBlock = 34183076
step = 10 #  10个区块一个间隔
BlockRanges = list(range(minBlock, maxBlock+1))
blockInfoDict = {} # 扫块 吧

def getAllhash(addr):
    url = f'http://172.93.101.78/?addr={addr}'
    return requests.get(url).json()
def getAllValidateTransHash(addr, hashes: list):
    addr = web3.toChecksumAddress(addr)
    count = 0
    all_validate_mint_hashes = getAllhash(addr)
    all_validate_hashes = []
    print(f'获取到总的合法hash:{len(all_validate_hashes)}条')
    for i in hashes:
        # print(i)
        if i in all_validate_mint_hashes:
            print(f'√hash=>{i}')
            count+=1
            all_validate_hashes.append(i)
    print(f'count=>{count}')
    return all_validate_hashes

def SweepBlock(): # 抓取所有符合的mint事件
    # key: addr value: [hashlist]
    dict = {
    }
    for blockNumber in BlockRanges:
        while True:
            try:
                blockinfo = web3NodeReal.eth.getBlock(blockNumber, False)
                break
            except Exception as e:
                logger.debug(f'请求nodereal出错=>{e}')
                time.sleep(10)
        miner = web3.toChecksumAddress(blockinfo['miner'])
        transactions = blockinfo['transactions']
        transactions = [i.hex() for i in transactions]
        if miner!=validator48: # 如果验证者不是48 直接跳过
            continue
        print(miner, transactions)
        for transaction in transactions:
            try:
                print(transaction)
                receipt = web3.eth.getTransaction(transaction)
                fromAddr = web3.toChecksumAddress(receipt['from'])
                toAddr = web3.toChecksumAddress(receipt['to'])
                inputData = receipt['input']

                if inputData==validateInput and fromAddr==toAddr: # 满足自转 并且input是mint铭文的16进制
                    print(fromAddr, toAddr, inputData)
                    if dict.get(fromAddr)==None: # 第一次
                        dict[fromAddr] = [transaction]
                    else:
                        tmp = dict[fromAddr]
                        tmp.append(transaction)
                        dict[fromAddr] = tmp # 更新交易列表
            except Exception as e:
                logger.debug(f'{e}')




            # print(receipt)
        # input('')
    with open('finalResult.json', 'w',encoding='utf-8') as f:
        f.write(json.dumps(dict,ensure_ascii=False,indent=4))


if __name__ == '__main__':
    # pass

    # SweepBlock()


    pass

