import react
import json
from reactives import ReactiveValues, Observer
from fastapi import WebSocket, WebSocketDisconnect

class ShinySession:
    def __init__(self, app: 'ShinyApp', id: int) -> None:
        self._app = app
        self.id: int = id
        self._message_queue: list[str] = []

        self.input = ReactiveValues()
        self.output = Outputs(self)

        self._app.server(self.input, self.output)

    # Pending messages
    def add_message(self, message: str):
        self._message_queue.append(message)

    def get_messages(self) -> list[str]:
        return self._message_queue

    def clear_messages(self) -> None:
        self._message_queue.clear()

    async def listen(self, websocket: WebSocket) -> None:
        try:
            while True:
                line = await websocket.receive_text()
                if not line:
                    break

                print("RECV: " + line)

                vals = json.loads(line)
                for (key, val) in vals.items():
                    self.input[key] = val

                react.flush()

                for message in self.get_messages():
                    message_str = json.dumps(message) + "\n"
                    print("SEND: " + message_str, end = "")
                    await websocket.send_text(message_str)

                self.clear_messages()

        except WebSocketDisconnect:
            pass


class Outputs:
    def __init__(self, session: ShinySession):
        self._output_obervers = {}
        self._session = session

    def set(self, name):
        def set_fn(fn):
            if name in self._output_obervers:
                self._output_obervers[name].destroy()

            @Observer
            def obs():
                message = {}
                message[name] = fn()
                self._session.add_message(message)

            self._output_obervers[name] = obs

            return None

        return set_fn

    def get(self, name):
        return self._fns[name]

