CREATE TABLE IF NOT EXIST planets (name text primary key, distance DECIMAL(10, 5));

INSERT INTO planets VALUES
    ("Mercury", 0.39),
    ("Venus", 0.72),
    ("Earth", 1.00),
    ("Mars", 1.52),
    ("Jupiter", 5.20),
    ("Saturn", 9.58),
    ("Uranus", 19.20),
    ("Neptune", 30.05);