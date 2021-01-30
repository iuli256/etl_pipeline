import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs;"
songplay_table_drop = "DROP TABLE IF EXISTS songplays;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS songs;"
artist_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = "DROP TABLE IF EXISTS time;"

# CREATE TABLES

staging_events_table_create= ("""
    CREATE TABLE staging_events(
        artist              VARCHAR(250),
        auth                VARCHAR(20),
        first_name           VARCHAR(250),
        gender              CHAR(1),
        item_in_session       INTEGER,
        last_name            VARCHAR(250),
        length              DECIMAL(12,5),
        level               VARCHAR(10),
        location            VARCHAR(250),
        method              VARCHAR(20),
        page                VARCHAR(20),
        registration        FLOAT,
        session_id           INTEGER,
        song                VARCHAR(250),
        status              INTEGER,
        ts                  TIMESTAMP,
        user_agent           VARCHAR(250),
        user_id              INTEGER 
    )
""")

staging_songs_table_create = ("""
    CREATE TABLE staging_songs(
        num_songs           INTEGER,
        artist_id           VARCHAR(20),
        artist_latitude     DECIMAL(12,5),
        artist_longitude    DECIMAL(12,5),
        artist_location     VARCHAR(250),
        artist_name         VARCHAR(250),
        song_id             VARCHAR(20),
        title               VARCHAR(250),
        duration            DECIMAL(15,5),
        year                INTEGER
    )
""")

songplay_table_create = ("""
    CREATE TABLE songplays(
        songplay_id         INTEGER         IDENTITY(0,1)   PRIMARY KEY,
        start_time          TIMESTAMP       REFERENCES time (start_time) SORTKEY DISTKEY,
        user_id             INTEGER         REFERENCES users (user_id),
        level               VARCHAR(10),
        song_id             VARCHAR(20)     REFERENCES songs (song_id),
        artist_id           VARCHAR(20)     REFERENCES artists (artist_id),
        session_id          INTEGER         NOT NULL,
        location            VARCHAR(250),
        user_agent          VARCHAR(250)
    )
""")

user_table_create = ("""
    CREATE TABLE users(
        user_id             INTEGER         NOT NULL SORTKEY PRIMARY KEY,
        first_name          VARCHAR(250)    NOT NULL,
        last_name           VARCHAR(250)    NOT NULL,
        gender              CHAR(1)         NOT NULL,
        level               VARCHAR(10)     NOT NULL
    )
""")

song_table_create = ("""
    CREATE TABLE songs(
        song_id             VARCHAR(20)     SORTKEY PRIMARY KEY,
        title               VARCHAR(250)    NOT NULL,
        artist_id           VARCHAR(20)     NOT NULL DISTKEY REFERENCES artists (artist_id),
        year                INTEGER         NOT NULL,
        duration            DECIMAL(15,5)   NOT NULL
    )
""")

artist_table_create = ("""
    CREATE TABLE artists(
        artist_id           VARCHAR(20)     NOT NULL SORTKEY PRIMARY KEY,
        name                VARCHAR(250)    NOT NULL,
        location            VARCHAR(250),
        latitude            DECIMAL(12,6),
        longitude           DECIMAL(12,6)
    )
""")

time_table_create = ("""
    CREATE TABLE time(
        start_time          TIMESTAMP       NOT NULL DISTKEY SORTKEY PRIMARY KEY,
        hour                INTEGER         NOT NULL,
        day                 INTEGER         NOT NULL,
        week                INTEGER         NOT NULL,
        month               INTEGER         NOT NULL,
        year                INTEGER         NOT NULL,
        weekday             INTEGER        NOT NULL
    )
""")

# STAGING TABLES

staging_events_copy = ("""
    copy staging_events from {data_bucket}
    credentials 'aws_iam_role={role_arn}'
    region 'us-west-2' format as JSON {log_json_path}
    timeformat as 'epochmillisecs';
""").format(data_bucket=config['S3']['LOG_DATA'], role_arn=config['IAM_ROLE']['ARN'], log_json_path=config['S3']['LOG_JSONPATH'])

staging_songs_copy = ("""
    copy staging_songs from {data_bucket}
    credentials 'aws_iam_role={role_arn}'
    region 'us-west-2' format as JSON 'auto';
""").format(data_bucket=config['S3']['SONG_DATA'], role_arn=config['IAM_ROLE']['ARN'])

# FINAL TABLES

user_table_insert = ("""
    INSERT INTO users (user_id, first_name, last_name, gender, level)
    SELECT  DISTINCT(user_id) AS user_id,
            first_name,
            last_name,
            gender,
            level
    FROM staging_events
    WHERE user_id IS NOT NULL
    AND page  =  'NextSong';
""")

song_table_insert = ("""
    INSERT INTO songs (song_id, title, artist_id, year, duration)
    SELECT  DISTINCT(song_id) AS song_id,
            title,
            artist_id,
            year,
            duration
    FROM staging_songs
    WHERE song_id IS NOT NULL;
""")

artist_table_insert = ("""
    INSERT INTO artists (artist_id, name, location, latitude, longitude)
    SELECT  DISTINCT(artist_id) AS artist_id,
            artist_name         AS name,
            artist_location     AS location,
            artist_latitude     AS latitude,
            artist_longitude    AS longitude
    FROM staging_songs
    WHERE artist_id IS NOT NULL;
""")

time_table_insert = ("""
    INSERT INTO time (start_time, hour, day, week, month, year, weekday)
    SELECT  DISTINCT(start_time)                AS start_time,
            EXTRACT(hour FROM start_time)       AS hour,
            EXTRACT(day FROM start_time)        AS day,
            EXTRACT(week FROM start_time)       AS week,
            EXTRACT(month FROM start_time)      AS month,
            EXTRACT(year FROM start_time)       AS year,
            EXTRACT(dayofweek FROM start_time)  as weekday
    FROM songplays;
""")


songplay_table_insert = ("""
    INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
    SELECT  DISTINCT(e.ts)  AS start_time, 
            e.user_id, 
            e.level, 
            s.song_id, 
            s.artist_id, 
            e.session_id, 
            e.location, 
            e.user_agent
    FROM staging_events e
    JOIN staging_songs  s   ON (e.song = s.title AND e.artist = s.artist_name)
    AND e.page  =  'NextSong'
""")

# GET NUMBER OF ROWS IN EACH TABLE
get_number_of_rows = ("""
    SELECT (SELECT COUNT(*) FROM staging_events) AS staging_events,
    (SELECT COUNT(*) FROM staging_songs) AS staging_songs,
    (SELECT COUNT(*) FROM songplays) AS songplays,
    (SELECT COUNT(*) FROM users) AS users,
    (SELECT COUNT(*) FROM songs) AS songs,
    (SELECT COUNT(*) FROM artists) AS artists,
    (SELECT COUNT(*) FROM time) AS time;
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, user_table_create, artist_table_create, song_table_create, time_table_create, songplay_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
select_number_rows_queries= [get_number_of_rows]