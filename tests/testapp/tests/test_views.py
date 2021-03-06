from unittest.mock import call, patch

from django.test import RequestFactory, TestCase

from testapp import views

factory = RequestFactory()


class PromptDownloadTestCase(TestCase):
    def test_prompt_download(self):
        request = factory.get('/some_view')

        response = views.PromptDownloadView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Content-Type: application/pdf',
            response.serialize_headers().splitlines()
        )
        self.assertIn(
            b'Content-Disposition: attachment; filename="myfile.pdf"',
            response.serialize_headers().splitlines(),
        )
        # Assert that response looks like a PDF
        self.assertTrue(response.content.startswith(b'%PDF-1.'))

    def test_dont_prompt_download(self):
        request = factory.get('/some_view')

        response = views.NoPromptDownloadView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Content-Type: application/pdf',
            response.serialize_headers().splitlines()
        )
        self.assertNotIn(b'Content-Disposition:', response.serialize_headers())
        # Assert that response looks like a PDF
        self.assertTrue(response.content.startswith(b'%PDF-1.'))


class ForceHTMLTestCase(TestCase):
    def test_force_html_allowed(self):
        request = factory.get('/some_view?html=true')

        response = views.AllowForceHtmlView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'Hi!\n', response.content)
        self.assertIn(
            b'Content-Type: text/html; charset=utf-8',
            response.serialize_headers().splitlines()
        )

    def test_no_force_html_allowed(self):
        request = factory.get('/some_view')

        response = views.AllowForceHtmlView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Content-Type: application/pdf',
            response.serialize_headers().splitlines()
        )
        # Assert that response looks like a PDF
        self.assertTrue(response.content.startswith(b'%PDF-1.'))

    def test_force_html_disallowed(self):
        request = factory.get('/some_view?html=true')

        response = views.DisallowForceHtmlView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Content-Type: application/pdf',
            response.serialize_headers().splitlines()
        )
        # Assert that response looks like a PDF
        self.assertTrue(response.content.startswith(b'%PDF-1.'))

    def test_no_force_html_disallowed(self):
        request = factory.get('/some_view')

        response = views.DisallowForceHtmlView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Content-Type: application/pdf',
            response.serialize_headers().splitlines()
        )
        # Assert that response looks like a PDF
        self.assertTrue(response.content.startswith(b'%PDF-1.'))


class CustomUrlFetcherTestCase(TestCase):
    pass  # TODO


class StaticFileResolutionTestCase(TestCase):
    def test_url_fetcher_used(self):
        request = factory.get('/some_view')

        with patch(
            'django_renderpdf.helpers.staticfiles_url_fetcher',
            return_value={
                'string': 'html { margin: 0; }',
                'mime_type': 'text/css',
            },
            spec=True,
        ) as fetcher:
            response = views.TemplateWithStaticFileView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(fetcher.call_count, 1)
        self.assertEqual(
            fetcher.call_args,
            call('/static/path/not/relevant.css'),
        )
