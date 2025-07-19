from django.core.management.base import BaseCommand
from mainapp.models import Review


class Command(BaseCommand):
    help = 'Додає зразки відгуків клієнтів'

    def handle(self, *args, **options):
        sample_reviews = [
            {
                'client_name': 'Олександр Петренко',
                'client_position': 'Власник приватного будинку',
                'review_text': 'Дуже задоволений співпрацею з GreenSolarTech! Встановили сонячну електростанцію потужністю 10 кВт за 3 тижні. Команда професійна, все зроблено якісно. Економія на електроенергії вже відчутна. Рекомендую!',
                'rating': 5,
                'project_type': 'Приватний будинок',
                'location': 'Київська область'
            },
            {
                'client_name': 'Марина Коваленко',
                'client_position': 'Директор ТОВ "Агро-Успіх"',
                'review_text': 'Встановили промислову СЕС на 50 кВт для нашого агропідприємства. Проект реалізовано в строк, документообіг оформлено швидко. Тепер маємо стабільне джерело електроенергії і значну економію коштів.',
                'rating': 5,
                'project_type': 'Промислова СЕС',
                'location': 'Полтавська область'
            },
            {
                'client_name': 'Віктор Сидоренко',
                'client_position': 'Інженер-енергетик',
                'review_text': 'Професійний підхід до справи! Детальна консультація, якісне обладнання, швидкий монтаж. Станція працює без збоїв вже понад рік. Команда GreenSolarTech знає свою справу.',
                'rating': 5,
                'project_type': 'Мережева СЕС',
                'location': 'Дніпропетровська область'
            },
            {
                'client_name': 'Анна Мельник',
                'client_position': 'Власниця кафе',
                'review_text': 'Встановили сонячні панелі для нашого кафе. Дуже приємно здивувала швидкість роботи та увага до деталей. Все пояснили зрозуміло, допомогли з оформленням зеленого тарифу.',
                'rating': 4,
                'project_type': 'Комерційна СЕС',
                'location': 'Львівська область'
            },
            {
                'client_name': 'Дмитро Гриценко',
                'client_position': 'Директор фермерського господарства',
                'review_text': 'Реалізували потужну СЕС на 100 кВт. Проект окупився швидше, ніж очікували. Особливо вдячний за якісне післяпродажне обслуговування та моніторинг системи.',
                'rating': 5,
                'project_type': 'Промислова СЕС',
                'location': 'Херсонська область'
            },
            {
                'client_name': 'Світлана Іваненко',
                'client_position': 'Домогосподарка',
                'review_text': 'Чудова команда! Встановили 15 кВт систему з акумуляторами. Тепер ми повністю енергонезалежні. Особливо важливо в умовах нестабільного електропостачання.',
                'rating': 5,
                'project_type': 'Гібридна СЕС',
                'location': 'Вінницька область'
            },
            {
                'client_name': 'Ігор Білоус',
                'client_position': 'Керівник будівельної компанії',
                'review_text': 'Співпрацюємо з GreenSolarTech вже другий рік. Встановили СЕС на офісі та виробничих потужностях. Якість обладнання європейська, сервіс на високому рівні.',
                'rating': 5,
                'project_type': 'Комерційна СЕС',
                'location': 'Одеська область'
            },
            {
                'client_name': 'Наталія Шевченко',
                'client_position': 'Власниця готелю',
                'review_text': 'Встановили СЕС для нашого готелю в Карпатах. Тепер маємо екологічну енергію і значно знизили витрати на електрику. Гості теж цінують наш підхід до збереження довкілля.',
                'rating': 4,
                'project_type': 'Комерційна СЕС',
                'location': 'Івано-Франківська область'
            }
        ]

        created_count = 0
        for review_data in sample_reviews:
            review, created = Review.objects.get_or_create(
                client_name=review_data['client_name'],
                defaults=review_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Створено відгук від {review.client_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Відгук від {review.client_name} вже існує')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Успішно створено {created_count} нових відгуків')
        ) 