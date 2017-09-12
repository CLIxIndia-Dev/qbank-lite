[![Build Status](https://travis-ci.org/CLIxIndia-Dev/qbank-lite.svg?branch=master)](https://travis-ci.org/CLIxIndia-Dev/qbank-lite)[![Coverage Status](https://coveralls.io/repos/github/CLIxIndia-Dev/qbank-lite/badge.svg?branch=master)](https://coveralls.io/github/CLIxIndia-Dev/qbank-lite?branch=master)

Running
=========================
QBank runs by default with `https` on port `8080`, with

```
python main.py
```

You can pass a different port into the arguments:

```
python main.py 8888
```


Bundling for distribution
=========================

```
pyinstaller main.spec
```

When bundled, qbank runs by default on port `8080`. To change this, you need to modify the
code in `main.py` and manually inject `sys.argv[1] = <new port #>` before `app.run()`.


Running with Docker
===================
The docker images built with this repository use the filesystem
to store data, in an unplatform-type scenario. If you want to run against
MongoDB, you have to modify the image / Dockerfile / docker-compose files
for that configuration.

You can find the public docker images at `clixtech/qbank`. To build it locally, install [Docker for your OS](https://docs.docker.com/engine/installation/#supported-platforms), v17+. Then run from the project root directory.

```
docker build -t <image name> .
```

Once you have an image, you can run the code:

```
docker run -p 8080:8080 <image name>
```
And in your browser, navigate to `https://localhost:8080/version` to verify that the `qbank` service is running. There is no data as part of the image, so you will see no banks, assessments, etc.

For development purposes, where your live code edits will reflect in the
browser, you can run with `docker-compose`:

Run this once, initially, and whenever the `requirements.txt` or
`test_requirements.txt` files change:
```
docker-compose build
```

To start `qbank`, you can then run:
```
docker-compose up
```

And in your browser, navigate to `https://localhost:8080/version` to verify
that the `qbank` service is running.
