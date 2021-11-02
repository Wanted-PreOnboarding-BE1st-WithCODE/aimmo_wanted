import json, jwt

from django.test     import TestCase, Client

from postings.models import Category, Posting, Comment
from users.models    import User
from django.conf     import settings

class PostingViewTest(TestCase) :
    def setUp(self):
        global headers, posting
        access_token = jwt.encode({'id' : 1}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}
        User.objects.bulk_create(
            [
                User(id=1, name='kylee', email='kylee@gmail.com', password='kylee11!'),
                User(id=2, name='wanted', email='wanted@gmail.com', password='wanted11!'),
                User(id=3, name='wecode', email='wecode@gmail.com', password='wecode11!')
            ]
        )

        Category.objects.create(id=1, name='테스트 카테고리1')

        posting = Posting.objects.create(id=1, title='테스트 타이틀', content='테스트 내용', category_id= 1, user_id= 1)
         
    def tearDown(self) :
        User.objects.all().delete()
        Category.objects.all().delete()
        Posting.objects.all().delete()
    
    def test_success_posting_view_register_posting(self) :
        client = Client()

        posting_info = {
            'title'       : 'test title',
            'content'     : 'test content',
            'category_id' : 1
        }

        response = client.post('/postings', json.dumps(posting_info), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message' : 'SUCCESS'
        })
    
    def test_falure_caused_by_key_error_posting_view_register_posting(self) :
        client = Client()

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
            'message' : 'KEY_ERROR'
        })

    def test_failure_caused_by_model_does_not_exists_error_posting_view_register_posting(self) :
        client = Client()

        posting_info = {
            'title'       : 'test title',
            'content'     : 'test content',
            'category_id' : 2
        }

        response = client.post('/postings', json.dumps(posting_info), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),{
            'message' : 'CATEGORY_DOES_NOT_EXIST'
        })
    
    def test_success_get_posting_list_success(self) :
        client = Client()

        posting_list = [{
            'id'          : 1,
            'title'       : posting.title,
            'content'     : posting.content,
            'views'       : posting.views,
            'created_at'  : posting.created_at.strftime("%Y/%m/%d"),
            'author_id'   : posting.user.id,
            'author'      : posting.user.name,     
        }]

        response = client.get('/postings')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'posting_list' : posting_list
        })

    def test_failure_caused_invalid_category_id_posting_list(self) :
        client = Client()

        response = client.get('/postings?category_id=3')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'message' : 'CATEGORY_DOES_NOT_EXIST'
        })

class PostingParamViewTest(TestCase) :
    def setUp(self) :
        global headers, posting
        access_token = jwt.encode({'id' : 1}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}
        User.objects.bulk_create(
            [
                User(id=1, name='kylee', email='kylee@gmail.com', password='kylee11!'),
                User(id=2, name='wanted', email='wanted@gmail.com', password='wanted11!'),
                User(id=3, name='wecode', email='wecode@gmail.com', password='wecode11!')
            ]
        )

        Category.objects.create(id=1, name='테스트 카테고리1')
        posting = Posting.objects.create(id = 1, title='테스트 타이틀', content='테스트 내용', category_id= 1, user_id= 1)
        
    def tearDown(self) :
        User.objects.all().delete()
        Category.objects.all().delete()
        Posting.objects.all().delete()

    def test_success_modify_posting_posting_view(self) :
        client = Client()

        posting_info = {
            'title' : 'new update title'
        }

        response = client.post('/postings/1', json.dumps(posting_info), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),{
            'message' : 'SUCCESS'
        })

    def test_failure_caused_posting_does_not_exist_modify_posting(self) :
        client = Client()

        posting_info = {
            'title' : 'update title new'
        }

        response = client.post('/postings/10', json.dumps(posting_info), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),{
            'message' : 'POSTING_DOES_NOT_EXIST'
        })        
    
    def test_success_delete_posting_param_view(self) :
        client = Client()      

        response = client.delete('/postings/1', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{
            'message' : 'SUCCESS'
        })
    
    def test_failure_caused_posting_does_not_exists_delete_posting(self) :
        client = Client()

        response = client.delete('/postings/10', **headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),{
            'message' : 'POSTING_DOES_NOT_EXIST'
        })      
    
    def test_success_get_posting_param_view(self) :
        client = Client()

        posting_info = {
            'id'            : 1,
            'title'         : posting.title,
            'views'         : posting.views,
            'content'       : posting.content,
            'author_id'     : posting.user.id,
            'author'        : posting.user.name,
            'comment_count' : posting.comment_set.count()
        }

        response = client.get('/postings/1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{
            'posting_info' : posting_info
        })      

