from django.core.management.base import BaseCommand
from game.models import Mission
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Initialize default missions'

    def handle(self, *args, **options):
        DEFAULT_MISSIONS = [
            ("Get someone to high-five you", "easy", 10),
            ("Make someone say 'I don't know'", "easy", 10),
            ("Get someone to compliment you", "easy", 10),
            ("Convince someone to do 5 jumping jacks", "medium", 20),
            ("Get someone to tell you a joke", "medium", 20),
            ("Make someone laugh out loud", "medium", 20),
            ("Get three people to agree with you", "hard", 30),
            ("Get someone to share their biggest fear", "hard", 30),
            ("Get someone to teach you something", "hard", 30),
        ]

        for text, difficulty, points in DEFAULT_MISSIONS:
            Mission.objects.get_or_create(
                text=text,
                defaults={'difficulty': difficulty, 'points': points}
            )

        # Create daily missions
        for i in range(7):
            mission_date = date.today() + timedelta(days=i)
            Mission.objects.get_or_create(
                text=f"Daily: Complete a secret handshake (Day {i+1})",
                date=mission_date,
                defaults={'difficulty': 'medium', 'points': 25, 'is_daily': True}
            )

        self.stdout.write(self.style.SUCCESS('Successfully initialized missions'))
