needs virtualenv

  virtualenv .venv

  source .venv/bin/activate

  pip install -r requirements.txt

  export FLASK_APP=movr.py

  export FLASK_DEBUG=1

  flask initdb

  flask run





sql schema

  genre - has_many moves

  move - belongs_to genre

  text - has_many lines

  lines - belongs_to_many moves, belongs_to text



## json schema

genres: [
  {
    id: 1,
    name: '',
  }
]

moves: [
  {
    id: 1,
    name: '',
    genre_id: 1
  }
]



users: [
  {
    id: 1,
    name: ''
  }
]

chats: [
  {
    start_datetime: ''
    users: [1,2],
    genre_id: 1
  }
]

lines: [
  {
    id: 1,
    order_id: 1,
    user_id: 1,
    datetime: '',
    text: '',
    move_ids: [1,2,3],
  }
]
