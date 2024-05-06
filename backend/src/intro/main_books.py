from flask import Flask, jsonify, request

app = Flask(__name__)

books = [
    {
        'id': 1,
        'title': 'Book 1',
        'author': 'Author 1'
    },
    {
        'id': 2,
        'title': 'Book 2',
        'author': 'Author 2'
    },
    {
        'id': 3,
        'title': 'Book 3',
        'author': 'Author 3'
    }
]


# Получение всех книг
@app.route('/api/books', methods=['GET'])
def get_books():
    return jsonify(books)


# Получение книги по id
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((item for item in books if item['id'] == book_id), None)
    if book:
        return jsonify(book)
    else:
        return jsonify({'message': 'Book not found'}), 404


# Добавление книги
@app.route('/api/books', methods=['POST'])
def create_book():
    new_book = {
        'id': len(books),
        'title': request.json['title'],
        'author': request.json['author']
    }
    books.append(new_book)
    return jsonify(new_book), 201


# Обновление информации
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((item for item in books if item['id'] == book_id), None)
    if book:
        book.update(request.json)
        return book
    else:
        return jsonify({'message': 'Book not found'}), 404


# Удаление книги
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = next((item for item in books if item['id'] == book_id), None)
    if book:
        books.remove(book)
        return jsonify({'message': 'Book deleted'})
    else:
        return jsonify({'message': 'Book not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
