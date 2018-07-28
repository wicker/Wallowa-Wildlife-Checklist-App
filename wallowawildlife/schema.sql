DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS creature_type;
DROP TABLE IF EXISTS creature;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE creature_type (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  url_text TEXT NOT NULL
);

CREATE TABLE creature (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name_common TEXT UNIQUE NOT NULL,
  name_latin TEXT UNIQUE NOT NULL,
  description TEXT NOT NULL,
  photo_url TEXT NOT NULL,
  wiki_url TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  type_name TEXT NOT NULL,

  FOREIGN KEY (user_id) REFERENCES user (id)
);

