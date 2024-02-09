from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjbGllbnRjaGFybGVzQGVtYWlsLmNvbSIsImlkIjoiODhkZTliYjEtMDE0ZS00YWNmLTgwNWEtZWYyODkwODJiMzRlIiwicm9sZSI6InVzZXIiLCJleHAiOjE3Mzg5NjM2ODh9.Xla4j_oVLSImFYlURueUGRfw6bVwv_9MN8E56Y4Qzk8"
            var ws = new WebSocket(`ws://localhost:8888/ws`);
            ws.setRequestHeader('Authorization:', token);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)
