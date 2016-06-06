
-- genres: [
--   {
--     id: 1,
--     name: '',
--   }
-- ]
drop table if exists genres;
create table genres (
  id integer primary key autoincrement,
  name text not null
);


-- moves: [
--   {
--     id: 1,
--     name: '',
--     genre_id: 1
--   }
-- ]
drop table if exists moves;
create table moves (
  id integer primary key autoincrement,
  name text not null,
  genre_id integer references genres(id)
);


-- users: [
--   {
--     id: 1,
--     name: ''
--   }
-- ]



-- chats: [
--   {
--     start_datetime: ''
--     user_ids: [1,2],
--     genre_id: 1
--   }
-- ]

drop table if exists chats;
create table chats (
  id integer primary key autoincrement,
  title text not null,
  genre_id integer references genres(id),
  session_count integer,
  users text
);


-- lines: [
--   {
--     id: 1,
--     order_id: 1,
--     user_id: 1,
--     datetime: '',
--     text: '',
--     move_ids: [1,2,3],
--   }
-- ]

drop table if exists lines;
create table lines (
  id integer primary key autoincrement,
  seq integer not null,
  text text,
  session text,
  time text,
  user text,
  chat_id integer references chats(id),
  client_notification integer
);

-- line_move: {
--     id: 1,
--     line_id: 1,
--     move_id: 1
-- }
drop table if exists line_move;
create table line_move (
  id integer primary key autoincrement,
  line_id integer not null,
  move_id integer not null
)
