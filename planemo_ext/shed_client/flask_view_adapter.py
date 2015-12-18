try:
    from flask import Flask
except ImportError:
    Flask = None

app = Flask(
    __name__,
    static_url_path='/static',
)


if __name__ == '__main__':
    app.run(debug=True)
