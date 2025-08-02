-- title.akas
DROP TABLE IF EXISTS title_akas;
CREATE TABLE title_akas (
    titleId TEXT,
    ordering INTEGER,
    title TEXT,
    region TEXT,
    language TEXT,
    types TEXT,
    attributes TEXT,
    isOriginalTitle BOOLEAN
);

-- title.basics
DROP TABLE IF EXISTS title_basics;
CREATE TABLE title_basics (
    tconst TEXT PRIMARY KEY,
    titleType TEXT,
    primaryTitle TEXT,
    originalTitle TEXT,
    isAdult BOOLEAN,
    startYear INTEGER,
    endYear INTEGER,
    runtimeMinutes INTEGER,
    genres TEXT
);

-- title.crew
DROP TABLE IF EXISTS title_crew;
CREATE TABLE title_crew (
    tconst TEXT PRIMARY KEY,
    directors TEXT,
    writers TEXT
);

-- title.episode
DROP TABLE IF EXISTS title_episode;
CREATE TABLE title_episode (
    tconst TEXT PRIMARY KEY,
    parentTconst TEXT,
    seasonNumber INTEGER,
    episodeNumber INTEGER
);

-- title.principals
DROP TABLE IF EXISTS title_principals;
CREATE TABLE title_principals (
    tconst TEXT,
    ordering INTEGER,
    nconst TEXT,
    category TEXT,
    job TEXT,
    characters TEXT
);

-- title.ratings
DROP TABLE IF EXISTS title_ratings;
CREATE TABLE title_ratings (
    tconst TEXT PRIMARY KEY,
    averageRating NUMERIC,
    numVotes INTEGER
);

-- name.basics
DROP TABLE IF EXISTS name_basics;
CREATE TABLE name_basics (
    nconst TEXT PRIMARY KEY,
    primaryName TEXT,
    birthYear INTEGER,
    deathYear INTEGER,
    primaryProfession TEXT,
    knownForTitles TEXT
);

COPY title_akas FROM '/data/title.akas.tsv' WITH (FORMAT text, DELIMITER E'\t', NULL '\N', HEADER true);
COPY title_basics FROM '/data/title.basics.tsv' WITH (FORMAT text, DELIMITER E'\t', NULL '\N', HEADER true);
COPY title_crew FROM '/data/title.crew.tsv' WITH (FORMAT text, DELIMITER E'\t', NULL '\N', HEADER true);
COPY title_episode FROM '/data/title.episode.tsv' WITH (FORMAT text, DELIMITER E'\t', NULL '\N', HEADER true);
COPY title_principals FROM '/data/title.principals.tsv' WITH (FORMAT text, DELIMITER E'\t', NULL '\N', HEADER true);
COPY title_ratings FROM '/data/title.ratings.tsv' WITH (FORMAT text, DELIMITER E'\t', NULL '\N', HEADER true);
COPY name_basics FROM '/data/name.basics.tsv' WITH (FORMAT text, DELIMITER E'\t', NULL '\N', HEADER true);
