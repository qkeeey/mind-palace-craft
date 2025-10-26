-- Create floor_room_objects table for storing mind palace associations
-- This table links concepts from PDFs with room objects

CREATE TABLE IF NOT EXISTS public.floor_room_objects (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  floor_id UUID NOT NULL REFERENCES public.floors(id) ON DELETE CASCADE,
  room_id UUID NOT NULL REFERENCES public.rooms(id) ON DELETE CASCADE,
  room_object_id UUID NOT NULL REFERENCES public.room_objects(id) ON DELETE CASCADE,
  concept TEXT NOT NULL,
  concept_description TEXT,
  association_text TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(floor_id, room_object_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_floor_room_objects_floor_id ON public.floor_room_objects(floor_id);
CREATE INDEX IF NOT EXISTS idx_floor_room_objects_room_id ON public.floor_room_objects(room_id);
CREATE INDEX IF NOT EXISTS idx_floor_room_objects_object_id ON public.floor_room_objects(room_object_id);

-- Enable Row Level Security
ALTER TABLE public.floor_room_objects ENABLE ROW LEVEL SECURITY;

-- RLS Policies for floor_room_objects table
CREATE POLICY "Anyone can view floor room objects"
  ON public.floor_room_objects FOR SELECT
  USING (true);

CREATE POLICY "Anyone can create floor room objects"
  ON public.floor_room_objects FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Anyone can update floor room objects"
  ON public.floor_room_objects FOR UPDATE
  USING (true);

CREATE POLICY "Anyone can delete floor room objects"
  ON public.floor_room_objects FOR DELETE
  USING (true);
