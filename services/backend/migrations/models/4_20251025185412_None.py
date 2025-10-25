from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "Observatories" (
    "uuid" UUID NOT NULL PRIMARY KEY,
    "code" VARCHAR(16) NOT NULL UNIQUE,
    "name" VARCHAR(128) NOT NULL,
    "latitude" DOUBLE PRECISION NOT NULL,
    "longitude" DOUBLE PRECISION NOT NULL,
    "elevation_m" DOUBLE PRECISION NOT NULL
);
CREATE TABLE IF NOT EXISTS "users" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "uuid" UUID NOT NULL PRIMARY KEY,
    "username" VARCHAR(255) UNIQUE,
    "email" VARCHAR(255) UNIQUE,
    "password_hash" VARCHAR(255),
    "registration_date" DATE NOT NULL,
    "role" VARCHAR(10) NOT NULL DEFAULT 'researcher'
);
COMMENT ON COLUMN "users"."role" IS 'User role';
CREATE TABLE IF NOT EXISTS "Comets" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "uuid" UUID NOT NULL PRIMARY KEY,
    "designation" VARCHAR(50) NOT NULL UNIQUE,
    "name" VARCHAR(255) NOT NULL,
    "discovery_date" TIMESTAMPTZ NOT NULL,
    "discovered_by_id" UUID NOT NULL REFERENCES "users" ("uuid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "Observations" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "uuid" UUID NOT NULL PRIMARY KEY,
    "observation_time" TIMESTAMPTZ NOT NULL,
    "ra_deg" DOUBLE PRECISION NOT NULL,
    "dec_deg" DOUBLE PRECISION NOT NULL,
    "altitude_deg" DOUBLE PRECISION NOT NULL,
    "azimuth_deg" DOUBLE PRECISION NOT NULL,
    "processed" BOOL NOT NULL DEFAULT False,
    "image_reference" VARCHAR(255),
    "image_width" INT,
    "image_height" INT,
    "image_format" VARCHAR(10),
    "image_size" BIGINT,
    "comet_id_id" UUID NOT NULL REFERENCES "Comets" ("uuid") ON DELETE CASCADE,
    "observatory_id_id" UUID NOT NULL REFERENCES "Observatories" ("uuid") ON DELETE CASCADE,
    "observer_id_id" UUID NOT NULL REFERENCES "users" ("uuid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "Orbits" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "uuid" UUID NOT NULL PRIMARY KEY,
    "semi_major_axis" DOUBLE PRECISION NOT NULL,
    "eccentricity" DOUBLE PRECISION NOT NULL,
    "inclination" DOUBLE PRECISION NOT NULL,
    "longitude_ascending_node" DOUBLE PRECISION NOT NULL,
    "argument_periapsis" DOUBLE PRECISION NOT NULL,
    "periapsis_time" TIMESTAMPTZ NOT NULL,
    "epoch" TIMESTAMPTZ NOT NULL,
    "method" VARCHAR(20) NOT NULL DEFAULT 'gauss',
    "is_hyperbolic" BOOL NOT NULL,
    "comet_id_id" UUID NOT NULL REFERENCES "Comets" ("uuid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "Close_approaches" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "uuid" UUID NOT NULL PRIMARY KEY,
    "approach_time" TIMESTAMPTZ NOT NULL,
    "distance_au" DOUBLE PRECISION,
    "distance_km" DOUBLE PRECISION NOT NULL,
    "comet_id_id" UUID NOT NULL REFERENCES "Comets" ("uuid") ON DELETE CASCADE,
    "orbit_id_id" UUID NOT NULL REFERENCES "Orbits" ("uuid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "calculation_tasks" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "uuid" UUID NOT NULL PRIMARY KEY,
    "status" VARCHAR(10) NOT NULL DEFAULT 'processing',
    "observation_start_time" TIMESTAMPTZ,
    "observation_end_time" TIMESTAMPTZ,
    "location_code" VARCHAR(16),
    "error_message" TEXT,
    "raw_observations" JSONB,
    "close_approach_id" UUID REFERENCES "Close_approaches" ("uuid") ON DELETE CASCADE,
    "comet_id" UUID REFERENCES "Comets" ("uuid") ON DELETE CASCADE,
    "orbit_id" UUID REFERENCES "Orbits" ("uuid") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "users" ("uuid") ON DELETE CASCADE
);
COMMENT ON COLUMN "calculation_tasks"."status" IS 'PROCESSING: processing\nCOMPLETED: completed\nFAILED: failed';
COMMENT ON TABLE "calculation_tasks" IS 'Задача на расчёт орбиты по наблюдениям.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "TocsR0AqGJZbilX/enn6F42ZmEw="
)
