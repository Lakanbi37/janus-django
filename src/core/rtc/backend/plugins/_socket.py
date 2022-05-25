from core.rtc.backend.plugins import JanusPlugin


class JanusSocketPlugin(JanusPlugin):

    def emit(self, _):
        _.update({"janus": "message", "handle_id": self._id})
        return self._session.send(_)
