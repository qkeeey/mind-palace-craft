-- Create floors table
CREATE TABLE public.floors (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'generating' CHECK (status IN ('generating', 'completed', 'failed')),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create pdf_files table
CREATE TABLE public.pdf_files (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  floor_id UUID NOT NULL REFERENCES public.floors(id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  extracted_text TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create rooms table
CREATE TABLE public.rooms (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  thumbnail_url TEXT,
  object_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create room_objects table
CREATE TABLE public.room_objects (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  room_id UUID NOT NULL REFERENCES public.rooms(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  image_url TEXT NOT NULL,
  position INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create floor_rooms junction table
CREATE TABLE public.floor_rooms (
  floor_id UUID NOT NULL REFERENCES public.floors(id) ON DELETE CASCADE,
  room_id UUID NOT NULL REFERENCES public.rooms(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  PRIMARY KEY (floor_id, room_id)
);

-- Create associations table (the mind palace output)
CREATE TABLE public.associations (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  floor_id UUID NOT NULL REFERENCES public.floors(id) ON DELETE CASCADE,
  object_id UUID NOT NULL REFERENCES public.room_objects(id) ON DELETE CASCADE,
  core_concept TEXT NOT NULL,
  mnemonic_text TEXT NOT NULL,
  display_order INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create indexes for better performance
CREATE INDEX idx_floors_user_id ON public.floors(user_id);
CREATE INDEX idx_pdf_files_floor_id ON public.pdf_files(floor_id);
CREATE INDEX idx_rooms_user_id ON public.rooms(user_id);
CREATE INDEX idx_room_objects_room_id ON public.room_objects(room_id);
CREATE INDEX idx_floor_rooms_floor_id ON public.floor_rooms(floor_id);
CREATE INDEX idx_floor_rooms_room_id ON public.floor_rooms(room_id);
CREATE INDEX idx_associations_floor_id ON public.associations(floor_id);
CREATE INDEX idx_associations_display_order ON public.associations(floor_id, display_order);

-- Enable Row Level Security on all tables
ALTER TABLE public.floors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pdf_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.room_objects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.floor_rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.associations ENABLE ROW LEVEL SECURITY;

-- RLS Policies for floors table
CREATE POLICY "Users can view their own floors"
  ON public.floors FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own floors"
  ON public.floors FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own floors"
  ON public.floors FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own floors"
  ON public.floors FOR DELETE
  USING (auth.uid() = user_id);

-- RLS Policies for pdf_files table
CREATE POLICY "Users can view PDFs from their own floors"
  ON public.pdf_files FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.floors
      WHERE floors.id = pdf_files.floor_id
      AND floors.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert PDFs to their own floors"
  ON public.pdf_files FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.floors
      WHERE floors.id = pdf_files.floor_id
      AND floors.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update PDFs in their own floors"
  ON public.pdf_files FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.floors
      WHERE floors.id = pdf_files.floor_id
      AND floors.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete PDFs from their own floors"
  ON public.pdf_files FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.floors
      WHERE floors.id = pdf_files.floor_id
      AND floors.user_id = auth.uid()
    )
  );

-- RLS Policies for rooms table
CREATE POLICY "Users can view their own rooms"
  ON public.rooms FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own rooms"
  ON public.rooms FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own rooms"
  ON public.rooms FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own rooms"
  ON public.rooms FOR DELETE
  USING (auth.uid() = user_id);

-- RLS Policies for room_objects table
CREATE POLICY "Users can view objects from their own rooms"
  ON public.room_objects FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.rooms
      WHERE rooms.id = room_objects.room_id
      AND rooms.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert objects to their own rooms"
  ON public.room_objects FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.rooms
      WHERE rooms.id = room_objects.room_id
      AND rooms.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update objects in their own rooms"
  ON public.room_objects FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.rooms
      WHERE rooms.id = room_objects.room_id
      AND rooms.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete objects from their own rooms"
  ON public.room_objects FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.rooms
      WHERE rooms.id = room_objects.room_id
      AND rooms.user_id = auth.uid()
    )
  );

-- RLS Policies for floor_rooms junction table
CREATE POLICY "Users can view their own floor-room connections"
  ON public.floor_rooms FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.floors
      WHERE floors.id = floor_rooms.floor_id
      AND floors.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create floor-room connections for their own floors"
  ON public.floor_rooms FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.floors
      WHERE floors.id = floor_rooms.floor_id
      AND floors.user_id = auth.uid()
    )
    AND
    EXISTS (
      SELECT 1 FROM public.rooms
      WHERE rooms.id = floor_rooms.room_id
      AND rooms.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete their own floor-room connections"
  ON public.floor_rooms FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.floors
      WHERE floors.id = floor_rooms.floor_id
      AND floors.user_id = auth.uid()
    )
  );

-- RLS Policies for associations table
CREATE POLICY "Users can view associations from their own floors"
  ON public.associations FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.floors
      WHERE floors.id = associations.floor_id
      AND floors.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create associations for their own floors"
  ON public.associations FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.floors
      WHERE floors.id = associations.floor_id
      AND floors.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update associations in their own floors"
  ON public.associations FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.floors
      WHERE floors.id = associations.floor_id
      AND floors.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete associations from their own floors"
  ON public.associations FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.floors
      WHERE floors.id = associations.floor_id
      AND floors.user_id = auth.uid()
    )
  );

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_floors_updated_at
  BEFORE UPDATE ON public.floors
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_rooms_updated_at
  BEFORE UPDATE ON public.rooms
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Create function to automatically update room object_count
CREATE OR REPLACE FUNCTION public.update_room_object_count()
RETURNS TRIGGER AS $$
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
$$ LANGUAGE plpgsql;

-- Create trigger to maintain room object_count
CREATE TRIGGER maintain_room_object_count
  AFTER INSERT OR DELETE ON public.room_objects
  FOR EACH ROW
  EXECUTE FUNCTION public.update_room_object_count();