-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS chain;
DROP TABLE IF EXISTS user_chain;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  admin BOOLEAN NOT NULL DEFAULT 0,
  lecturer BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE chain (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  data BLOB,
  FOREIGN KEY (owner_id) REFERENCES user (id)
);

CREATE TABLE user_chain (
  user_id INTEGER NOT NULL,
  chain_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (chain_id) REFERENCES chain (id)
);
