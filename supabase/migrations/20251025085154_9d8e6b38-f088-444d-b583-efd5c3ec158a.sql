-- Enable public uploads to room-images bucket
CREATE POLICY "Anyone can upload room images"
ON storage.objects
FOR INSERT
WITH CHECK (bucket_id = 'room-images');

CREATE POLICY "Anyone can view room images"
ON storage.objects
FOR SELECT
USING (bucket_id = 'room-images');

CREATE POLICY "Anyone can update room images"
ON storage.objects
FOR UPDATE
USING (bucket_id = 'room-images');

CREATE POLICY "Anyone can delete room images"
ON storage.objects
FOR DELETE
USING (bucket_id = 'room-images');

-- Enable public uploads to pdfs bucket
CREATE POLICY "Anyone can upload PDFs"
ON storage.objects
FOR INSERT
WITH CHECK (bucket_id = 'pdfs');

CREATE POLICY "Anyone can view PDFs"
ON storage.objects
FOR SELECT
USING (bucket_id = 'pdfs');

CREATE POLICY "Anyone can update PDFs"
ON storage.objects
FOR UPDATE
USING (bucket_id = 'pdfs');

CREATE POLICY "Anyone can delete PDFs"
ON storage.objects
FOR DELETE
USING (bucket_id = 'pdfs');