from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>News NIT IIT - Sponsor Engine</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0F172A; color: #F8FAFC; padding: 50px; text-align: center; }
                .card { background: #1E293B; border-radius: 12px; padding: 30px; max-width: 600px; margin: 0 auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
                h1 { color: #38BDF8; }
                a.button { display: inline-block; background: #2563EB; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🚀 News NIT IIT Sponsor Engine</h1>
                <p>The backend API service is running on Vercel.</p>
                <p>Streamlit interactive dashboards run on Streamlit Cloud or local environment.</p>
                <a class="button" href="https://share.streamlit.io/" target="_blank">Deploy Streamlit Dashboard (1-Click Free)</a>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
