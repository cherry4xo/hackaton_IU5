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
    "eJztXVtP4zgU/itVnxiJRbRcNVqtVEqZ6S5QBGV3NMMochO3zZLEnVwGuiP++9rOzXGc0L"
    "RpSahfuNg+jv0d++ScL8fJr6aJNGg4e11gqJ4BXB1ZQ+A8Nj82fjUtYEL8R1aT3UYTzGZx"
    "A1LggpFBZdS4seLi1rQWjBzXBqqLG4yB4UBcpEFHtfUZaUfEHrz9w9YJ+XmwT38exn8fBu"
    "UN+ktj/jncZ1q14rZH/t9tXwIyTWnFwalfTX+O/EZjv2niGozEiLaFzNCOmJZ+f34X6h6Z"
    "sYZUPGXdmry3yT1YdDZqfPGD41gkGJU/3KD6hJ/yQZuZmD9OtRFfyh/OwSkzv2CcGlPSZk"
    "Y+TvQ0sEe66wQdNroGcqCC16uNgDqFDtWOZ+k/PKi4aALdKbSxjr59x8W6pcFn6IT/zh6V"
    "sQ4NLbEnPE/XSBe0RnHnM1p6f98/v6Btie5HiooMz7TY9rO5OyVbIhAgxXtEitRNoAVt4E"
    "KN2R+WZxjBngqL/FHjAtf2YDRcLS7Q4Bh4Btllzd/HnqWSzdWgVyI/Dv9opvYduQq3WoMi"
    "FVlkz+qWS/D49eLPK541LW2SS3U/d253Do4/0Fkix53YtJJi0nyhgsAFvijFNgZTtSGZtg"
    "LcNKTnuMbVTSiGNSnJgasFonvhH8uAHBbEKMemK4Q5hG85TJt4DtrAMuaBBnMwHvavenfD"
    "ztUNmYnpOD8MClFn2CM1bVo650p3fJUgbHh90xx10vinP/zcIP82vg6ue7zionbDr00yJu"
    "C5SLHQkwI0ZrGFpSEwuCWzS2bakopNSkrFvqlig8HHenVc4HpOWqfdKbB7lmdSnfYxGMBS"
    "YUq3sTSnVwzeujTZxIZfhY5D9JV2O25uB93e3V3/+tPHRtzwweoOrm4ue8Pe+ceGisyZAf"
    "GgHqyLTv+SFI2BbkCNv81nrAUTPCsGtCbuFP/b2s9ZC393bqktbe1z+r0Oatq06iWhETRy"
    "oP3T97cwvrarhPuiyK7L7qWEHRisqw1uwJpsuHDauaaUVQ20tJXVy/YhlfvGyjWQ6mtFxZ"
    "GU2KyKNZoSXMqibl55nDk8XsQc8gpizOExbw6hbSNbMbEdBxMBoEP47IoBTQnWBNC83dD7"
    "MkxshBC4navOlw+JzXA5uP4UNmeA7l4OzjiAbfCkMOZE4Av8eTe4FmMskuVgvrdwxTdNV9"
    "3dhqE77ve6gU5mnw86jy9nVkgHPOhqIohVikWgQuEVwtFKwf1q8MmAiEzoFsWOkdlCyBCh"
    "UgpCxspsIWQeNm8FEWNEymSJqowYodfGj0JOiKCRRu8C2VCfWH/BeSrE5DALSOv7oJvKoh"
    "aXxqud3CBDypFdFnh6eFI4CKXQdu66nfNeM23cSoCtS/pxqrw/X8WNtdmvA0fNVQnA+axz"
    "rYFjLfcCKy7hVpSx9DimvtZYCp0uMajEFo6A+vgEbE1JGEVSg9qIK4napqvMtsmXAAvHM1"
    "owHzL6LLRFD/4EGsl+8ids/dqDv2zg5TMa+Yzm7W/W74bKl89o3qliU89oopvOMkxxSrie"
    "2q2JNhfiiDXd95wU4Am8LAOBDEaTk+MUOSaCVXaxRLo7H9yfXfYaN7e9bv+uHxBtkbJoJS"
    "nCBbrvZN32OpdcgB7B8mguB6cvtySc1doLZeAZhltLMmtbRnyI2LUlCbYtQy6HMspmdtfH"
    "f1SYOOK21oIcSDn4LUyDVBg/boMVjdqZdSnKhU0CfBZ0cfHXLfRb5qzNdB5uVW/eKYxf1s"
    "pl+JtWxGBE2zmHt4jbSLZCshUyqK1AUCvZineq2BRbgQHBDkZ051s0/4kTKyef9HUrWGby"
    "09EiuaBH2bmgR6lcUPq7AIhh+81l45aJX/voaAEAcatMBGldih1Q0U9ozxViEIqamrR0Pc"
    "1NTczLovQZ1Qm+A4zmBUNtkayMt5OwlBA01j9XQ7RQZNxYRtyYohod7hHzCrgUTzio0BIU"
    "IZOfmFsEmwHXU81xiVipFRCpIbO1VtYlsUQE3Au/hLIZmFRLycNIHkaG6xUI1yUP804Vm7"
    "pTskcEVz1iKHNHqhL82gDHIJNCeQ6xiExxiDhKtTCMjIzEMcxMM1zd9TRYGExeUCIaIvqf"
    "bnrutDigSTmJZ4Bn8A4IKAgEzhAyILDEeCbkODRHWHBdYBYNjxZH82wwuEzc5c76/Ong+6"
    "uz3u1O60MS1f71UGaIlZUhFjhVyJ4vkScmEt5eFOlhuqUgZCW3BT+Zbbe+bLvEviwBxUHU"
    "oV43EpsHU2izFoU04+D1Fj6OStutKh09TK7XHOY4WtCvU8dxU8kd1547LvgupJVegfTGSU"
    "DlvwFpu5KAWu3TRQBsn2YjSOqSEJJHgYRuKBRSs0Iyno7eb2ZNloCSlZJYhq82M2DArxc7"
    "uMbJbTWeqbBmkXQcxPsYW5lWsVaP0M+tELmCUdZFjg8Yt5HOX+2dP5k48B6eL8vEgXeq2P"
    "QrwaGpKyb4F9kKeNYF98cc10Qgu9XuScLdU1Vo4RGouivKsc7x9zhBiWiAqG6php511CgH"
    "UE5O4skHdwpw8JLT8FCwkVg21hN0IpEOH/PbE8/Em1qZQVsHM6egmRWLS3TDh/4hKkslvq"
    "Wl6+mh1MQjWSjtDc6Q6JWU+YqMhKT+3lp/Jo7BkSCmzmaxY4kNflpmAjzHWSGC5s6zLnIe"
    "uJ19HridOg+MbdIU92KPkKGrAuIqL6MpJbvBrKa1bQSZ1CTTSSrGq+4uk04iD5EW465TL7"
    "va7pOj66TyafKMgMgPk2qyaXzyvnvJ4ksWX7L4lSF7JYv/ThWbuisS41s0c4iVKeVraZtN"
    "vVrL+4OgCXSjCIiRgEQwYOOA4zwh7IZMgSPgcLKRTAnW5At+G8DUhhOdXJIGA9kvthLjKh"
    "TOs9/VtN15JDK2vzxiyMiwha9/5jiU3SAThe8DENjq1PexuY8cE9e7EQ7qbb5YvFTe1ZtH"
    "sFWK2USvNFsVkBrSJcJjHzIpbx2RfAfaujptCmL5oGY3L5oHcZs3CedFwXzfynrCL4rkCc"
    "zcagicg9VC+BW9hQm5ym/t1uHJ4enB8eEpbkJHEpWc5BjskMfOjtzJdir4LlZGpJ6HCNbi"
    "c5GtUQDEoHk9AWztL+Yl5LkJqadX+IoutAQ8Q/YHphmREr4rXS0ntbQPSxfwxcq/vbz8D3"
    "80iFs="
)
