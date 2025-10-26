from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "orbits" DROP CONSTRAINT IF EXISTS "fk_orbits_Comets_1d659a36";
        ALTER TABLE "observations" DROP CONSTRAINT IF EXISTS "fk_observat_Comets_c83c61cd";
        ALTER TABLE "close_approaches" DROP CONSTRAINT IF EXISTS "fk_close_ap_Comets_32cc17ee";
        ALTER TABLE "close_approaches" DROP CONSTRAINT IF EXISTS "fk_close_ap_Orbits_7fc6b51f";
        ALTER TABLE "Close_approaches" RENAME TO "close_approaches";
        ALTER TABLE "close_approaches" RENAME COLUMN "orbit_id_id" TO "orbit_id";
        ALTER TABLE "close_approaches" RENAME COLUMN "comet_id_id" TO "comet_id";
        ALTER TABLE "Comets" RENAME TO "comets";
        ALTER TABLE "Observations" RENAME TO "observations";
        ALTER TABLE "observations" RENAME COLUMN "comet_id_id" TO "comet_id";
        ALTER TABLE "Observatories" RENAME TO "observatories";
        ALTER TABLE "Orbits" RENAME TO "orbits";
        ALTER TABLE "orbits" RENAME COLUMN "comet_id_id" TO "comet_id";
        ALTER TABLE "close_approaches" ADD CONSTRAINT "fk_close_ap_orbits_0af1de4b" FOREIGN KEY ("orbit_id") REFERENCES "orbits" ("uuid") ON DELETE CASCADE;
        ALTER TABLE "close_approaches" ADD CONSTRAINT "fk_close_ap_comets_45ac64e9" FOREIGN KEY ("comet_id") REFERENCES "comets" ("uuid") ON DELETE CASCADE;
        ALTER TABLE "observations" ADD CONSTRAINT "fk_observat_comets_fdbd39d2" FOREIGN KEY ("comet_id") REFERENCES "comets" ("uuid") ON DELETE CASCADE;
        ALTER TABLE "orbits" ADD CONSTRAINT "fk_orbits_comets_401eacf0" FOREIGN KEY ("comet_id") REFERENCES "comets" ("uuid") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "close_approaches" DROP CONSTRAINT IF EXISTS "fk_close_ap_comets_45ac64e9";
        ALTER TABLE "close_approaches" DROP CONSTRAINT IF EXISTS "fk_close_ap_orbits_0af1de4b";
        ALTER TABLE "observations" DROP CONSTRAINT IF EXISTS "fk_observat_comets_fdbd39d2";
        ALTER TABLE "orbits" DROP CONSTRAINT IF EXISTS "fk_orbits_comets_401eacf0";
        ALTER TABLE "comets" RENAME TO "Comets";
        ALTER TABLE "orbits" RENAME TO "Orbits";
        ALTER TABLE "orbits" RENAME COLUMN "comet_id" TO "comet_id_id";
        ALTER TABLE "observations" RENAME TO "Observations";
        ALTER TABLE "observations" RENAME COLUMN "comet_id" TO "comet_id_id";
        ALTER TABLE "observatories" RENAME TO "Observatories";
        ALTER TABLE "close_approaches" RENAME TO "Close_approaches";
        ALTER TABLE "close_approaches" RENAME COLUMN "comet_id" TO "comet_id_id";
        ALTER TABLE "close_approaches" RENAME COLUMN "orbit_id" TO "orbit_id_id";
        ALTER TABLE "orbits" ADD CONSTRAINT "fk_orbits_Comets_1d659a36" FOREIGN KEY ("comet_id_id") REFERENCES "Comets" ("uuid") ON DELETE CASCADE;
        ALTER TABLE "observations" ADD CONSTRAINT "fk_observat_Comets_c83c61cd" FOREIGN KEY ("comet_id_id") REFERENCES "Comets" ("uuid") ON DELETE CASCADE;
        ALTER TABLE "close_approaches" ADD CONSTRAINT "fk_close_ap_Orbits_7fc6b51f" FOREIGN KEY ("orbit_id_id") REFERENCES "Orbits" ("uuid") ON DELETE CASCADE;
        ALTER TABLE "close_approaches" ADD CONSTRAINT "fk_close_ap_Comets_32cc17ee" FOREIGN KEY ("comet_id_id") REFERENCES "Comets" ("uuid") ON DELETE CASCADE;"""


MODELS_STATE = (
    "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"
)
