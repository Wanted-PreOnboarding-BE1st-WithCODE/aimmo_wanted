import json

from django.http      import JsonResponse
from json.decoder     import JSONDecodeError
from django.views     import View
from django.db.models import Q

from postings.models  import Category, Posting, Comment
from users.models     import User
from users.utils      import login_decorator

class PostingView(View):
    @login_decorator
    def post(self, request):
        try:
            data        = json.loads(request.body)
            user        = request.user
            category_id = data['category_id']

            if not Category.objects.filter(id = category_id).exists():
                return JsonResponse({"message" : "CATEGORY_DOES_NOT_EXIST"}, status = 404)

            Posting.objects.create(
                category_id = category_id,
                user        = user,
                title       = data['title'],
                content     = data['content']
            )

            return JsonResponse({'message' : 'SUCCESS'}, status = 201)

        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        
    def get(self, request):
        keyword     = request.GET.get('keyword')
        category_id = request.GET.get('category_id')

        posting_filter = Q()

        if keyword:
            posting_filter.add(Q(title__icontains = keyword) | Q(content__icontains = keyword), Q.AND)
        
        if category_id:
            if not Category.objects.filter(id = category_id).exists():
                return JsonResponse({"message" : "CATEGORY_DOES_NOT_EXIST"}, status = 404)
            
            posting_filter.add(Q(category_id = category_id))
        
        postings = Posting.objects.select_related('user').filter(posting_filter)

        posting_list = [{
            'id'          : posting.id,
            'title'       : posting.title,
            'content'     : posting.content,
            'views'       : posting.views,
            'created_at'  : posting.created_at.strftime("%Y/%m/%d"),
            'author_id'   : posting.user.id,
            'author'      : posting.user.name,     
        }for posting in postings]

        return JsonResponse({'posting_list' : posting_list}, status = 200)
    
class PostingParamView(View) :
    def get(self, request, posting_id):
        try:
            if not Posting.objects.filter(id = posting_id).exists():
                return JsonResponse({'message' : 'POSTING_DOES_NOT_EXIST'}, status = 404)

            user_id = request.session.get('user')
            posting = Posting.objects.select_related('user').prefetch_related('comment_set').get(id = posting_id)

            posting_info = {
                'id'            : posting.id,
                'title'         : posting.title,
                'views'         : posting.views,
                'content'       : posting.content,
                'author_id'     : posting.user.id,
                'author'        : posting.user.name,
                'comment_count' : posting.comment_set.count()
            }
            
            if not user_id :
                posting.views += 1
                posting.save()
            
            return JsonResponse({'posting_info' : posting_info}, status = 200)
        
        except Posting.DoesNotExist:
            return JsonResponse({'message' : 'POSTING_DOES_NOT_EXIST'}, status = 404)
        
        except Posting.MultipleObjectsReturned:
            return JsonResponse({'message' : 'MULTIPLE_RETURN_ERROR'}, status = 400)

    @login_decorator
    def post(self, request, posting_id) :
        try :
            if not Posting.objects.filter(id = posting_id).exists():
                return JsonResponse({'message' : 'POSTING_DOES_NOT_EXIST'}, status = 404)
            
            data    = json.loads(request.body)
            user    = request.user
            posting = Posting.objects.get(id = posting_id)

            if user != posting.user:
                return JsonResponse({'message' : 'INVALID_USER'}, status = 401)

            posting.title   = data.get('title', posting.title)
            posting.content = data.get('content', posting.content)
            posting.save()

            return JsonResponse({'message' : 'SUCCESS'}, status=201)
        
        except Posting.DoesNotExist :
            return JsonResponse({'message' : 'POSTING_DOES_NOT_EXIST'}, status=404)
        
        except Posting.MultipleObjectsReturned:
            return JsonResponse({'message' : 'MULTIPLE_RETURN_ERROR'}, status = 400)

    @login_decorator
    def delete(self, request, posting_id) :
        try :
            user    = request.user
            posting = Posting.objects.get(id = posting_id)

            if user != posting.user:
                return JsonResponse({'message' : 'INVALID_USER'}, status = 401)

            posting.delete()
            
            return JsonResponse({'message' : 'SUCCESS'}, status = 200)
        
        except Posting.DoesNotExist :
            return JsonResponse({'message' : 'POSTING_DOES_NOT_EXIST'}, status = 404)

