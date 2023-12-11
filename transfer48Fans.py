import time
import sys
from web3 import Web3
import json, os
from loguru import logger
import hashlib
from eth_account import Account
from GetIns import downloadInsData, fans_48_uri, downloadInsData, getAddrInsCount
from Fans48Utils import getAllValidateTransHash
logger.add(f'日志.txt')
web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/bsc'))  # 支持1gwei的rpc节点
def hash_text_md5(text):
    md5_hash = hashlib.md5()
    md5_hash.update(text.encode('utf-8'))
    return md5_hash.hexdigest()
def SendTransaction(txn, private_key, isWait=False):
    txn["chainId"] = 56
    signed_txn = web3.eth.account.signTransaction(txn, private_key)  # 用私钥签名交易
    tmp = web3.eth.sendRawTransaction(signed_txn.rawTransaction)  # 发送交易
    txhash = web3.toHex(web3.sha3(signed_txn.rawTransaction))
    if isWait:
        web3.eth.waitForTransactionReceipt(tmp)  # 等待交易完成 阻塞
    return txhash
def FromPrivateKeyToAddress(private_key):
    return Account.privateKeyToAccount(private_key)._address
def convertDataToHashes(result_hashes):
    allHashes = []
    for _, j in result_hashes.items():
        for i in j:
            allHashes.append(i)
    return allHashes
def transferIns(nonce,data,targetAddr, privateKey, isSendTransaction=False):
    address = FromPrivateKeyToAddress(privateKey)
    txn = {
        'from': web3.toChecksumAddress(address),
        'nonce': nonce,
        'to': web3.toChecksumAddress(targetAddr),
        'gas': int(3e5),
        'gasPrice': web3.toWei(3, 'gwei'),
        'data': data,
    }
    if isSendTransaction:
        tx = SendTransaction(txn, privateKey, isWait=False)
        print("data=>",data,nonce, tx)
    else:
        gas = web3.eth.estimateGas(txn)
        print(gas)
if __name__=="__main__":
    pk = '填写你的私钥'
    targetAddr = '填写目标地址'
    transferNum = 100 # 这里填写转账数量

    myAddr = FromPrivateKeyToAddress(pk)
    allInsNum = getAddrInsCount(myAddr, 50, uri=fans_48_uri)
    print(f'allInsNum=>{allInsNum}')
    cishu = int(allInsNum / 50)

    name = hash_text_md5(f"{cishu}_{myAddr}.json")


    js = downloadInsData(cishu, addr=myAddr, uri=fans_48_uri) # 每次转账前都要下载最新数据
    with open(f'{name}', 'w', encoding='utf-8') as f:
        f.write(json.dumps(js))
    logger.debug(f'下载[{int(len(js)*50)}]个hash成功')
    hashes0 = convertDataToHashes(js)
    validateHashes = getAllValidateTransHash(myAddr,hashes0)

    initNonce = web3.eth.getTransactionCount(myAddr)
    ct = 0
    for i in validateHashes:
        try:
            transferIns(initNonce+ct, i, targetAddr, pk, True)
            ct += 1
            time.sleep(3) # 等待3s
            if ct >= transferNum:
                print(f'转账完毕ct:{ct}')
                break
        except Exception as e:
            logger.debug(f'处理转账时发生错误=>{e}')
            time.sleep(12)
