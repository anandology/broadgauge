create table users (
    id serial primary key,
    name text,
    email text unique not null,
    phone text
);

create table organization (
    id serial primary key,
    name text,
    city text,
    admin_id integer references users,
    admin_role text
);

create table trainer (
    user_id integer references users unique,
    city text,
    github text,
    website text,
    bio text
);

create table workshop (
    id serial primary key,
    org_id integer references organization,
    title text,
    description text,
    status text default 'pending', -- one of pending, confirmed or completed
    expected_participants integer,
    "date" date
);
