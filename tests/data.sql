INSERT INTO product (title, qty, image)
VALUES
  ('apple', 100, 'default_image.jpg'),
  ('orange', 60, 'default_image.jpg');

INSERT INTO location (name, image)
VALUES
  ('Nablus', 'location_default.jpg'),
  ('Rammallah', 'location_default.jpg');


INSERT INTO productMovement (from_location, to_location, product_id, qty)
VALUES
  ('Not Specified', 'Nablus', 1, 50),
  ('Nablus', 'Rammallah', 1, 15);


INSERT INTO productLocation (name, title, qty)
VALUES
  ('Nablus', 'apple', 50),
  ('Rammallah', 'apple', 15);