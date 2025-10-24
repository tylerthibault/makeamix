"""
User business logic layer.
Contains all business rules and operations for user management.
"""
from datetime import date, datetime
from src import db
from src.models.user_model import User, Teacher, Student, Role


class UserLogic:
    """Business logic for user operations."""
    
    @staticmethod
    def create_user(data, user_type='user'):
        """Create a new user with validation and business rules."""
        # Basic validation
        if not data.get('email'):
            raise ValueError('Email is required')
        
        if not data.get('password'):
            raise ValueError('Password is required')
        
        if not data.get('first_name'):
            raise ValueError('First name is required')
        
        if not data.get('last_name'):
            raise ValueError('Last name is required')
        
        # Business rule: Check if email already exists
        if UserLogic.email_exists(data['email']):
            raise ValueError('Email already registered')
        
        # Password validation
        if len(data['password']) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        try:
            # Create user based on type
            if user_type == 'teacher':
                user = Teacher(
                    email=data['email'].lower().strip(),
                    first_name=data['first_name'].strip(),
                    last_name=data['last_name'].strip(),
                    employee_id=data.get('employee_id', '').strip() or None,
                    department=data.get('department', '').strip() or None,
                    specialization=data.get('specialization', '').strip() or None
                )
            elif user_type == 'student':
                user = Student(
                    email=data['email'].lower().strip(),
                    first_name=data['first_name'].strip(),
                    last_name=data['last_name'].strip(),
                    student_id=data.get('student_id', '').strip() or None,
                    grade_level=data.get('grade_level', '').strip() or None,
                    enrollment_date=date.today()
                )
            else:
                user = User(
                    email=data['email'].lower().strip(),
                    first_name=data['first_name'].strip(),
                    last_name=data['last_name'].strip()
                )
            
            # Set password
            user.set_password(data['password'])
            
            # Add default role if specified
            if data.get('default_role'):
                role = RoleLogic.get_role_by_name(data['default_role'])
                if role:
                    user.add_role(role)
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            
            return user
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create user: {str(e)}")
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password."""
        if not email or not password:
            return None
        
        user = User.query.filter_by(
            email=email.lower().strip(), 
            is_active=True
        ).first()
        
        if user and user.check_password(password):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        
        return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID."""
        return User.query.filter_by(id=user_id, is_active=True).first()
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email."""
        return User.query.filter_by(email=email.lower().strip()).first()
    
    @staticmethod
    def email_exists(email):
        """Check if email already exists."""
        return User.query.filter_by(email=email.lower().strip()).first() is not None
    
    @staticmethod
    def update_user(user_id, data):
        """Update user information."""
        user = UserLogic.get_user_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        
        try:
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'is_active', 'is_verified']
            for field in allowed_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            # Handle password update separately
            if 'password' in data and data['password']:
                if len(data['password']) < 8:
                    raise ValueError('Password must be at least 8 characters long')
                user.set_password(data['password'])
            
            # Update timestamp
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update user: {str(e)}")
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate a user account."""
        user = UserLogic.get_user_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return user
    
    @staticmethod
    def activate_user(user_id):
        """Activate a user account."""
        user = UserLogic.get_user_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        
        user.is_active = True
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return user
    
    @staticmethod
    def get_all_teachers(include_inactive=False):
        """Get all teacher users."""
        query = Teacher.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.all()
    
    @staticmethod
    def get_all_students(include_inactive=False):
        """Get all student users."""
        query = Student.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.all()
    
    @staticmethod
    def get_users_by_role(role_name):
        """Get all users with a specific role."""
        role = RoleLogic.get_role_by_name(role_name)
        if not role:
            return []
        return [user for user in role.users if user.is_active]


class RoleLogic:
    """Business logic for role operations."""
    
    @staticmethod
    def create_role(name, description=None):
        """Create a new role."""
        if not name:
            raise ValueError('Role name is required')
        
        # Check if role already exists
        if RoleLogic.role_exists(name):
            raise ValueError('Role already exists')
        
        try:
            role = Role(name=name.lower().strip(), description=description)
            db.session.add(role)
            db.session.commit()
            return role
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create role: {str(e)}")
    
    @staticmethod
    def get_role_by_name(name):
        """Get role by name."""
        return Role.query.filter_by(name=name.lower().strip(), is_active=True).first()
    
    @staticmethod
    def get_role_by_id(role_id):
        """Get role by ID."""
        return Role.query.filter_by(id=role_id, is_active=True).first()
    
    @staticmethod
    def role_exists(name):
        """Check if role exists."""
        return Role.query.filter_by(name=name.lower().strip()).first() is not None
    
    @staticmethod
    def get_all_roles(include_inactive=False):
        """Get all roles."""
        query = Role.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(Role.name).all()
    
    @staticmethod
    def assign_role_to_user(user_id, role_name):
        """Assign a role to a user."""
        user = UserLogic.get_user_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        
        role = RoleLogic.get_role_by_name(role_name)
        if not role:
            raise ValueError('Role not found')
        
        if role in user.roles:
            raise ValueError(f'User already has role "{role_name}"')
        
        try:
            user.add_role(role)
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to assign role: {str(e)}")
    
    @staticmethod
    def remove_role_from_user(user_id, role_name):
        """Remove a role from a user."""
        user = UserLogic.get_user_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        
        role = RoleLogic.get_role_by_name(role_name)
        if not role:
            raise ValueError('Role not found')
        
        if role not in user.roles:
            raise ValueError(f'User does not have role "{role_name}"')
        
        try:
            user.remove_role(role)
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to remove role: {str(e)}")
    
    @staticmethod
    def initialize_default_roles():
        """Initialize default roles for the application."""
        default_roles = [
            ('admin', 'System administrator with full access'),
            ('teacher', 'Teacher with access to teaching features'),
            ('student', 'Student with access to learning features'),
            ('user', 'Basic user with minimal access')
        ]
        
        for role_name, description in default_roles:
            if not RoleLogic.role_exists(role_name):
                try:
                    RoleLogic.create_role(role_name, description)
                except Exception as e:
                    print(f"Warning: Could not create role {role_name}: {e}")
