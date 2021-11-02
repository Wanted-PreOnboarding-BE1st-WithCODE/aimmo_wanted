from django.urls    import path

from postings.views import (
    PostingView,
    PostingParamView
)
urlpatterns =[
    path('', PostingView.as_view()), 
    path('/<int:posting_id>', PostingParamView.as_view())  
]