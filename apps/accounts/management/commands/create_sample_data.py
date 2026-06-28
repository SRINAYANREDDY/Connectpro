from django.core.management.base import BaseCommand
from apps.accounts.models import User, Follow, Skill, Education
from apps.posts.models import Post


class Command(BaseCommand):
    help = 'Creates sample data for development'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample users...')

        users_data = [
            {'email': 'alice@example.com', 'username': 'alice', 'full_name': 'Alice Johnson',
             'headline': 'Senior Software Engineer @ TechCorp', 'bio': 'Building the future, one commit at a time.'},
            {'email': 'bob@example.com', 'username': 'bob', 'full_name': 'Bob Smith',
             'headline': 'Product Designer | UX Enthusiast', 'bio': 'Designing experiences that matter.'},
            {'email': 'carol@example.com', 'username': 'carol', 'full_name': 'Carol White',
             'headline': 'Data Scientist | ML Engineer', 'bio': 'Turning data into insights.'},
        ]

        users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={**data, 'is_active': True}
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  Created user: {user.username}')
            users.append(user)

        # Add skills
        skills_map = {
            'alice': ['Python', 'Django', 'PostgreSQL', 'Docker', 'AWS'],
            'bob': ['Figma', 'CSS', 'UI/UX', 'Prototyping', 'React'],
            'carol': ['Python', 'TensorFlow', 'SQL', 'Pandas', 'Jupyter'],
        }
        for user in users:
            for skill_name in skills_map.get(user.username, []):
                Skill.objects.get_or_create(user=user, name=skill_name)

        # Add posts
        posts_data = [
            (users[0], 'Excited to share that I just shipped a new feature using #Django and #Python! The team worked incredibly hard on this. #webdev #backend'),
            (users[1], 'Just finished redesigning our onboarding flow. Users are 40% more likely to complete setup now! #UX #design #product'),
            (users[2], 'Trained a new ML model today that achieves 94% accuracy on our dataset. #machinelearning #python #datascience'),
            (users[0], 'Hot take: code reviews are the best way to learn. Fight me. #programming #softwareengineering'),
            (users[1], 'Reminder: white space is not wasted space. Breathe, design! #design #minimalism'),
        ]
        for author, content in posts_data:
            Post.objects.get_or_create(author=author, content=content)

        # Make them follow each other
        for i, user in enumerate(users):
            for j, other in enumerate(users):
                if i != j:
                    Follow.objects.get_or_create(follower=user, following=other, defaults={'status': 'accepted'})

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('Login with any of:')
        self.stdout.write('  alice@example.com / password123')
        self.stdout.write('  bob@example.com / password123')
        self.stdout.write('  carol@example.com / password123')
