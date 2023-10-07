CREATE TABLE user (
    username TEXT,
    joindate DATE NOT NULL,
    PRIMARY KEY (username)
);

CREATE TABLE channel (
    id INT,
    username VARCHAR(16) NOT NULL,
    subscriptions INT,
    created_at DATE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (username) REFERENCES user(username)
);

CREATE TABLE video (
    id INT,
    channel_id INT NOT NULL,
    likes INT NOT NULL,
    dislikes INT NOT NULL,
    description TEXT,
    views INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (channel_id) REFERENCES channel(id)
);

CREATE TABLE history (
    username VARCHAR(16) NOT NULL,
    video_id INTEGER NOT NULL,
    date_watched DATE NOT NULL,
    FOREIGN KEY (username) REFERENCES user (username),
    FOREIGN KEY (video_id) REFERENCES video (id)
);

CREATE TABLE comment (
    id INT,
    video_id INT,
    username TEXT,
    content TEXT,
    PRIMARY KEY (id),
    FOREIGN KEY (video_id) REFERENCES video(id),
    FOREIGN KEY (username) REFERENCES user(username)
);

CREATE TABLE usersubscription (
    username TEXT NOT NULL,
    channel_id INT NOT NULL,
    PRIMARY KEY (username, channel_id),
    FOREIGN KEY (username) REFERENCES user(username),
    FOREIGN KEY (channel_id) REFERENCES channel(id)
);
