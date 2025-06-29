set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.delete_old_generated_posts()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
DECLARE
    rec RECORD;
    filename TEXT;
BEGIN
    FOR rec IN 
        WITH deleted AS (
            DELETE FROM public.generated_posts
            WHERE created_at < (NOW() - INTERVAL '2 days')
              AND is_publicated = false
            RETURNING id, image_url
        )
        SELECT id, image_url FROM deleted
    LOOP
        -- Извлекаем имя файла из URL: всё, что находится после "generated_images/" до символа "?"
        filename := substring(rec.image_url from 'generated-images/([^?]+)');
        
        IF filename IS NOT NULL THEN
            DELETE FROM storage.objects
            WHERE bucket_id = 'generated-images'
              AND name = filename;
        END IF;
    END LOOP;
END;
$function$
;

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
      is_active,
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
      true,
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


drop trigger if exists "on_user_created" on "auth"."users";