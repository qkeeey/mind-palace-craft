-- Create storage bucket for PDF files
INSERT INTO storage.buckets (id, name, public)
VALUES ('pdfs', 'pdfs', false);

-- Create storage bucket for room images
INSERT INTO storage.buckets (id, name, public)
VALUES ('room-images', 'room-images', false);

-- RLS Policies for pdfs bucket
-- Users can upload their own PDFs
CREATE POLICY "Users can upload their own PDFs"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'pdfs' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can view their own PDFs
CREATE POLICY "Users can view their own PDFs"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'pdfs' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can update their own PDFs
CREATE POLICY "Users can update their own PDFs"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'pdfs' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can delete their own PDFs
CREATE POLICY "Users can delete their own PDFs"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'pdfs' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- RLS Policies for room-images bucket
-- Users can upload their own room images
CREATE POLICY "Users can upload their own room images"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'room-images' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can view their own room images
CREATE POLICY "Users can view their own room images"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'room-images' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can update their own room images
CREATE POLICY "Users can update their own room images"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'room-images' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can delete their own room images
CREATE POLICY "Users can delete their own room images"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'room-images' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);