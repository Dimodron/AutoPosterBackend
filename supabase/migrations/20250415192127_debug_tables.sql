alter table "public"."generated_posts" add column "is_publicated" boolean not null default false;

alter table "public"."payments" drop column "user_id";
alter table "public"."payments" add column "user_id" uuid not null;

alter table "public"."payments" enable row level security;

alter table "public"."tariffs" drop column "created_at";

alter table "public"."tariffs" drop column "description";

alter table "public"."tariffs" add column "service" text not null;

alter table "public"."tariffs" enable row level security;

alter table "public"."telegram_parsed_posts" add column "post_generated" uuid[] default '{}'::uuid[];

alter table "public"."payments" add constraint "payments_tariff_id_fkey" FOREIGN KEY (tariff_id) REFERENCES tariffs(id) ON UPDATE RESTRICT ON DELETE RESTRICT not valid;

alter table "public"."payments" validate constraint "payments_tariff_id_fkey";

create policy "Enable users to view their own data only"
on "public"."payments"
as permissive
for select
to authenticated
using ((( SELECT auth.uid() AS uid) = user_id));


create policy "Enable read access for all users"
on "public"."tariffs"
as permissive
for select
to public
using (true);