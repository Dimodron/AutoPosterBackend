alter table "public"."telegram" alter column "parsing_timeout" set default 30;


CREATE TRIGGER trigger_handle_new_user AFTER INSERT ON auth.users FOR EACH ROW EXECUTE FUNCTION handle_new_user();


