"""
Example usage of the new user models without Flask-User dependencies.
This demonstrates the clean, simple user authentication system.
"""
from src import create_app
from src.logic.user_logic import UserLogic, RoleLogic


def example_user_operations():
    """Demonstrate basic user operations."""
    app = create_app()
    
    with app.app_context():
        print("=== Clean User Model Demo (No Flask-User) ===\n")
        
        # 1. List existing users
        print("1. Current users in database:")
        teachers = UserLogic.get_all_teachers()
        students = UserLogic.get_all_students()
        
        print(f"Teachers: {len(teachers)}")
        for teacher in teachers:
            print(f"  - {teacher.full_name} ({teacher.email}) - {teacher.department}")
        
        print(f"Students: {len(students)}")
        for student in students:
            print(f"  - {student.full_name} ({student.email}) - Grade {student.grade_level}")
        
        # 2. Test authentication
        print("\n2. Testing authentication:")
        
        # Valid login
        user = UserLogic.authenticate_user('admin@makeamix.com', 'Pass123!!')
        if user:
            print(f"✓ Admin login successful: {user.full_name}")
            print(f"  User type: {user.user_type}")
            print(f"  Roles: {user.get_role_names()}")
            print(f"  Last login: {user.last_login}")
        else:
            print("✗ Admin login failed")
        
        # Invalid login
        user = UserLogic.authenticate_user('admin@makeamix.com', 'wrongpassword')
        if user:
            print(f"✓ Wrong password test failed (unexpected)")
        else:
            print("✓ Wrong password correctly rejected")
        
        # 3. Create a new teacher
        print("\n3. Creating a new teacher:")
        try:
            new_teacher_data = {
                'email': 'newteacher@makeamix.com',
                'password': 'Pass123!!',
                'first_name': 'Maria',
                'last_name': 'Rodriguez',
                'department': 'Music Technology',
                'specialization': 'Beat Making',
                'employee_id': 'T002',
                'default_role': 'teacher'
            }
            
            new_teacher = UserLogic.create_user(new_teacher_data, 'teacher')
            print(f"✓ New teacher created: {new_teacher.full_name}")
            print(f"  Email: {new_teacher.email}")
            print(f"  Employee ID: {new_teacher.employee_id}")
            print(f"  Specialization: {new_teacher.specialization}")
            
        except ValueError as e:
            print(f"✗ Teacher creation failed: {e}")
        
        # 4. Create a student (normally done by teachers)
        print("\n4. Creating a student (simulating teacher action):")
        try:
            student_data = {
                'email': 'newstudent@makeamix.com',
                'password': 'Pass123!!',
                'first_name': 'David',
                'last_name': 'Chen',
                'student_id': 'S002',
                'grade_level': '12th',
                'default_role': 'student'
            }
            
            new_student = UserLogic.create_user(student_data, 'student')
            print(f"✓ New student created: {new_student.full_name}")
            print(f"  Email: {new_student.email}")
            print(f"  Student ID: {new_student.student_id}")
            print(f"  Grade: {new_student.grade_level}")
            
        except ValueError as e:
            print(f"✗ Student creation failed: {e}")
        
        # 5. Test role management
        print("\n5. Testing role management:")
        
        # Get all roles
        roles = RoleLogic.get_all_roles()
        print(f"Available roles: {[role.name for role in roles]}")
        
        # Test role assignment
        teacher = UserLogic.get_user_by_email('teacher@makeamix.com')
        if teacher:
            print(f"Teacher roles before: {teacher.get_role_names()}")
            
            # Add admin role to teacher
            try:
                RoleLogic.assign_role_to_user(teacher.id, 'admin')
                teacher = UserLogic.get_user_by_id(teacher.id)  # Refresh
                print(f"Teacher roles after adding admin: {teacher.get_role_names()}")
            except ValueError as e:
                print(f"Role assignment note: {e}")
        
        # 6. Test user dictionary conversion
        print("\n6. User data serialization:")
        admin = UserLogic.get_user_by_email('admin@makeamix.com')
        if admin:
            user_dict = admin.to_dict()
            print("Admin user as dictionary:")
            for key, value in user_dict.items():
                print(f"  {key}: {value}")
        
        print("\n=== Demo Complete ===")
        print("\nKey Features Demonstrated:")
        print("✓ Clean models without Flask-User dependencies")
        print("✓ Simple SHA-256 password hashing")
        print("✓ Role-based access control")
        print("✓ Polymorphic inheritance (Teacher/Student)")
        print("✓ Business logic separation")
        print("✓ Session-based authentication")
        print("✓ Comprehensive error handling")


def test_password_functionality():
    """Test password hashing and verification."""
    app = create_app()
    
    with app.app_context():
        print("\n=== Password Security Test ===")
        
        user = UserLogic.get_user_by_email('admin@makeamix.com')
        if user:
            print(f"Testing password functionality for: {user.email}")
            
            # Test correct password
            if user.check_password('admin123'):
                print("✓ Correct password verification works")
            else:
                print("✗ Correct password verification failed")
            
            # Test wrong password
            if user.check_password('wrongpassword'):
                print("✗ Wrong password verification failed (security issue)")
            else:
                print("✓ Wrong password correctly rejected")
            
            # Test password change
            old_hash = user.password_hash
            user.set_password('newpassword123')
            new_hash = user.password_hash
            
            if old_hash != new_hash:
                print("✓ Password hash changed successfully")
            else:
                print("✗ Password hash did not change")
            
            if user.check_password('newpassword123'):
                print("✓ New password works")
            else:
                print("✗ New password verification failed")
            
            # Reset to original password
            user.set_password('admin123')
            print("✓ Password reset to original")


if __name__ == '__main__':
    example_user_operations()
    test_password_functionality()