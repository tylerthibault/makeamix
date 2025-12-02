from flask import flash
from src import bcrypt

import re
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

class UserService:
    

    @staticmethod
    def create_user(data):
        # validate data
        is_valid = UserService.validate_registration(data)
        if not is_valid:
            return None
        from src.models.user import User
        # hash password
        password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        # create
        user = User.create(
            username=data['username'],
            email=data['email'],
            password_hash=password_hash
        )
        return user
    
    @staticmethod
    def login_user(data):
        # validate data
        is_valid = UserService.validate_login(data)
        if not is_valid:
            flash('Invalid email or password.', 'err_login_invalid')
        
        # is_valid is actually the user object here
        return is_valid
        

    @staticmethod
    def validate_login(data):
        is_valid = True
        if not data.get('username'):
            if not data.get('email'):
                is_valid = False
        # if data.get('email'):
        #     if not re.match(EMAIL_REGEX, data['email']):
        #         is_valid = False
        if not data.get('password'):
            is_valid = False

        if is_valid:
            from src.models.user import User
            user = User.query.filter_by(username=data['username']).first()
            if not user:
                # check the username
                # user = User.query.filter_by(email=data['email']).first()
                # if not user:
                is_valid = False

            if user and not bcrypt.check_password_hash(user.password_hash, data['password']):
                is_valid = False
            
            return user

        return is_valid    
    

    @staticmethod
    def validate_registration(data):
        is_valid = True

        # check to see all fields are filled in
        if not data.get('username'):
            is_valid = False
            flash('Username is required.', 'err_registration_username')
        if not data.get('email'):
            is_valid = False
            flash('Email is required.', 'err_registration_email')
        elif not re.match(EMAIL_REGEX, data['email']):
            is_valid = False
            flash('Invalid email format.', 'err_registration_email_format')
        if not data.get('password'):
            is_valid = False
            flash('Password is required.', 'err_registration_password')
        if not data.get('confirm_password'):
            is_valid = False
            flash('Confirm Password is required.', 'err_registration_confirm_password')

        if is_valid:
            # check to see if the user is in the database already.
            from src.models.user import User
            existing_user = User.query.filter(
                (User.username == data['username']) | (User.email == data['email'])
            ).first()
            if existing_user:
                is_valid = False
                flash('Username or Email already exists.', 'err_registration_exists')
            
        return is_valid


    @staticmethod
    def get_current_user(hash_key):
        from src.models.logbook import Logbook
        log_entry = Logbook.get_by_hash(hash_key)
        if not log_entry:
            return None
        from src.models.user import User
        # For simplicity, assume the log entry contains the user ID in reference_code
        user = User.query.filter_by(id=log_entry.user_id).first()
        return user