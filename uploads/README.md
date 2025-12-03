# Uploads Directory

This directory stores user-uploaded audio files.

## Structure

```
uploads/
└── songs/
    ├── user_1/
    │   ├── song_abc123def456.mp3
    │   └── song_xyz789ghi012.mp3
    └── user_2/
        └── song_jkl345mno678.mp3
```

## File Naming Convention

- **User directories**: `user_{user_id}`
- **Song files**: `song_{short_id}.{ext}`
  - `short_id`: 12-character alphanumeric unique identifier
  - `ext`: Original file extension (defaults to .mp3)

## Notes

- User directories are automatically created when uploading songs
- Files are automatically deleted when songs are removed
- This directory is git-ignored to prevent committing user data
- Ensure proper permissions for the web server to read/write files
