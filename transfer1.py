import time
import sys
from web3 import Web3
import json
from loguru import logger
from eth_account import Account
from GetIns import downloadInsData
logger.add(f'日志.txt')
web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/bsc'))  # 支持1gwei的rpc节点
gasPrcie = 3 # 3gwei
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

def transferIns(nonce,data,targetAddr, privateKey, isSendTransaction=False):
    address = FromPrivateKeyToAddress(privateKey)
    txn = {
        'from': web3.toChecksumAddress(address),
        'nonce': nonce,
        'to': web3.toChecksumAddress(targetAddr),
        'gas': int(3e5),
        'gasPrice': web3.toWei(gasPrcie, 'gwei'),
        'data': data,
    }
    if isSendTransaction:
        tx = SendTransaction(txn, privateKey, isWait=False)
        print("data=>",data,nonce, tx)
    else:
        gas = web3.eth.estimateGas(txn)
        print(gas)
if __name__=="__main__":
    delay = 2 # 每次转账间隔2s
    pk = input('输入私钥:\n')
    gasPrcie = int(input("输入gasPrice:\n"))
    targetAddr = input('输入目标地址:\n')
    transferNum = int(input('输入转账数量:\n') )# 这里填写转账数量
    cishu = int(transferNum/50)
    nonce = web3.eth.getTransactionCount(FromPrivateKeyToAddress(pk))
    myAddr = FromPrivateKeyToAddress(pk)

    js = downloadInsData(cishu, addr=myAddr)
    logger.debug(f'下载[{int(len(js)*50)}]个hash成cm功')
    initNonce = web3.eth.getTransactionCount(myAddr)
    ct = 0

    for k,v in js.items():
        for i in v:
            try:
                transferIns(initNonce+ct, i, targetAddr, pk, True)
                ct += 1
                time.sleep(delay)
            except Exception as e:
                logger.debug(f'处理转账时发生错误=>{e}')
                time.sleep(12)
    input('done.')