"""
Database initialization and setup utilities.
"""
from src import create_app, db
from src.logic.user_logic import UserLogic, RoleLogic
from src.logic.mix_logic import MixLogic


def init_database():
    """Initialize the database with tables and default data."""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all tables and recreate (for development)
        db.drop_all()
        db.create_all()
        
        print("Database tables created successfully!")
        
        # Initialize default roles
        print("Creating default roles...")
        RoleLogic.initialize_default_roles()
        print("Default roles created!")
        
        # Create a default admin teacher
        print("Creating default admin teacher...")
        try:
            admin_data = {
                'email': 'admin@makeamix.com',
                'password': 'Pass123!!',
                'first_name': 'Admin',
                'last_name': 'Teacher',
                'department': 'Music Technology',
                'specialization': 'Music Production',
                'employee_id': 'ADMIN001',
                'default_role': 'admin'
            }
            admin_user = UserLogic.create_user(admin_data, 'teacher')
            
            # Assign additional teacher role
            RoleLogic.assign_role_to_user(admin_user.id, 'teacher')
            
            print(f"Admin teacher created: {admin_user.email}")
            
        except ValueError as e:
            if "Email already registered" in str(e):
                print("Admin teacher already exists")
            else:
                print(f"Error creating admin teacher: {e}")
        
        # Create a sample teacher
        print("Creating sample teacher...")
        try:
            teacher_data = {
                'email': 'teacher@makeamix.com',
                'password': 'Pass123!!',
                'first_name': 'John',
                'last_name': 'Music',
                'department': 'Music',
                'specialization': 'DJ/Mixing',
                'employee_id': 'T001',
                'default_role': 'teacher'
            }
            teacher_user = UserLogic.create_user(teacher_data, 'teacher')
            print(f"Sample teacher created: {teacher_user.email}")
            
        except ValueError as e:
            if "Email already registered" in str(e):
                print("Sample teacher already exists")
            else:
                print(f"Error creating sample teacher: {e}")
        
        # Create sample mixes for the teacher
        print("Creating sample mixes...")
        try:
            # Get the sample teacher
            from src.models.user_model import User
            teacher = User.query.filter_by(email='teacher@makeamix.com').first()
            
            if teacher:
                # Create sample mixes
                mix1_data = {
                    'title': 'Summer Vibes 2025',
                    'description': 'Perfect songs for summer relaxation and good vibes',
                    'genre': 'pop',
                    'visibility': 'public'
                }
                mix1 = MixLogic.create_mix(mix1_data, teacher.id)
                
                mix2_data = {
                    'title': 'Study Session Focus',
                    'description': 'Instrumental music to help students concentrate',
                    'genre': 'classical',
                    'visibility': 'class'
                }
                mix2 = MixLogic.create_mix(mix2_data, teacher.id)
                
                mix3_data = {
                    'title': 'Workout Energy Mix',
                    'description': 'High-energy tracks for fitness and motivation',
                    'genre': 'electronic',
                    'visibility': 'private'
                }
                mix3 = MixLogic.create_mix(mix3_data, teacher.id)
                
                print(f"Sample mixes created: {mix1.title}, {mix2.title}, {mix3.title}")
            
        except Exception as e:
            print(f"Error creating sample mixes: {e}")
        
        print("\nDatabase initialization complete!")
        print("\nDefault accounts created:")
        print("Admin Teacher: admin@makeamix.com / Pass123!!")
        print("Sample Teacher: teacher@makeamix.com / Pass123!!")
        print("\nSample mixes created for demonstration")
        print("Note: Students will be created by teachers from their dashboard.")
        print("Note: Songs will be uploaded through the web interface.")


def create_sample_student():
    """Create a sample student for testing (normally done by teachers)."""
    app = create_app()
    
    with app.app_context():
        try:
            student_data = {
                'email': 'student@makeamix.com',
                'password': 'Pass123!!',
                'first_name': 'Jane',
                'last_name': 'Learner',
                'student_id': 'S001',
                'grade_level': '11th',
                'default_role': 'student'
            }
            
            student = UserLogic.create_user(student_data, 'student')
            print(f"Sample student created: {student.email}")
            return student
            
        except Exception as e:
            print(f"Error creating sample student: {e}")
            return None


if __name__ == '__main__':
    init_database()
    
    # Optionally create a sample student for testing
    # create_sample_student()
