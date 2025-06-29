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
      10,
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

CREATE OR REPLACE FUNCTION public.merge_duplicates_after_insert()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
  merged_user_ids uuid[];
  min_id integer;
BEGIN
  -- Собираем объединённый массив user_ids для всех записей с одинаковым content
  SELECT array_agg(DISTINCT user_id_elem)
  INTO merged_user_ids
  FROM (
    SELECT unnest(users) AS user_id_elem
    FROM telegram_parsed_posts
    WHERE content = NEW.content
  ) sub;
  
  -- Определяем id записи, которую оставим (например, с минимальным id)
  SELECT min(id)
  INTO min_id
  FROM telegram_parsed_posts
  WHERE content = NEW.content;
  
  -- Обновляем выбранную запись объединённым массивом
  UPDATE telegram_parsed_posts
  SET users = merged_user_ids
  WHERE id = min_id;
  
  -- Удаляем все остальные дубликаты по данному ключу
  DELETE FROM telegram_parsed_posts
  WHERE content = NEW.content AND id <> min_id;
  
  RETURN NEW;
END;
$function$
;


CREATE TRIGGER on_user_created AFTER INSERT ON auth.users FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();