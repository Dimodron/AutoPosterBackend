alter table "public"."payments" drop column "created_at";

alter table "public"."payments" alter column "payed_at" set default now();

alter table "public"."payments" alter column "payed_at" set not null;

alter table "public"."payments" alter column "payed_at" set data type timestamp with time zone using "payed_at"::timestamp with time zone;

alter table "public"."payments" alter column "payment_id" set data type uuid using "payment_id"::uuid;

alter table "public"."tariffs" add column "days_valid" integer not null default 30;

alter table "public"."telegram" drop column "is_active";

alter table "public"."telegram" add column "active_until" timestamp with time zone not null default (now() + '1 day'::interval);

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.handle_new_user()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$BEGIN
    INSERT INTO public.profiles (
        user_id,
        firstname,
        lastname,
        company,
        postal_code,
        country,
        language,
        timezone,
        currency,
        balance,
        is_active
    )
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data ->> 'firstname', ''),
        COALESCE(NEW.raw_user_meta_data ->> 'lastname', ''),
        COALESCE(NEW.raw_user_meta_data ->> 'company', ''),
        COALESCE(NEW.raw_user_meta_data ->> 'postal_code', ''),
        COALESCE(NEW.raw_user_meta_data ->> 'country', ''),
        'RU',
        COALESCE(NEW.raw_user_meta_data ->> 'timezone', 'UTC'),
        'RUB',
        0.0,
        true
    );

    -- 2) Создаём запись в telegram
    INSERT INTO public.telegram (
      id,
      active_until,
      created_at,
      user_id,
      channels_to_parse,
      telegram_maintainer_channel,
      parsing_timeout,
      tov,
      prompt_base,
      words_count,
      use_emoji,
      use_hashtag,
      count_of_posts,
      prompts
    )
    VALUES (
      DEFAULT,              -- id автоинкрементируется
      NOW() + INTERVAL '1 day',
      NOW(),
      NEW.id,              -- cвязка по user_id = auth.users.id
      ARRAY[]::varchar[],     -- Пустой массив строк (тип _varchar)
      '',
      30,
      'serious',
      'advertising_creative',
      500,
      true,
      true,
      10,
      ARRAY['Нужно уникализировать пост', 'Пост должен содержать экспертное мнение', 'Нужно повысить читаемость поста']::text[]
    );

    RETURN NEW;
END;$function$
;


