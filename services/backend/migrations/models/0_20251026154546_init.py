from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "observatories" (
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
CREATE TABLE IF NOT EXISTS "comets" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "uuid" UUID NOT NULL PRIMARY KEY,
    "designation" VARCHAR(50) NOT NULL UNIQUE,
    "discovery_date" TIMESTAMPTZ NOT NULL,
    "discovered_by_id" UUID NOT NULL REFERENCES "users" ("uuid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "observations" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "uuid" UUID NOT NULL PRIMARY KEY,
    "observation_time" TIMESTAMPTZ NOT NULL,
    "ra_deg" DOUBLE PRECISION NOT NULL,
    "dec_deg" DOUBLE PRECISION NOT NULL,
    "altitude_deg" DOUBLE PRECISION NOT NULL,
    "azimuth_deg" DOUBLE PRECISION NOT NULL,
    "processed" BOOL NOT NULL DEFAULT False,
    "comet_id" UUID NOT NULL REFERENCES "comets" ("uuid") ON DELETE CASCADE,
    "observatory_id_id" UUID NOT NULL REFERENCES "observatories" ("uuid") ON DELETE CASCADE,
    "observer_id_id" UUID NOT NULL REFERENCES "users" ("uuid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "orbits" (
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
    "comet_id" UUID NOT NULL REFERENCES "comets" ("uuid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "close_approaches" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "uuid" UUID NOT NULL PRIMARY KEY,
    "approach_time" TIMESTAMPTZ NOT NULL,
    "distance_au" DOUBLE PRECISION,
    "distance_km" DOUBLE PRECISION NOT NULL,
    "comet_id" UUID NOT NULL REFERENCES "comets" ("uuid") ON DELETE CASCADE,
    "orbit_id" UUID NOT NULL REFERENCES "orbits" ("uuid") ON DELETE CASCADE
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
    "close_approach_id" UUID REFERENCES "close_approaches" ("uuid") ON DELETE CASCADE,
    "comet_id" UUID REFERENCES "comets" ("uuid") ON DELETE CASCADE,
    "orbit_id" UUID REFERENCES "orbits" ("uuid") ON DELETE CASCADE,
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
)
