-- Fix function search_path security warnings
-- Update the update_updated_at_column function
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- Update the update_room_object_count function
CREATE OR REPLACE FUNCTION public.update_room_object_count()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE public.rooms
    SET object_count = object_count + 1,
        thumbnail_url = COALESCE(thumbnail_url, NEW.image_url)
    WHERE id = NEW.room_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE public.rooms
    SET object_count = GREATEST(0, object_count - 1)
    WHERE id = OLD.room_id;
  END IF;
  RETURN NULL;
END;
$$;