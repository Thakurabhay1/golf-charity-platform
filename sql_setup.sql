-- Golf Charity Platform Database Schema

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    subscription_type VARCHAR(50) NOT NULL,
    subscription_status VARCHAR(50) NOT NULL DEFAULT 'active',
    renewal_date TIMESTAMP,
    charity_id INTEGER,
    contribution_percentage DECIMAL(5,2) DEFAULT 10.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE charities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    website VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 1 AND score <= 45),
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE draws (
    id SERIAL PRIMARY KEY,
    draw_date DATE NOT NULL,
    numbers INTEGER[] NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    prize_pool DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE draw_participants (
    id SERIAL PRIMARY KEY,
    draw_id INTEGER REFERENCES draws(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    numbers INTEGER[] NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(draw_id, user_id)
);

CREATE TABLE winners (
    id SERIAL PRIMARY KEY,
    draw_id INTEGER REFERENCES draws(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    match_type INTEGER NOT NULL CHECK (match_type >= 3 AND match_type <= 5),
    prize_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    proof_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO charities (name, description, website) VALUES
('Cancer Research UK', 'Leading cancer research charity funding life-saving research.', 'https://www.cancerresearchuk.org'),
('Red Cross', 'International humanitarian organization providing emergency assistance.', 'https://www.redcross.org'),
('Save the Children', 'Fighting for children''s rights and delivering immediate humanitarian aid.', 'https://www.savethechildren.org'),
('WWF', 'World Wildlife Fund protecting nature and reducing threats to biodiversity.', 'https://www.wwf.org');

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_scores_user_id ON scores(user_id);
CREATE INDEX idx_scores_date ON scores(date DESC);
CREATE INDEX idx_draws_date ON draws(draw_date DESC);
CREATE INDEX idx_winners_user_id ON winners(user_id);
CREATE INDEX idx_winners_draw_id ON winners(draw_id);
CREATE INDEX idx_draw_participants_draw_id ON draw_participants(draw_id);
CREATE INDEX idx_draw_participants_user_id ON draw_participants(user_id);
