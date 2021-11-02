from django.urls    import path

from postings.views import (
    PostingView,
    PostingParamView,
    CommentView,
    CommentDetailView,
)

urlpatterns =[
    path('', PostingView.as_view()), 
    path('/<int:posting_id>', PostingParamView.as_view()),
    path('/comments/<int:posting_id>', CommentView.as_view()),
    path('/comment/<int:comment_id>', CommentDetailView.as_view()),  
]