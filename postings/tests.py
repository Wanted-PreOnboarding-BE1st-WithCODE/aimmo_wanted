import json

from django.test import TestCase, Client

from postings.models import Category, Posting
from users.models    import User

class PostingViewTest(TestCase) :
    def setUp(self) :
        User.objects.bulk_create(
            [
                User(id=1, name='kylee', email='kylee@gmail.com', password='kylee11!'),
                User(id=2, name='wanted', email='wanted@gmail.com', password='wanted11!'),
                User(id=3, name='wecode', email='wecode@gmail.com', password='wecode11!')
            ]
        )

        Category.objects.create(id=1, name='테스트 카테고리1')

        Posting(id=1, title='테스트 타이틀', content='테스트 내용', category_id=Category.objects.get(id=1).id, user_id=User.objects.get(id=1).id).save()
    
    def tearDown(self) :
        User.objects.all().delete()
        Category.objects.all().delete()
        Posting.objects.all().delete()
    
    def test_success_posting_view_register_posting(self) :
        client = Client()

        headers = {'HTTP_Authorization' : 'token'}

        posting_info = {
            'id'       : 4,
            'title'    : 'test title',
            'content'  : 'test content',
            'user'     : User.objects.get(id=1).id,
            'category' : Category.objects.get(id=1).id
        }

        response = client.post('/postings', json.dumps(posting_info), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message' : 'Posting Success'
        })
    
    def test_falure_caused_by_key_error_posting_view_register_posting(self) :
        client = Client()

        headers = {'HTTP_Authorization' : 'token'}

        posting_info = {
            'id'       : 4,
            'title'    : 'test title',
            'contents' : 'test content',
            'usersss'  : User.objects.get(id=1).id,
            'category' : Category.objects.get(id=1).id
        }

        response = client.post('/postings', json.dumps(posting_info), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'message' : 'Key Error'
        })

    def test_failure_caused_by_model_does_not_exists_error_posting_view_register_posting(self) :
        client = Client()

        headers = {'HTTP_Authorization' : 'token'}

        posting_info = {
            'id'       : 4,
            'title'    : 'test title',
            'content'  : 'test content',
            'user'     : User.objects.get(id=1).id,
            'category' : 2
        }

        response = client.post('/postings', json.dumps(posting_info), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'message' : 'Category matching query does not exist'
        })
    
    def test_success_get_posting_list_using_keyword(self) :
        client = Client()

        response = client.get('/postings?keyword=t')

        self.assertEqual(response.status_code, 200)

    def test_failure_caused_key_error_get_posting_list(self) :
        client = Client()

        response = client.get('/postings?keyworld=t')

        self.assertEqual(response.status_code, 400)

class PostingParamViewTest(TestCase) :
    def setUp(self) :
        User.objects.bulk_create(
            [
                User(id=1, name='kylee', email='kylee@gmail.com', password='kylee11!'),
                User(id=2, name='wanted', email='wanted@gmail.com', password='wanted11!'),
                User(id=3, name='wecode', email='wecode@gmail.com', password='wecode11!')
            ]
        )

        Category.objects.create(id=1, name='테스트 카테고리1')

        Posting(id=1, title='테스트 타이틀', content='테스트 내용', category_id=Category.objects.get(id=1).id, user_id=User.objects.get(id=1).id).save()
        
    def tearDown(self) :
        User.objects.all().delete()
        Category.objects.all().delete()
        Posting.objects.all().delete()

    def test_success_modify_posting_posting_view(self) :
        client = Client()

        headers = {'HTTP_Authorization' : 'token'}

        posting_info = {
            'title' : 'new update title'
        }

        response = client.post('/postings/1', json.dumps(posting_info), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),{
            'message' : 'Update Success'
        })

    def test_failure_caused_posting_does_not_exist_modify_posting(self) :
        client = Client()

        headers = {'HTTP_Authorization' : 'token'}

        posting_info = {
            'title' : 'update title new'
        }

        response = client.post('/postings/10', json.dumps(posting_info), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'message' : 'Posting matching query does not exist'
        })        
    
    def test_success_delete_posting_param_view(self) :
        client = Client()

        headers = {'HTTP_Authorization' : 'token'}        

        response = client.delete('/postings/1', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),{
            'message' : 'Delete Success'
        })
    
    def test_failure_caused_posting_does_not_exists_delete_posting(self) :
        client = Client()

        headers = {'HTTP_Authorization' : 'token'} 

        response = client.delete('/postings/10')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'message' : 'Posting matching query does not exist'
        })      