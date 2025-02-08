from api.src.tasks import analyze_code_task
import requests


class DummyResponse:
    def __init__(self):
        self._json = {"issues": []}
    def json(self):
        return self._json


def fake_post_success(url, json):
    return DummyResponse()


def fake_post_failure(url, json):
    raise Exception("Simulated failure")


def test_task_success(monkeypatch):
    # Monkey patch requests.post to simulate a successful analysis
    monkeypatch.setattr(requests, "post", fake_post_success)
    result = analyze_code_task.apply(args=["/fake/path"]).get()
    assert result["status"] == "COMPLETED"


def test_task_failure(monkeypatch):
    # Monkey patch requests.post to simulate a failure in the task
    monkeypatch.setattr(requests, "post", fake_post_failure)
    result = analyze_code_task.apply(args=["/invalid"]).get()
    assert result["status"] == "FAILED" 