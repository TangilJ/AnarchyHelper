DROP TABLE IF EXISTS public.bot_comments;
DROP TABLE IF EXISTS public.users;

-- Table: public.bot_comments
CREATE TABLE public.bot_comments
(
    comment_id integer NOT NULL,
    issue_id integer NOT NULL,
    CONSTRAINT unique_comment UNIQUE (comment_id),
    CONSTRAINT unique_issue UNIQUE (issue_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.bot_comments OWNER to postgres;


-- Table: public.users
CREATE TABLE public.users
(
    user_id integer NOT NULL,
    additions_left integer NOT NULL,
    deletions_left integer NOT NULL,
    last_commit integer NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (user_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.users OWNER to postgres;