DROP TABLE IF EXISTS product;
CREATE TABLE product (
  product_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT UNIQUE NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  qty INTEGER NOT NULL,
  image TEXT NOT NULL
);

DROP TABLE IF EXISTS productLocation;

CREATE TABLE productLocation (
  name TEXT NOT NULL,
  title TEXT NOT NULL,
  qty INTEGER,
  PRIMARY KEY (name,title),
  FOREIGN KEY (name) REFERENCES location (name),
  FOREIGN KEY (title) REFERENCES product (title)
);



DROP TABLE IF EXISTS location;

CREATE TABLE location (
  location_id INTEGER PRIMARY KEY AUTOINCREMENT ,
  name TEXT UNIQUE NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  image TEXT NOT NULL
);

DROP TABLE IF EXISTS productMovement;

CREATE TABLE productMovement (
  movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_location TEXT,
  to_location TEXT,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  product_id INTEGER NOT NULL,
  qty INTEGER NOT NULL,
  FOREIGN KEY (from_location) REFERENCES location (name),
  FOREIGN KEY (to_location) REFERENCES location (name) ,
  FOREIGN KEY (product_id) REFERENCES product (product_id)
);
