import http.server
import socketserver
import urllib.parse
import json
import os

import unified_resolver

PORT = 8089

class MarketplaceAPIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        def get_param(key, default=None):
            return query.get(key, [default])[0]

        try:
            if path == "/api/states":
                res = unified_resolver.resolve_get_states()
                self._send_json(200, {"states": res})
            elif path == "/api/insurance-types":
                st = get_param("state")
                res = unified_resolver.legacy_repository.get_insurance_types(st) if os.getenv("DATA_SOURCE")=="legacy" else unified_resolver.db_repository.get_insurance_types(st)
                self._send_json(200, {"insurance_types": res})
            elif path == "/api/insurers":
                st = get_param("state")
                itype = get_param("type")
                res = unified_resolver.db_repository.get_insurers(st, itype) if os.getenv("DATA_SOURCE")=="database" else unified_resolver.legacy_repository.get_insurers(st, itype)
                self._send_json(200, {"insurers": res})
            elif path == "/api/plans":
                st = get_param("state")
                itype = get_param("type")
                ins = get_param("insurer")
                res = unified_resolver.resolve_get_plans(st, itype, ins)
                self._send_json(200, {"plans": res})
            elif path.startswith("/api/plans/") and path.endswith("/coverage"):
                parts = path.split("/")
                plan_id = parts[3]
                year = int(get_param("year", 2026))
                res = unified_resolver.resolve_get_plan_coverage(plan_id, year)
                self._send_json(200, {"plan_id": plan_id, "year": year, "rules": res})
            elif path.startswith("/api/plans/"):
                parts = path.split("/")
                plan_id = parts[3]
                year = int(get_param("year", 2026))
                res = unified_resolver.resolve_get_plan(plan_id, year)
                if not res:
                    self._send_json(404, {"error": "Plan not found", "plan_id": plan_id})
                else:
                    self._send_json(200, res)
            elif path.startswith("/api/coverage/") and path.endswith("/evidence"):
                parts = path.split("/")
                rule_id = parts[3]
                res = unified_resolver.resolve_get_rule_evidence(rule_id)
                if not res:
                    self._send_json(404, {"error": "Evidence not found", "rule_id": rule_id})
                else:
                    self._send_json(200, res)
            elif path == "/api/admin/progress":
                res = unified_resolver.db_repository.get_admin_progress()
                self._send_json(200, res)
            else:
                self._send_json(404, {"error": "Endpoint not found"})
        except Exception as e:
            self._send_json(500, {"error": f"Internal Server Error: {str(e)}"})

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MarketplaceAPIHandler) as httpd:
        print(f"Marketplace API Server running on port {PORT}...")
        httpd.serve_forever()
