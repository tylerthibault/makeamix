"""
This module defines the User model for the application. It contains a base user class and child teacher class and student class. It uses SQLAlchemy for the ORM. There will be a roles table as well and the user will be able to be attached to multiple roles.
"""
import hashlib
from datetime import datetime, date
from src import db


# Association table for many-to-many relationship between users and roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow)
)


class Role(db.Model):
    """Role model for user permissions."""
    
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        """Convert role to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class User(db.Model):
    """Base user model."""
    
    __tablename__ = 'users'
    
    # Primary key and timestamps
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Basic user information
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # User status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # User type for polymorphic inheritance
    user_type = db.Column(db.String(20), nullable=False)
    
    # Many-to-many relationship with roles
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                           backref=db.backref('users', lazy=True))
    
    # Polymorphic configuration
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def full_name(self):
        """Get the user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def set_password(self, password):
        """Set password using SHA-256 hashing (simple approach)."""
        self.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def check_password(self, password):
        """Check if provided password matches the stored hash."""
        return self.password_hash == hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)
    
    def add_role(self, role):
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)
    
    def remove_role(self, role):
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)
    
    def get_role_names(self):
        """Get list of role names for this user."""
        return [role.name for role in self.roles]
    
    def to_dict(self):
        """Convert user to dictionary, excluding sensitive data."""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'user_type': self.user_type,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'role_names': self.get_role_names()
        }


class Teacher(User):
    """Teacher user model with additional teacher-specific fields."""
    
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    # Teacher-specific information
    employee_id = db.Column(db.String(20), unique=True, nullable=True)
    department = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    
    # Teacher status
    hire_date = db.Column(db.Date, default=date.today)
    
    # Polymorphic configuration
    __mapper_args__ = {
        'polymorphic_identity': 'teacher',
    }
    
    def __repr__(self):
        return f'<Teacher {self.email}>'
    
    def to_dict(self):
        """Convert teacher to dictionary."""
        result = super().to_dict()
        result.update({
            'employee_id': self.employee_id,
            'department': self.department,
            'specialization': self.specialization,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None
        })
        return result


class Student(User):
    """Student user model with additional student-specific fields."""
    
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    # Student-specific information
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    grade_level = db.Column(db.String(20))
    enrollment_date = db.Column(db.Date, default=date.today)
    
    # Student status
    is_enrolled = db.Column(db.Boolean, default=True, nullable=False)
    
    # Polymorphic configuration
    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }
    
    def __repr__(self):
        return f'<Student {self.email}>'
    
    def to_dict(self):
        """Convert student to dictionary."""
        result = super().to_dict()
        result.update({
            'student_id': self.student_id,
            'grade_level': self.grade_level,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'is_enrolled': self.is_enrolled
        })
        return result