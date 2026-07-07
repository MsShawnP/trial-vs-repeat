"""Thin entry point — named wsgi.py to avoid an import collision with the app/ package."""

import os

from dotenv import load_dotenv
from flask import jsonify

load_dotenv()

from app.app import server  # noqa: E402
from app.layout import register_layout  # noqa: E402

register_layout()


@server.route("/health")
def health():
    """Liveness check for the Fly proxy.

    Leaky Bucket has NO database — its data is the in-process, seed-locked panel
    warmed at startup. A 200 here means the process is up and serving; there is
    nothing else to gate on. Deliberately never returns non-200 for a data reason,
    so a transient issue can never pull the machine from the proxy (the Spin Rate
    503 bug, designed out — same call as Decompose).
    """
    return jsonify(status="ok"), 200


if __name__ == "__main__":
    from app.app import app

    app.run(
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
        use_reloader=False,
        port=int(os.environ.get("PORT", 8050)),
    )
