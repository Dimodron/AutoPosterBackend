alter table "public"."telegram" alter column "autoposting_timeout" drop default;

alter table "public"."telegram" alter column "parsing_timeout" drop default;

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.handle_new_user()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$BEGIN
  -- 1) Создаём профиль
  RAISE NOTICE 'Создаю профиль для пользователя %', NEW.id;

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

  RAISE NOTICE 'Профиль успешно создан.';

  -- 2) Создаём запись в telegram
  RAISE NOTICE 'Создаю telegram настройки для пользователя %', NEW.id;

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
    prompts,
    active_until
  )
  VALUES (
    DEFAULT,
    NOW(),
    NEW.id,
    ARRAY[]::varchar[],
    '',
    30,
    30,
    'serious',
    'advertising_creative',
    500,
    true,
    true,
    1,
    ARRAY[
      'Нужно уникализировать пост',
      'Пост должен содержать экспертное мнение',
      'Нужно повысить читаемость поста'
    ]::text[],
    NOW() + INTERVAL '1 day'
  );

  RAISE NOTICE 'Telegram настройки успешно созданы.';

  -- 3) Создаём тестовую оплату
  RAISE NOTICE 'Создаю оплату для пользователя %', NEW.id;

  BEGIN
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
      DEFAULT,
      'succeeded',
      NOW() + INTERVAL '1 day',
      NOW(),
      3,
      0,
      'RUB',
      0,
      NEW.id
    );

    RAISE NOTICE 'Оплата успешно добавлена.';
  EXCEPTION
    WHEN OTHERS THEN
      RAISE NOTICE 'Ошибка при создании оплаты: %', SQLERRM;
  END;

  RETURN NEW;
END;$function$
;


