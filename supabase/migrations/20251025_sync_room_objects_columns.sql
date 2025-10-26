-- Add object_name as alias for name (for backward compatibility)
ALTER TABLE public.room_objects ADD COLUMN IF NOT EXISTS object_name TEXT;
ALTER TABLE public.room_objects ADD COLUMN IF NOT EXISTS object_description TEXT;
ALTER TABLE public.room_objects ADD COLUMN IF NOT EXISTS short_description TEXT;

-- Update existing data to populate new columns
UPDATE public.room_objects 
SET object_name = name, 
    object_description = description,
    short_description = description
WHERE object_name IS NULL;

-- Create trigger to keep columns in sync
CREATE OR REPLACE FUNCTION sync_room_object_columns()
RETURNS TRIGGER AS $$
BEGIN
  -- Sync name fields
  IF NEW.name IS DISTINCT FROM OLD.name THEN
    NEW.object_name = NEW.name;
  ELSIF NEW.object_name IS DISTINCT FROM OLD.object_name THEN
    NEW.name = NEW.object_name;
  END IF;
  
  -- Sync description fields
  IF NEW.description IS DISTINCT FROM OLD.description THEN
    NEW.object_description = NEW.description;
    NEW.short_description = NEW.description;
  ELSIF NEW.object_description IS DISTINCT FROM OLD.object_description THEN
    NEW.description = NEW.object_description;
    NEW.short_description = NEW.object_description;
  ELSIF NEW.short_description IS DISTINCT FROM OLD.short_description THEN
    NEW.description = NEW.short_description;
    NEW.object_description = NEW.short_description;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_room_object_columns_trigger
  BEFORE INSERT OR UPDATE ON public.room_objects
  FOR EACH ROW
  EXECUTE FUNCTION sync_room_object_columns();
