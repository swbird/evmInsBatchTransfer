import json

import requests
from pprint import pprint
from web3.auto import Web3
from loguru import logger
evmInkGraphQl = 'https://api.evm.ink/v1/graphql/'

bsci_URL = '\\x646174613a2c7b2270223a226273632d3230222c226f70223a226d696e74222c227469636b223a2262736369222c22616d74223a2231303030227d'
# 此处可改为任意的 mint data以转账不同的铭文

def getAddrIns(allInfo,addr:str,offset,uri=bsci_URL, limit=50):
    payload = {
      "query": "query GetUserInscriptions($limit: Int, $offset: Int, $order_by: [inscriptions_order_by!] = {}, $where: inscriptions_bool_exp = {}, $whereAggregate: inscriptions_bool_exp = {}) {\n  inscriptions_aggregate(where: $whereAggregate) {\n    aggregate {\n      count\n    }\n  }\n  inscriptions(limit: $limit, offset: $offset, order_by: $order_by, where: $where) {\n    block_number\n    confirmed\n    content_uri\n    created_at\n    creator_address\n    owner_address\n    trx_hash\n    id\n    position\n    category\n    mtype\n    internal_trx_index\n    network_id\n    brc20_command {\n      reason\n      is_valid\n    }\n  }\n}",
      "variables": {
        "limit": limit,
          'offset': offset,
        "order_by": [
          {
            "position": "desc"
          }
        ],
        "whereAggregate": {
          "owner_address": {
            "_eq": addr.lower()
          },
            "content_uri": {
                "_eq":uri
            },
          "network_id": {
            "_eq": "eip155:56"
          }
        },
        "where": {
          "owner_address": {
            "_eq": addr.lower()
          },
            "content_uri": {
                "_eq": uri
            },
          "network_id": {
            "_eq": "eip155:56"
          }
        }
      },
      "operationName": "GetUserInscriptions"
    }
    res = requests.post(evmInkGraphQl, json=payload)
    # print(res.text)
    inscriptions = res.json()['data']['inscriptions']

    print("获取到的hash个数=>",len(inscriptions))
    # print(inscriptions)
    hashes = [i['trx_hash'] for i in inscriptions]
    allInfo[offset] = hashes
    # pprint(allInfo)


def downloadInsData(cishu, addr):
    allInfo = {}
    for i in range(cishu):  # 找出5000张记录
        try:
            getAddrIns(allInfo,addr, offset=50 * i)
        except Exception as  e:

            logger.debug(f'下载数据时出错=>{str(e)}')
    with open(f'owner_{addr}_{cishu * 50}.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(allInfo, ensure_ascii=False, indent=4))
    return allInfo
if __name__ == '__main__':
    addr = ''
    cishu = 100

    downloadInsData(cishu, addr)