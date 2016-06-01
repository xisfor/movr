
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
