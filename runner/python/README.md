# Python exercise runner

Runtime profile `python-pytest`. The API copies a sandboxed workspace into the container:

```text
/workspace/
  <learner files>        # editable files from the exercise manifest
  <provided files>       # non-editable files from starter/ (helpers the exercise builds on)
  tests/                 # trusted hidden tests (test_*.py, conftest.py)
```

`run.sh` runs `pytest tests` with `PYTHONPATH=/workspace` and writes `target/surefire-reports/TEST-pytest.xml`. That is the same report location the Java runner uses, so `SurefireResultParser` reads both.

Build locally:

```bash
docker build -t neuralascent-python-runner:dev runner/python
```

The API picks the image from `ExerciseExecution__RunnerImagesByProfile__python_pytest`.
