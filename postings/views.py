import json

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q

from postings.models  import (
    Category, 
    Posting
)
from users.models     import User

class PostingView(View) :
    #@login_decorator
    def post(self, request) :
        try :
            data = json.loads(request.body)

            user     = User.objects.get(id=1) #request.user
            category = Category.objects.get(id=data['category'])
            
            Posting.objects.create(
                category    = category,
                user        = user,
                title       = data['title'],
                content     = data['content']
            )

            return JsonResponse({'message' : 'Posting Success'}, status=201)

        except KeyError :
            return JsonResponse({'message' : 'Key Error'}, status=400)

        except Category.DoesNotExist :
            return JsonResponse({'message' : 'Category matching query does not exist'}, status=400)
        
    def get(self, request) :
        try :
            keyword = request.GET.get('keyword', None)

            q = Q()

            q.add(Q(title__icontains=keyword), q.AND)
            q.add(Q(content__icontains=keyword), q.OR)

            posting_list = [{
                'id'         : posting.id,
                'title'      : posting.title,
                'content'    : posting.content,
                'created_at' : posting.created_at,
                'name'       : User.objects.get(id=posting.user_id).name,
                'user_id'    : User.objects.get(id=posting.user_id).id
            }for posting in Posting.objects.filter(q)]

            return JsonResponse({'posting_list':posting_list}, status=200)
        
        except ValueError :
            return JsonResponse({'message' : 'Value Error'}, status=400)

class PostingParamView(View) :
    def get(self, request, posting_id) :
        try : #특정 번호의 포스트 조회 / 같은유저면 조회수 증가x 
            postings = Posting.objects.get(id=posting_id)
            
            print(request.session.__dict__)

           # return JsonResponse({'login_session', login_session}, status=200)
        
        except Posting.DoesNotExist :
            return JsonResponse({'message' : 'Posting matching query does not exist'})
    #@login_decorator
    def post(self, request, posting_id) :
        try :
            data = json.loads(request.body)
            
            posting = Posting.objects.get(id=posting_id)

            title    = data.get('title',    posting.title)
            content  = data.get('content',  posting.content)
            category = data.get('category', posting.category_id)

            Posting.objects.filter(id=posting_id).update(
                title    = title,
                content  = content,
                category = category
            )

            return JsonResponse({'message' : 'Update Success'}, status=201)
        
        except Posting.DoesNotExist :
            return JsonResponse({'message' : 'Posting matching query does not exist'}, status=400)

    #@login_decorator
    def delete(self, request, posting_id) :
        try :
            posting = Posting.objects.get(id=posting_id)
            posting.delete()
            return JsonResponse({'message' : 'Delete Success'}, status=201)
        
        except Posting.DoesNotExist :
            return JsonResponse({'message' : 'Posting matching query does not exist'}, status=400)