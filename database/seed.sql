-- Seed data for testing

-- Insert test user
INSERT INTO users (email, password_hash, name) VALUES
('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYQKZZzZzZz', 'Test User');

-- Insert test videos
INSERT INTO videos (user_id, filename, original_filename, file_path, file_size, status) VALUES
((SELECT id FROM users WHERE email = 'test@example.com'), 
 'test-video-1.mp4', 
 'my-video.mp4', 
 'storage/uploads/test-video-1.mp4', 
 10485760, 
 'uploaded');

-- Insert test processing job
INSERT INTO processing_jobs (video_id, user_id, status, progress, options) VALUES
((SELECT id FROM videos WHERE filename = 'test-video-1.mp4'),
 (SELECT id FROM users WHERE email = 'test@example.com'),
 'completed',
 100,
 '{"autoTrim": true, "autoCaptions": true, "autoMusic": false}');
