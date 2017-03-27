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

