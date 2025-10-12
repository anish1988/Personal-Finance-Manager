-- db/seed/categories_seed.sql
-- Create categories table if it doesn't exist
CREATE TABLE IF NOT EXISTS categories (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
  slug TEXT,
  UNIQUE(name, parent_id)
);

-- Insert top-level categories
INSERT INTO categories (name, parent_id, slug)
VALUES
  ('Food & Dining', NULL, 'food-dining'),
  ('Transport', NULL, 'transport'),
  ('Bills & Utilities', NULL, 'bills-utilities'),
  ('Housing', NULL, 'housing'),
  ('Income', NULL, 'income'),
  ('Healthcare', NULL, 'healthcare'),
  ('Entertainment', NULL, 'entertainment'),
  ('Shopping', NULL, 'shopping'),
  ('Others', NULL, 'others')
ON CONFLICT (name, parent_id) DO NOTHING;

-- Insert common subcategories (referencing parent by name)
-- Using WITH to get parent ids dynamically so the script is portable
WITH parents AS (
  SELECT id, name FROM categories
)
INSERT INTO categories (name, parent_id, slug)
VALUES
  ('Groceries', (SELECT id FROM parents WHERE parents.name='Food & Dining'), 'groceries'),
  ('Restaurants', (SELECT id FROM parents WHERE parents.name='Food & Dining'), 'restaurants'),
  ('Coffee', (SELECT id FROM parents WHERE parents.name='Food & Dining'), 'coffee'),
  ('Fuel', (SELECT id FROM parents WHERE parents.name='Transport'), 'fuel'),
  ('Taxi', (SELECT id FROM parents WHERE parents.name='Transport'), 'taxi'),
  ('Public Transport', (SELECT id FROM parents WHERE parents.name='Transport'), 'public-transport'),
  ('Electricity', (SELECT id FROM parents WHERE parents.name='Bills & Utilities'), 'electricity'),
  ('Internet', (SELECT id FROM parents WHERE parents.name='Bills & Utilities'), 'internet'),
  ('Mobile', (SELECT id FROM parents WHERE parents.name='Bills & Utilities'), 'mobile'),
  ('Rent', (SELECT id FROM parents WHERE parents.name='Housing'), 'rent'),
  ('Maintenance', (SELECT id FROM parents WHERE parents.name='Housing'), 'maintenance'),
  ('Salary', (SELECT id FROM parents WHERE parents.name='Income'), 'salary'),
  ('Interest', (SELECT id FROM parents WHERE parents.name='Income'), 'interest'),
  ('Pharmacy', (SELECT id FROM parents WHERE parents.name='Healthcare'), 'pharmacy'),
  ('Doctor', (SELECT id FROM parents WHERE parents.name='Healthcare'), 'doctor'),
  ('Subscriptions', (SELECT id FROM parents WHERE parents.name='Entertainment'), 'subscriptions'),
  ('Movies', (SELECT id FROM parents WHERE parents.name='Entertainment'), 'movies'),
  ('Clothing', (SELECT id FROM parents WHERE parents.name='Shopping'), 'clothing')
ON CONFLICT (name, parent_id) DO NOTHING;
