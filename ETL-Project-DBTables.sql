CREATE TABLE "Author" (
    "id" int UNIQUE  NOT NULL,
    "name" varchar   NOT NULL,
    "birthdate" date   NOT NULL,
    "description" varchar   NOT NULL,
    CONSTRAINT "pk_Author" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Quotes" (
    "id" int  UNIQUE NOT NULL,
    "author_id" int   NOT NULL,
    "quote_text" varchar   NOT NULL,
    CONSTRAINT "pk_Quotes" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Tags" (
    "quote_id" int  NOT NULL,
    "tag" varchar  NOT NULL,
    CONSTRAINT "pk_Tags" PRIMARY KEY (
        "quote_id","tag"
     )
);