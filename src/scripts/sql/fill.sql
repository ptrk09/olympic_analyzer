COPY games FROM '/Users/ptrk/projects/olympic_statistics/scripts/data/games.csv' DELIMITER ',' NULL AS '\N' CSV HEADER;

COPY nation FROM '/Users/ptrk/projects/olympic_statistics/scripts/data/nations.csv' DELIMITER ',' NULL AS '\N' CSV HEADER;

COPY athletes FROM '/Users/ptrk/projects/olympic_statistics/scripts/data/new_athletes.csv' DELIMITER ',' NULL AS '\N' CSV HEADER;

COPY sport FROM '/Users/ptrk/projects/olympic_statistics/scripts/data/sports.csv' DELIMITER ',' NULL AS '\N' CSV HEADER;

COPY event FROM '/Users/ptrk/projects/olympic_statistics/scripts/data/events.csv' DELIMITER ',' NULL AS '\N' CSV HEADER;

COPY medal FROM '/Users/ptrk/projects/olympic_statistics/scripts/data/medals.csv' DELIMITER ',' NULL AS '\N' CSV HEADER;