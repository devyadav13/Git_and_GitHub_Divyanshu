# Local verification test

`test_success_path.py` uses the `mongomock` package (an in-memory fake of
MongoDB) to verify the `/submit` route's success flow (insert + redirect to
`/success`) without needing live Atlas credentials.

Run it with:
```
pip install -r requirements-test.txt
python test_success_path.py
```

This is a developer convenience script only — it is not part of the Flask
application itself.
