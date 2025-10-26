-- Make user_id nullable in floors table
ALTER TABLE public.floors ALTER COLUMN user_id DROP NOT NULL;

-- Make user_id nullable in rooms table
ALTER TABLE public.rooms ALTER COLUMN user_id DROP NOT NULL;

-- Drop all existing RLS policies for floors
DROP POLICY IF EXISTS "Users can create their own floors" ON public.floors;
DROP POLICY IF EXISTS "Users can delete their own floors" ON public.floors;
DROP POLICY IF EXISTS "Users can update their own floors" ON public.floors;
DROP POLICY IF EXISTS "Users can view their own floors" ON public.floors;

-- Create public policies for floors (anyone can do anything)
CREATE POLICY "Anyone can view floors" ON public.floors
FOR SELECT USING (true);

CREATE POLICY "Anyone can create floors" ON public.floors
FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update floors" ON public.floors
FOR UPDATE USING (true);

CREATE POLICY "Anyone can delete floors" ON public.floors
FOR DELETE USING (true);

-- Drop all existing RLS policies for rooms
DROP POLICY IF EXISTS "Users can create their own rooms" ON public.rooms;
DROP POLICY IF EXISTS "Users can delete their own rooms" ON public.rooms;
DROP POLICY IF EXISTS "Users can update their own rooms" ON public.rooms;
DROP POLICY IF EXISTS "Users can view their own rooms" ON public.rooms;

-- Create public policies for rooms (anyone can do anything)
CREATE POLICY "Anyone can view rooms" ON public.rooms
FOR SELECT USING (true);

CREATE POLICY "Anyone can create rooms" ON public.rooms
FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update rooms" ON public.rooms
FOR UPDATE USING (true);

CREATE POLICY "Anyone can delete rooms" ON public.rooms
FOR DELETE USING (true);

-- Update pdf_files policies (based on public floors)
DROP POLICY IF EXISTS "Users can delete PDFs from their own floors" ON public.pdf_files;
DROP POLICY IF EXISTS "Users can insert PDFs to their own floors" ON public.pdf_files;
DROP POLICY IF EXISTS "Users can update PDFs in their own floors" ON public.pdf_files;
DROP POLICY IF EXISTS "Users can view PDFs from their own floors" ON public.pdf_files;

CREATE POLICY "Anyone can view PDFs" ON public.pdf_files
FOR SELECT USING (true);

CREATE POLICY "Anyone can create PDFs" ON public.pdf_files
FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update PDFs" ON public.pdf_files
FOR UPDATE USING (true);

CREATE POLICY "Anyone can delete PDFs" ON public.pdf_files
FOR DELETE USING (true);

-- Update room_objects policies (based on public rooms)
DROP POLICY IF EXISTS "Users can delete objects from their own rooms" ON public.room_objects;
DROP POLICY IF EXISTS "Users can insert objects to their own rooms" ON public.room_objects;
DROP POLICY IF EXISTS "Users can update objects in their own rooms" ON public.room_objects;
DROP POLICY IF EXISTS "Users can view objects from their own rooms" ON public.room_objects;

CREATE POLICY "Anyone can view room objects" ON public.room_objects
FOR SELECT USING (true);

CREATE POLICY "Anyone can create room objects" ON public.room_objects
FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update room objects" ON public.room_objects
FOR UPDATE USING (true);

CREATE POLICY "Anyone can delete room objects" ON public.room_objects
FOR DELETE USING (true);

-- Update associations policies (based on public floors)
DROP POLICY IF EXISTS "Users can create associations for their own floors" ON public.associations;
DROP POLICY IF EXISTS "Users can delete associations from their own floors" ON public.associations;
DROP POLICY IF EXISTS "Users can update associations in their own floors" ON public.associations;
DROP POLICY IF EXISTS "Users can view associations from their own floors" ON public.associations;

CREATE POLICY "Anyone can view associations" ON public.associations
FOR SELECT USING (true);

CREATE POLICY "Anyone can create associations" ON public.associations
FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update associations" ON public.associations
FOR UPDATE USING (true);

CREATE POLICY "Anyone can delete associations" ON public.associations
FOR DELETE USING (true);

-- Update floor_rooms policies
DROP POLICY IF EXISTS "Users can create floor-room connections for their own floors" ON public.floor_rooms;
DROP POLICY IF EXISTS "Users can delete their own floor-room connections" ON public.floor_rooms;
DROP POLICY IF EXISTS "Users can view their own floor-room connections" ON public.floor_rooms;

CREATE POLICY "Anyone can view floor-room connections" ON public.floor_rooms
FOR SELECT USING (true);

CREATE POLICY "Anyone can create floor-room connections" ON public.floor_rooms
FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update floor-room connections" ON public.floor_rooms
FOR UPDATE USING (true);

CREATE POLICY "Anyone can delete floor-room connections" ON public.floor_rooms
FOR DELETE USING (true);