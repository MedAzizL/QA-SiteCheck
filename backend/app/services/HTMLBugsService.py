import requests

class HTMLBugsService:
    W3C_VALIDATOR_URL = "https://validator.w3.org/nu/"

    def analyze(self, html: str):
        try:
            
            response = requests.post(
                self.W3C_VALIDATOR_URL,
                params={'out': 'json'},
                data=html.encode('utf-8'),
                headers={"Content-Type": "text/html; charset=utf-8"},
            )
            response.raise_for_status()
        except requests.RequestException as e:
            return {"error": f"Validator API failed: {str(e)}"}

        try:
            data = response.json()
        except ValueError:
            return {"error": "Invalid JSON response from validator"}

        bugs = [
            {"type": msg.get("type"), "message": msg.get("message")}
            for msg in data.get('messages', [])
            if msg['type'] in ['error', 'warning']
        ]
        return bugs or [{"type": "info", "message": "No HTML bugs found"}]
