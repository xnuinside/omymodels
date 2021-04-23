CREATE TYPE "material_type" AS ENUM (
  'video',
  'article'
);

CREATE TABLE "material" (
  "id" SERIAL PRIMARY KEY,
  "title" varchar NOT NULL,
  "description" text,
  "link" varchar NOT NULL,
  "type" material_type,
  "additional_properties" json,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);

CREATE TABLE "author" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "link" varchar
);

CREATE TABLE "material_authors" (
  "category" int,
  "material" int
);

CREATE TABLE "material_platforms" (
  "category" int,
  "material" int
);

CREATE TABLE "platform" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar NOT NULL,
  "link" varchar NOT NULL
);

CREATE TABLE "material_categories" (
  "category" int,
  "material" int
);

CREATE TABLE "category" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar NOT NULL,
  "description" text,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);

CREATE TABLE "content_filters" (
  "category" int,
  "channels" varchar[],
  "words" varchar[],
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);

ALTER TABLE "material_authors" ADD FOREIGN KEY ("category") REFERENCES "author" ("id");

ALTER TABLE "material_authors" ADD FOREIGN KEY ("material") REFERENCES "material" ("id");

ALTER TABLE "material_platforms" ADD FOREIGN KEY ("category") REFERENCES "platform" ("id");

ALTER TABLE "material_platforms" ADD FOREIGN KEY ("material") REFERENCES "material" ("id");

ALTER TABLE "material_categories" ADD FOREIGN KEY ("category") REFERENCES "category" ("id");

ALTER TABLE "material_categories" ADD FOREIGN KEY ("material") REFERENCES "material" ("id");

ALTER TABLE "content_filters" ADD FOREIGN KEY ("category") REFERENCES "category" ("id");
