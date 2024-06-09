from flask import Flask, render_template, request

# __name__ = file name
app = Flask(__name__)

@app.route('/')
def index():
    url = request.args.get('src-url')
    output = ['пусто', 'пусто', 'пусто', 'пусто', 'пусто', 'пусто', 'пусто',]
    
    return render_template('index.html', title='Парсер', button='Запарсить')


if __name__ == "__main__":
    app.run(debug=True)


