-- ============================================================
-- FIX IMAGE STORAGE PERMISSIONS
-- Run this in Supabase SQL Editor
-- ============================================================

-- Enable public access to room-images bucket (SELECT/READ)
DROP POLICY IF EXISTS "Anyone can view room images" ON storage.objects;
CREATE POLICY "Anyone can view room images"
ON storage.objects
FOR SELECT
USING (bucket_id = 'room-images');

-- Allow authenticated and anon users to upload
DROP POLICY IF EXISTS "Anyone can upload room images" ON storage.objects;
CREATE POLICY "Anyone can upload room images"
ON storage.objects
FOR INSERT
WITH CHECK (bucket_id = 'room-images');

-- Allow update of room images
DROP POLICY IF EXISTS "Anyone can update room images" ON storage.objects;
CREATE POLICY "Anyone can update room images"
ON storage.objects
FOR UPDATE
USING (bucket_id = 'room-images');

-- Allow delete of room images
DROP POLICY IF EXISTS "Anyone can delete room images" ON storage.objects;
CREATE POLICY "Anyone can delete room images"
ON storage.objects
FOR DELETE
USING (bucket_id = 'room-images');

-- Make sure the bucket is public
UPDATE storage.buckets 
SET public = true 
WHERE id = 'room-images';

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================
-- Check if bucket is public
SELECT id, name, public FROM storage.buckets WHERE id = 'room-images';
-- Should show: public = true

-- Check policies
SELECT * FROM pg_policies WHERE tablename = 'objects' AND policyname LIKE '%room image%';
-- Should show 4 policies (view, upload, update, delete)
