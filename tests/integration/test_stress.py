from api.src.tasks import analyze_code_task


def test_high_concurrency_with_diverse_projects():
    paths = ["tests/sample_project", "tests/large_project"] * 10
    tasks = [analyze_code_task.delay(p) for p in paths]
    results = [t.get(timeout=60) for t in tasks]
    assert sum(1 for r in results if r["status"] == "COMPLETED") >= 18 