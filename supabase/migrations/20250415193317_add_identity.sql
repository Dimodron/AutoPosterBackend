CREATE UNIQUE INDEX payments_id_key ON public.payments USING btree (id);

CREATE UNIQUE INDEX payments_pkey ON public.payments USING btree (id);

alter table "public"."payments" add constraint "payments_pkey" PRIMARY KEY using index "payments_pkey";

alter table "public"."payments" add constraint "payments_id_key" UNIQUE using index "payments_id_key";