class CommentView(View):
    @login_decorator
    def post(self, request, posting_id):
        try:
            if not Posting.objects.filter(id = posting_id).exists():
                return JsonResponse({'message' : 'POSTING_DOES_NOT_EXIST'}, status = 404)

            data              = json.loads(request.body)
            user              = request.user
            content           = data['content']
            parent_comment_id = data.get('parent_comment_id')

            if parent_comment_id:
                if not Comment.objects.filter(id = parent_comment_id).exists():
                    return JsonResponse({'message' : 'COMMENT_DOES_NOT_EXIST'}, status = 404)

            Comment.objects.create(
                user              = user,
                posting_id        = posting_id,
                content           = content,
                parent_comment_id = parent_comment_id
                )
            
            return JsonResponse({'message' : 'SUCCESS'}, status = 201)
        
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        
        except JSONDecodeError:
            return JsonResponse({'message' : 'JSON_DECODE_ERROR'}, status = 400)
    
    def get(self, request, posting_id):
        if not Posting.objects.filter(id = posting_id).exists():
            return JsonResponse({'message' : 'POSTING_DOES_NOT_EXIST'}, status = 404)
        
        page      = int(request.GET.get('page', 1))
        page_size = 5
        limit     = int(page_size * page)
        offset    = int(limit - page_size)

        comments     = Comment.objects.select_related('user').filter(posting_id = posting_id, parent_comment_id = None).prefetch_related('child_comments')[offset : limit]
        comment_list = [{
            'comment_id'          : comment.id,
            'comment_author'      : comment.user.name,
            'comment_content'     : comment.content,
            'comment_created_at'  : comment.created_at.strftime("%Y/%m/%d"),
            'child_comment_count' : comment.child_comments.count()
        }for comment in comments]
        
        return JsonResponse({'comment_list' : comment_list}, status = 200)

class CommentDetailView(View):
    def get(self, request, comment_id):
        try:
            if not Comment.objects.filter(id = comment_id).exists():
                return JsonResponse({'message' : 'COMMENT_DOES_NOT_EXIST'}, status = 404)
            
            page      = int(request.GET.get('page', 1))
            page_size = 5
            limit     = int(page_size * page)
            offset    = int(limit - page_size)

            comment            = Comment.objects.prefetch_related('child_comments__user').get(id = comment_id)
            child_comment_list = [{
                'child_comment_id'         : child_comment.id,
                'child_comment_author'     : child_comment.user.name,
                'child_comment_content'    : child_comment.content,
                'child_comment_created_at' : child_comment.created_at.strftime("%Y/%m/%d"),
            }for child_comment in comment.child_comments.all()[offset : limit]]

            return JsonResponse({'child_comment_list' : child_comment_list}, status = 200)
        
        except Comment.DoesNotExist:
            return JsonResponse({'message' : 'COMMENT_DOES_NOT_EXIST'}, status = 404)
        
        except Comment.MultipleObjectsReturned:
            return JsonResponse({'message' : "MULTIPLE_RETURN_ERROR"}, status = 400)
            
    @login_decorator
    def delete(self, request, comment_id):
        try:
            user = request.user
            if not Comment.objects.filter(id = comment_id).exists():
                return JsonResponse({'message' : 'COMMENT_DOES_NOT_EXIST'}, status = 404)
            
            comment = Comment.objects.get(id = comment_id)

            if user != comment.user:
                return JsonResponse({'message' : 'INVALID_USER'}, status = 401)

            comment.delete()
            return JsonResponse({'message' : 'SUCCESS'}, status = 200)
        
        except Comment.DoesNotExist:
            return JsonResponse({'message' : 'COMMENT_DOES_NOT_EXIST'}, status = 404)
        
        except Comment.MultipleObjectsReturned:
            return JsonResponse({'message' : 'MULTIPLE_RETURN_ERROR'}, status = 400)

    @login_decorator
    def patch(self, request, comment_id):
        try:
            user = request.user
            data = json.loads(request.body)

            if not Comment.objects.filter(id = comment_id).exists():
                return JsonResponse({'message' : 'COMMENT_DOES_NOT_EXIST'}, status = 404)
            
            comment = Comment.objects.get(id = comment_id)

            if user != comment.user:
                return JsonResponse({'message' : 'INVALID_USER'}, status = 401)

            comment.content = data.get('content', comment.content)
            comment.save()

            return JsonResponse({'message' : 'SUCCESS'}, status = 201)
        
        except Comment.DoesNotExist:
            return JsonResponse({'message' : 'COMMENT_DOES_NOT_EXIST'}, status = 404)
        
        except Comment.MultipleObjectsReturned:
            return JsonResponse({'message' : 'MULTIPLE_RETURN_ERROR'}, status = 400)