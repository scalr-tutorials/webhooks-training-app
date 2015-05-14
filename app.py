#coding:utf-8
import json
import os
import logging
import collections
import datetime

import flask

import middleware

# App Global Configuration
SIGNING_KEY_ENV_VAR = "SIGNING_KEY"
REQUESTS_LOG_DEPTH = 5

# Log to stdout / stderr
stderr_log_handler = logging.StreamHandler()


RequestLogEntry = collections.namedtuple("RequestLogEntry", ["ts", "body"])


def make_app():
    ##############################
    # Configure from environment #
    ##############################

    app = flask.Flask(__name__)
    app.config.update(
        signing_key=os.environ.get(SIGNING_KEY_ENV_VAR, ""),
        )

    #################
    # Setup logging #
    #################

    app.logger.addHandler(stderr_log_handler)
    app.logger.setLevel(logging.DEBUG)

    ###############################################
    # Prepare in-memory store for the request log #
    ###############################################

    requests_log = collections.deque(maxlen=REQUESTS_LOG_DEPTH)

    ##############
    # Middleware #
    ##############

    app.before_request(middleware.validate_request_signature)
    app.before_request(middleware.validate_json_payload)
    app.before_request(middleware.log_request)

    #########
    # Views #
    #########

    @app.route("/", methods=("GET",))
    def webhook_get_handler():
        return flask.render_template("history.html", requests_log=requests_log)

    @app.route("/", methods=("POST",))
    def webhook_post_handler():
        payload = flask.request.json
        app.logger.info("Received Notification '%s' for: '%s' on '%s'", payload["eventId"],
                        payload["eventName"], payload["data"]["SCALR_SERVER_ID"])

        # Redact non-Scalr variables in the payload (being safe)
        for k, v in payload["data"].items():
            if not k.startswith("SCALR_"):
                payload["data"][k] = "*" * 12  # No particular reason for using 12; it just reflects "redacted" well.

        # Log this payload
        requests_log.append(RequestLogEntry(datetime.datetime.utcnow(), payload))

        return flask.Response(status=202)

    ####################
    # Template Filters #
    ####################

    @app.template_filter('to_pretty_json')
    def to_pretty_json(obj):
        return json.dumps(obj, indent=2).strip()


    return app

def main():
    app = make_app()
    app.run(debug=True)


if __name__ == '__main__':
    main()
