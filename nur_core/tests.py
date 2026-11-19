from django.core import mail
from django.test import SimpleTestCase, override_settings


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CONTACT_EMAILS=['dmuhemedi5@gmail.com', 'contact@nursarl.com'],
    DEFAULT_FROM_EMAIL='NUR <contact@nursarl.com>',
)
class ContactEmailTests(SimpleTestCase):
    def test_valid_contact_submission_emails_both_recipients(self):
        response = self.client.post(
            '/contact/',
            {
                'name': 'Ada Lovelace',
                'email': 'ada@example.com',
                'organization': 'Analytical Engines',
                'phone': '+123456789',
                'service': 'software',
                'message': 'Je souhaite discuter de mon projet.',
            },
        )

        self.assertRedirects(response, '/contact/envoye/')
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(
            message.to,
            ['dmuhemedi5@gmail.com', 'contact@nursarl.com'],
        )
        self.assertEqual(message.reply_to, ['ada@example.com'])
        self.assertIn('Ada Lovelace', message.body)
