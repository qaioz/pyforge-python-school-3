import http.client
import json


def _parse_base_url(url):
    # Assuming base_url is of the form "http://localhost:6969"
    if "http://" in url:
        url = url.replace("http://", "")
    host, port = url.split(":")
    return host, int(port)


class HTTPDatabaseClient:
    # TODO: Currently only the necessary methods for molecule repository are implemented. Implement the rest of the
    #  methods.
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.host, self.port = _parse_base_url(self.base_url)

    def _request(self, method, path, body=None) -> http.client.HTTPResponse:
        conn = http.client.HTTPConnection(self.host, self.port)
        headers = {'Content-Type': 'application/json'}
        json_body = json.dumps(body) if body else None
        conn.request(method, path, body=json_body, headers=headers)
        response = conn.getresponse()
        conn.close()
        return response

    def create_collection(self, collection_name: str) -> http.client.HTTPResponse:
        return self._request("POST", "/collections", {"name": collection_name})

    def delete_collection(self, collection_name: str) -> http.client.HTTPResponse:
        return self._request("DELETE", f"/collections/{collection_name}")

    def add_document(self, collection_name: str, document: dict) -> http.client.HTTPResponse:
        return self._request("POST", f"/collections/{collection_name}/documents", document)

    def update_document(self, collection_name: str, document_id: str, document: dict) -> http.client.HTTPResponse:
        return self._request("PUT", f"/collections/{collection_name}/documents/{document_id}", document)

    def delete_document(self, collection_name, document_id):
        return self._request("DELETE", f"/collections/{collection_name}/documents/{document_id}")

    def get_documents(self, collection_name):
        return self._request("GET", f"/collections/{collection_name}/documents")

