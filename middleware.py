# coding:utf-8
import hashlib
import hmac
import flask
import util


def validate_request_signature():
    if flask.request.method == "GET":
        return

    signing_key = flask.current_app.config["signing_key"]
    if not signing_key:
        flask.current_app.logger.warning("No signing key found. Request will not be checked for authenticity.")
        return

    payload = flask.request.get_data()
    date = flask.request.headers.get("Date", "")
    message_hmac = hmac.HMAC(signing_key, payload + date, hashlib.sha1)

    local_signature = message_hmac.hexdigest()
    remote_signature = flask.request.headers.get("X-Signature", "")

    if not util.constant_time_compare(local_signature, remote_signature):
        flask.current_app.logger.warning("Detected invalid signature, aborting.")
        return flask.Response(status=403)


def validate_json_payload():
    if flask.request.method == "GET":
        return
    if flask.request.json is None:
        return flask.Response(status=400)


def log_request():
    flask.current_app.logger.debug("Received request: %s %s", flask.request.method, flask.request.url)
