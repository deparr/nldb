#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from sqlite3 import Error
import openai
import os

# language_model.ipynb
#
# Automatically generated by Colaboratory.
#
# Original file is located at
#    https://colab.research.google.com/drive/1FTTJU7V-T0fNNv0GyjjLofrdT4PBo_4c


insert_statements = ("""INSERT INTO user (username, joindate) VALUES
  ('ylim', '2023-09-10'),
  ('selz', '2023-09-10'),
  ('dpar', '2023-09-10');
  """,
                     """INSERT INTO history (username, video_id, date_watched) VALUES
  ('ylim', 1, '2023-10-03'),
  ('selz', 2, '2023-10-03'),
  ('dpar', 3, '2023-09-01');
  """,
                     """INSERT INTO channel (id, username, subscriptions, created_at) VALUES
  (1, 'ylim', 30, '2023-10-01'),
  (2, 'selz', 50, '2023-10-01'),
  (3, 'dpar', 10000, '2020-10-01');
  """,
                     """INSERT INTO video (id, channel_id, likes, dislikes, description, views) VALUES
  (1, 1, 30, 0, 'chipmunk eating a squirrel', 3000),
  (2, 2, 1000, 0, 'cat flying kicking a 100 year old grandma in a wheelchair', 1000000),
  (3, 3, 0, 100000, 'teen eating raisin brans in bacon grease', 1000000);
  """,
                     """INSERT INTO comment (id, video_id, username, content) VALUES
  (1, 2, 'ylim', 'hey! thats my grandma'),
  (2, 3, 'selz', 'yoooo, you should try it with fruity pebbles next time!'),
  (3, 1, 'dpar', 'thats raaaaaaad!~');
  """,
                     """INSERT INTO usersubscription (username, channel_id) VALUES
  ('ylim', 1),
  ('ylim', 2),
  ('ylim', 3),
  ('dpar', 2),
  ('selz', 1),
  ('dpar', 3);
  """
                     )

openai.api_key = os.getenv("OPENAI_KEY")


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f'sqlite3 {sqlite3.version}')
    except Error as e:
        print(e)

    return conn


def init_database(conn):
    create_statements = (
        """CREATE TABLE channel (
                id INT,
                username VARCHAR(16) NOT NULL,
                subscriptions INT,
                created_at DATE NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY (username) REFERENCES user(username)
              );
    """,
        """CREATE TABLE video (
                id INT,
                channel_id INT NOT NULL,
                likes INT NOT NULL,
                dislikes INT NOT NULL,
                description TEXT,
                views INT NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY (channel_id) REFERENCES channel(id)
              );
    """,
        """CREATE TABLE user (
                username TEXT,
                joindate DATE NOT NULL,
                PRIMARY KEY (username)
            );
    """,

        """CREATE TABLE history (
              username VARCHAR(16) NOT NULL,
              video_id INTEGER NOT NULL,
              date_watched TEXT NOT NULL,
              FOREIGN KEY (username) REFERENCES user (username),
              FOREIGN KEY (video_id) REFERENCES video (id)
            );
    """,
        """CREATE TABLE comment (
                    id INT,
                    video_id INT,
                    username TEXT,
                    content TEXT,
                    PRIMARY KEY (id),
                    FOREIGN KEY (video_id) REFERENCES video(id),
                    FOREIGN KEY (username) REFERENCES user(username)
              );
    """,
        """CREATE TABLE usersubscription (
                    username TEXT NOT NULL,
                    channel_id INT NOT NULL,
                    PRIMARY KEY (username, channel_id)
                );
    """
    )

    for create_statement in create_statements:
        cur = conn.cursor()
        cur.execute(create_statement)
        cur.close()

    for insert_statement in insert_statements:
        cur = conn.cursor()
        cur.execute(insert_statement)
        conn.commit()
        cur.close()


prefix = """
        I will give you series of SQLite3 create table statements. In subsequent messages I will provide a statement in natural language; I want you to create an SQL query based on my statement. Your query will always end with a semicolon (;). You will reply with only your SQL query, nothing else.
        begin SQLite3 statements:

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
        CREATE TABLE user (
                username TEXT,
                joindate DATE NOT NULL,
                PRIMARY KEY (username)
        );
        CREATE TABLE history (
              username VARCHAR(16) NOT NULL,
              video_id INTEGER NOT NULL,
              date_watched TEXT NOT NULL,
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
                    PRIMARY KEY (username, channel_id)
        );

        end SQLite3 statements
"""


def query(conn, prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prefix},
            {"role": "user", "content": prompt}
        ],
        max_tokens=None,
        temperature=0
    )

    gpt_query = response.choices[0].message.content

    print(f'\ngot query:\n{gpt_query}\n')
    yn = input('Run this query against the database? (y/n)  ')
    print()
    if yn.lower() == 'y':
        try:
            rs = conn.execute(gpt_query)
            if 'INSERT' in gpt_query or 'UPDATE' in gpt_query or 'DELETE' in gpt_query:
                yn = input(f'{rs.rowcount} rows affected, commit this transaction? (y/n) ')
                if yn.lower() == 'y':
                    conn.commit()
            with open('query-results.txt', mode='a') as f:
                print('--------------------------------', file=f)
                print(f'{prompt}\n\n{gpt_query}', file=f, end='\n\n')
                print('SUCCESS:', file=f)
                for row in rs.fetchall():
                    print(row, file=f)
                    print(row)
        except Error as e:
            with open('query-results.txt', mode='a') as f:
                print('--------------------------------', file=f)
                print(f'{prompt}\n{gpt_query}', file=f, end='\n\n')
                print(f'FAILURE: {e}', file=f)


if __name__ == '__main__':
    need_to_create = not os.path.isfile(r"./pythonsqlite.db")
    conn = create_connection(r"./pythonsqlite.db")
    if need_to_create:
        print('initializing db...')
        init_database(conn)
    else:
        print('using existing db')

    yn = 'y'
    while yn.lower() == 'y':
        prompt = input("ChatGPT has been provided with the table schemas, make your query:\n")
        query(conn, prompt)
        yn = input('Make another query? (y/n) ')

    conn.close()
