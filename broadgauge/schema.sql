create table users (
    id serial primary key,
    name text,
    email text unique not null,
    phone text,
    city text,
    bio text,
    website text,
    github text,
    is_admin boolean,
    is_trainer boolean
);

create table organization (
    id serial primary key,
    name text,
    city text
);

create table organization_members (
    id serial primary key,
    org_id integer references organization,
    user_id integer references users,
    role text,
    since timestamp default (current_timestamp at time zone 'UTC')
);

create table workshop (
    id serial primary key,
    org_id integer references organization,
    trainer_id integer references users,
    title text,
    description text,
    status text default 'pending', -- one of pending, confirmed or completed
    expected_participants integer,
    "date" date
);

create table workshop_trainers (
    id serial primary key,
    workshop_id integer references workshop,
    trainer_id integer references users,
    tstamp timestamp default (current_timestamp at time zone 'UTC')
);
