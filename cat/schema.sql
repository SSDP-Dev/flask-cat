DROP TABLE IF EXISTS action;
DROP TABLE IF EXISTS action_list;
DROP TABLE IF EXISTS spending;
DROP TABLE IF EXISTS spending_list;
DROP TABLE IF EXISTS user;

CREATE TABLE action (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  note TEXT,
  points INTEGER NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE action_list (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  type TEXT NOT NULL,
  point_value INTEGER,
  spanish_translation TEXT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE spending (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  description TEXT,
  points INTEGER NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE spending_list (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  type TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  permissions TEXT NOT NULL,
  cb INTEGER,
  pc INTEGER,
  te INTEGER,
  balance INTEGER,
  url TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
