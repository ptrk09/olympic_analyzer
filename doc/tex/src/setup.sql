CREATE TABLE games(
    id INTEGER NOT NULL,
    city VARCHAR,
    year INTEGER NOT NULL CHECK(year > 1895),
    season VARCHAR CHECK(season = 'Summer' OR season = 'Winter'),
    PRIMARY KEY(id),
    UNIQUE(id)
);


CREATE TABLE nation(
    id INTEGER NOT NULL,
    noc VARCHAR,
    namecountry VARCHAR,
    capital VARCHAR,
    population INTEGER,
    region VARCHAR,
    PRIMARY KEY(id)
);


CREATE TABLE athletes(
    id INTEGER NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    sex VARCHAR(1) NOT NULL,
    age INTEGER,
    height INTEGER,
    weight NUMERIC(4, 1),
    id_noc INTEGER NOT NULL,
    sport VARCHAR NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(id_noc) REFERENCES nation(id)
);


CREATE TABLE sport(
    id INTEGER NOT NULL,
    name_sport VARCHAR,
    PRIMARY KEY(id)
);


CREATE TABLE event(
    id INTEGER NOT NULL,
    name_event VARCHAR,
    id_sport INTEGER NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(id_sport) REFERENCES sport(id)
);


CREATE TABLE medal(
    id INTEGER NOT NULL,
    id_game INTEGER NOT NULL,
    sport INTEGER NOT NULL,
    event INTEGER NOT NULL,
    gold_m INTEGER NOT NULL CHECK(gold_m < 2),
    silver_m INTEGER NOT NULL CHECK(silver_m < 2),
    bronze_m INTEGER NOT NULL CHECK(bronze_m < 2),
    FOREIGN KEY(id) REFERENCES athletes(id),
    FOREIGN KEY(id_game) REFERENCES games(id),
    FOREIGN KEY(sport) REFERENCES sport(id),
    FOREIGN KEY(event) REFERENCES event(id)
);


CREATE TABLE comments(
    id SERIAL,
    id_user INTEGER NOT NULL,
    content TEXT NOT NULL,
    date_comment DATE,
    time_comment TIME,
    PRIMARY KEY(id),
    FOREIGN KEY(id_user) REFERENCES auth_user(id),
    UNIQUE(id)
);


CREATE TABLE buffer_comments(
    id SERIAL,
    id_user INTEGER NOT NULL,
    content TEXT NOT NULL,
    date_comment DATE,
    time_comment TIME,
    PRIMARY KEY(id),
    FOREIGN KEY(id_user) REFERENCES auth_user(id),
    UNIQUE(id)
);


create or replace function logs_buffer_comment()
returns trigger
language plpgsql as
$$
begin
    new.date_comment := current_date;
    new.time_comment := localtime;
    insert into buffer_comments(id_user, content, date_comment, time_comment)
    values(new.id_user, new.content, new.date_comment, new.time_comment);
    return new;
end;
$$;


create trigger insert_comment before insert
on comments
for each row
execute procedure logs_buffer_comment();


create or replace function delete_user_comments()
returns trigger
language plpgsql as
$$
begin
	delete from comments
	where id_user = old.id;
	
	delete from buffer_comments
	where id_user = old.id;
	
    return old;
end;
$$;


create trigger delete_user before delete
on auth_user
for each row
execute procedure delete_user_comments();

create user user_serv with password 'admin';
create user reader with password 'reader';

grant select on athletes, games, nation, medal, sport, event to reader;
REVOKE ALL ON auth_user, comments, buffer_comments event from reader;

grant select, insert, delete on auth_user, comments, buffer_comments to user_serv;
REVOKE ALL ON athletes, games, nation, medal, sport, event from user_serv;