
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
from web3.auto import w3
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # 解析查询参数
        query_components = parse_qs(urlparse(self.path).query)
        addr = query_components.get('addr', [''])[0]  # 获取addr参数的值

        # 读取JSON文件
        with open('finalResult.json', 'r') as file:
            data = json.load(file)

        # 查找对应的值
        response = data.get(w3.toChecksumAddress(addr), [])

        # 发送响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

# 设置服务器和端口
httpd = HTTPServer(('0.0.0.0', 80), SimpleHTTPRequestHandler)

# 启动服务器
print("Serving at port 80")
httpd.serve_forever()