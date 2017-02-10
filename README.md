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

