alter table "public"."telegram" add column "active_until" timestamp with time zone;

alter table "public"."telegram" add column "autoposting_timeout" integer not null default 15;

alter table "public"."telegram_parsed_posts" drop column "post_generated";

alter table "public"."telegram_parsed_posts" add column "users_generated" uuid[] default '{}'::uuid[];

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
      created_at,
      user_id,
      channels_to_parse,
      telegram_maintainer_channel,
      autoposting_timeout,
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
      NOW(),
      NEW.id,              -- cвязка по user_id = auth.users.id
      ARRAY[]::varchar[],     -- Пустой массив строк (тип _varchar)
      '',
      30,
      30,
      'serious',
      'advertising_creative',
      500,
      true,
      true,
      1,
      ARRAY['Нужно уникализировать пост', 'Пост должен содержать экспертное мнение', 'Нужно повысить читаемость поста']::text[]
    );

    -- 3) Создаём оплату по тестовому периоду
    INSERT INTO public.payments (
      id,
      status,
      valid_until,
      payed_at,
      tariff_id,
      amount,
      currency,
      balance,
      user_id
    )
    VALUES (
      DEFAULT,              -- id автоинкрементируется
      'succeeded',
      NOW() + INTERVAL '1 day',
      NOW(),              -- cвязка по user_id = auth.users.id
      3,     -- Пустой массив строк (тип _varchar)
      0,
     'RUB',
      0,
      NEW.id
    );

    RETURN NEW;
END;$function$
;


