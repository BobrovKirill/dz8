from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import os
from requests import get, put
import urllib.parse
import json


def run(handler_class=BaseHTTPRequestHandler):
    server_address = ('', 8008)
    httpd = HTTPServer(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


class HttpGetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        def fname2html(fname):
            return f"""
                <li>
                    <button onclick="fetch('/upload', {{'method': 'POST', 'body': '{fname}'}})" style="{'background-color: rgba(0, 200, 0, 0.25);' if has_item_in_list(fname) else ''} cursor: pointer;">
                        {fname}
                    </button>
                </li>
            """

        def has_item_in_list(item):
            return item in files_from_server

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        resp = get(f"https://cloud-api.yandex.net/v1/disk/resources/files",
                   headers={"Authorization": "OAuth y0_AgAAAAB68_zDAADLWwAAAAEdGLclAACrwZuQibJMwbh1on0yJskTnqYk9w"})
        files_from_server = [obj['name'] for obj in json.loads(resp.text)["items"]]
        self.end_headers()
        self.wfile.write("""
            <html>
                <head>
                </head>
                <body>
                    <main style="display: flex; align-items:center; justify-content: center; height: 100vh; width: 100%;">
                        <ul style="display: flex; gap: 8px; list-style: none;">
                          {files}
                        </ul>
                    </main>
                </body>
            </html>
        """.format(files="\n".join(map(fname2html, os.listdir("files")))).encode())

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        fname = self.rfile.read(content_len).decode("utf-8")
        local_path = f"files/{fname}"
        ya_path = f"images/{urllib.parse.quote(fname)}"
        resp = get(f"https://cloud-api.yandex.net/v1/disk/resources/upload?path={ya_path}",
                   headers={"Authorization": "OAuth y0_AgAAAAB68_zDAADLWwAAAAEdGLclAACrwZuQibJMwbh1on0yJskTnqYk9w"})
        print(resp.text)
        upload_url = json.loads(resp.text)["href"]
        print(upload_url)
        resp = put(upload_url, files={'file': (fname, open(local_path, 'rb'))})
        print(resp.status_code)
        self.send_response(200)
        self.end_headers()


run(handler_class=HttpGetHandler)