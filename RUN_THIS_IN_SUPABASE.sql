-- ============================================================
-- MIGRATION SCRIPT: Add floor_room_objects table and sync columns
-- Run this in Supabase SQL Editor (Dashboard > SQL Editor > New Query)
-- ============================================================

-- STEP 1: Add missing columns to room_objects table
-- ============================================================
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

DROP TRIGGER IF EXISTS sync_room_object_columns_trigger ON public.room_objects;
CREATE TRIGGER sync_room_object_columns_trigger
  BEFORE INSERT OR UPDATE ON public.room_objects
  FOR EACH ROW
  EXECUTE FUNCTION sync_room_object_columns();

-- STEP 2: Create floor_room_objects table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.floor_room_objects (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  floor_id UUID NOT NULL REFERENCES public.floors(id) ON DELETE CASCADE,
  room_id UUID NOT NULL REFERENCES public.rooms(id) ON DELETE CASCADE,
  room_object_id UUID NOT NULL REFERENCES public.room_objects(id) ON DELETE CASCADE,
  concept TEXT NOT NULL,
  concept_description TEXT,
  association_text TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_floor_room_objects_floor_id ON public.floor_room_objects(floor_id);
CREATE INDEX IF NOT EXISTS idx_floor_room_objects_room_id ON public.floor_room_objects(room_id);
CREATE INDEX IF NOT EXISTS idx_floor_room_objects_room_object_id ON public.floor_room_objects(room_object_id);

-- Enable Row Level Security
ALTER TABLE public.floor_room_objects ENABLE ROW LEVEL SECURITY;

-- RLS Policies for floor_room_objects table (public access for now)
DROP POLICY IF EXISTS "Anyone can view floor room objects" ON public.floor_room_objects;
CREATE POLICY "Anyone can view floor room objects" ON public.floor_room_objects
FOR SELECT USING (true);

DROP POLICY IF EXISTS "Anyone can create floor room objects" ON public.floor_room_objects;
CREATE POLICY "Anyone can create floor room objects" ON public.floor_room_objects
FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Anyone can update floor room objects" ON public.floor_room_objects;
CREATE POLICY "Anyone can update floor room objects" ON public.floor_room_objects
FOR UPDATE USING (true);

DROP POLICY IF EXISTS "Anyone can delete floor room objects" ON public.floor_room_objects;
CREATE POLICY "Anyone can delete floor room objects" ON public.floor_room_objects
FOR DELETE USING (true);

-- Create trigger for automatic timestamp updates
DROP TRIGGER IF EXISTS update_floor_room_objects_updated_at ON public.floor_room_objects;
CREATE TRIGGER update_floor_room_objects_updated_at
  BEFORE UPDATE ON public.floor_room_objects
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================
-- MIGRATION COMPLETE
-- ============================================================
-- You should now see:
-- 1. room_objects table with object_name, object_description, short_description columns
-- 2. floor_room_objects table created
-- 3. All necessary indexes and RLS policies applied
-- ============================================================
