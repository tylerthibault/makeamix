# Make a Mix - Project Overview

## 🎵 Project Description

**Make a Mix** is an educational music platform that connects teachers and students through shared music experiences. The platform enables teachers to create virtual classrooms where they can upload music, curate playlists (called "mixes"), and give students access to explore and create their own musical collections.

## 🎯 Core Features

### For Teachers
- **Classroom Management**: Create and manage virtual music classrooms
- **Music Upload**: Upload songs to their classroom library
- **Mix Creation**: Create curated playlists/mixes with custom ordering
- **Student Management**: Invite and manage students in their classes
- **Content Control**: Full control over what music is available to students

### For Students
- **Class Access**: Join teacher-created classrooms
- **Music Library**: Access to teacher-uploaded music collection
- **Personal Mixes**: Create their own playlists from available music
- **Listening Experience**: Stream music individually or from teacher's curated mixes

## 🏗️ Project Structure

```
makeamix/
├── run.py                          # Application entry point
├── src/
│   ├── __init__.py                 # Package initialization
│   ├── controllers/
│   │   └── routes.py               # URL routing and view controllers
│   ├── logic/                      # Business logic layer
│   ├── models/
│   │   └── base.py                 # Database models
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css           # Styling
│   │   ├── img/                   # Images and media assets
│   │   └── js/
│   │       └── main.js            # Client-side JavaScript
│   ├── templates/
│   │   ├── bases/
│   │   │   ├── private.html       # Base template for authenticated users
│   │   │   └── public.html        # Base template for public pages
│   │   ├── private/
│   │   │   ├── student/
│   │   │   │   └── dashboard/
│   │   │   │       └── index.html # Student dashboard
│   │   │   └── teacher/
│   │   │       └── dashboard/
│   │   │           └── index.html # Teacher dashboard
│   │   └── public/
│   │       ├── components/        # Reusable UI components
│   │       └── landing/
│   │           └── index.html     # Landing page
│   └── utils/
│       └── logger.py              # Logging utilities
└── .github/
    └── instructions/
        └── project overview.instructions.md
```

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLAlchemy (assumed from models structure)
- **Architecture**: MVC pattern with separation of concerns

## 👥 User Roles

### Teacher
- Primary content creator and classroom manager
- Can upload music files to their classroom
- Creates and manages mixes (playlists)
- Controls student access and permissions
- Has administrative rights within their classroom

### Student  
- Consumer of teacher-provided content
- Can access teacher's music library
- Can create personal mixes from available songs
- Limited to content shared by their teachers

## 🎼 Key Concepts

### Mix
A "mix" is essentially a playlist - an ordered collection of songs that can be:
- Created by teachers as curated content
- Created by students from their available music library
- Played in sequence or shuffled
- Shared within the classroom context

### Classroom
A virtual space where:
- Teachers upload and organize music
- Students gain access to shared content
- Mixes are created and shared
- Learning and musical exploration happens

## 🚀 Development Goals

1. **Intuitive User Experience**: Simple, clean interface for both teachers and students
2. **Scalable Architecture**: Modular design supporting growth
3. **Security**: Proper authentication and authorization
4. **Performance**: Efficient music streaming and file management
5. **Educational Focus**: Features that enhance learning and musical discovery

## 📋 Future Enhancements

- Real-time collaboration on mixes
- Music recommendation system
- Analytics for teachers (listening habits, popular songs)
- Integration with music streaming services
- Mobile application
- Assignment creation (e.g., "create a mix about jazz history")

## 🔧 Development Setup

1. Install Python dependencies
2. Configure database connection
3. Set up file storage for music uploads
4. Configure authentication system
5. Run Flask development server via `run.py`

This platform aims to bridge education and music, creating an engaging environment where teachers can share their musical knowledge and students can explore, learn, and create their own musical experiences.