class CommentTest(TestCase):
    def setUp(self):
        global headers
        access_token = jwt.encode({'id' : 1}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}
        user1        = User.objects.create(id = 1, email = "user1@gmail.com", password = "abc1234!", name = '박유저')
        user2        = User.objects.create(id = 2, email = "user2@gmail.com", password = "abc1234!", name = '김유저')
        category     = Category.objects.create(id = 1, name = '카테고리')
        posting1     = Posting.objects.create(id = 1, user_id = 1, category = category, title = '제목', content = '내용')
        comment1     = Comment.objects.create(id = 1, user_id = 2, posting_id = 1, content = '내용')
        comment2     = Comment.objects.create(id = 2, user_id = 1, posting_id = 1, content = '내용', parent_comment_id = 1)

    def tearDown(self):
        User.objects.all().delete()
        Category.objects.all().delete()
        Posting.objects.all().delete()
        Comment.objects.all().delete()
    
    def test_commentview_post_success(self):
        client = Client()

        data = {
            "content" : "댓글 내용"
        }

        response = client.post('/postings/comments/1', json.dumps(data), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message' : 'SUCCESS'
        })
    
    def test_commentview_post_posting_does_not_exist(self):
        client = Client()

        data = {
            "content" : "댓글 내용"
        }

        response = client.post('/postings/comments/2', json.dumps(data), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'message' : 'POSTING_DOES_NOT_EXIST'
        })
    
    def test_commentview_post_comment_does_not_exist(self):
        client = Client()

        data = {
            "content"           : "댓글 내용",
            "parent_comment_id" :  3
        }

        response = client.post('/postings/comments/1', json.dumps(data), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'message' : 'COMMENT_DOES_NOT_EXIST'
        })
    
    def test_commentview_post_json_decode_error(self):
        client = Client()

        response = client.post('/postings/comments/1', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message' : 'JSON_DECODE_ERROR'
        })
    
    def test_commentview_get_success(self):
        client = Client()

        response = client.get('/postings/comments/1')

        comment_list = [{
            'comment_id'          : 1,
            'comment_author'      : '김유저',
            'comment_content'     : '내용',
            'comment_created_at'  : '2021/11/03',
            'child_comment_count' : 1,
        }]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'comment_list' : comment_list
        })

    def test_commentview_get_posting_does_not_exist(self):
        client = Client()

        response = client.get('/postings/comments/2')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'message' : 'POSTING_DOES_NOT_EXIST'
        })

    def test_commentdetailview_get_success(self):
        client = Client()

        response = client.get('/postings/comment/1')

        child_comment_list = [{
                'child_comment_id'         : 2,
                'child_comment_author'     : '박유저',
                'child_comment_content'    : '내용',
                'child_comment_created_at' : '2021/11/03',
        }]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'child_comment_list' : child_comment_list
        })

    def test_commentdetailview_delete_success(self):
        client = Client()

        response = client.delete('/postings/comment/2', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'message' : 'SUCCESS'
        })
    
    def test_commentdetailview_patch_success(self):
        client = Client()

        data = {
            "content" : "댓글 내용 수정"
        }

        response = client.patch('/postings/comment/2', json.dumps(data), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message' : 'SUCCESS'
        })