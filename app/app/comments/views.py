from models import Comment
import datetime
from rest_framework import viewsets
from serializers import CommentSerializer
from rest_framework.response import Response
from rest_framework.decorators import list_route
from ratelimit.decorators import ratelimit
from rest_framework.exceptions import Throttled
from django.core.cache import cache
from ipware.ip import get_ip

def check_locked_out(request):
    '''
        method to verify a requestor is not locked out before handling request
    '''
    key = str(get_ip(request)) + "_locked"
    if cache.get(key):
        raise Throttled(detail="you have been temporarily locked out")

def lockout(request, timeout):
    '''
        method to lockout a requestor by ip address
    '''
    key = str(get_ip(request)) + "_locked"
    cache.set(key, True, timeout)
    

class CommentView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def list(self, request):
        '''
            api to request a list of comments. takes an optional parameter url. when this 
            parameter is set the comments returned will all be associated to the provided url
        '''
        queryset = Comment.objects.all()

        #determine if url parameter was provided or if all comments should be returned
        url = request.GET.get('url', None);
        if url:
            queryset = queryset.filter(url=url)
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        '''
            api to create a new comment. can lockout requester by ip addres under the following scenarios:
                1) a request matching username, comment and url was already created in the last 24 hrs
                   this will result in a 60 second timeout
                2) a single ip address has already posted 2 comments withint the past 60 seconds
                   this will result in a 5 minute timeout
        '''
        #verify the user is not locked out before processing request
        check_locked_out(request);

        # get needed data off request
        comment_str = request.data.get("comment");
        username = request.data.get("username")
        url = request.data.get("url")
        ip = get_ip(request)

        #check to see if there is an exact matching comment made within 24 hours
        date_from = datetime.datetime.now() - datetime.timedelta(days=1)
        if(Comment.objects.filter(comment=comment_str, username=username,
                                  url=url, date__gte=date_from).count() > 0):
            lockout(request, 60)    #set lockout key to expire in 60 seconds
            raise Throttled(detail=("This is a duplicate comment from within 24 hours"))

        #check to see if a user has made more then the alloted number of comments in 60 seconds
        date_from = datetime.datetime.now() - datetime.timedelta(minutes=1)
        if(Comment.objects.filter(ip=ip, date__gte=date_from).count() >= 2):
            lockout(request, 60 * 5) # set lockout key to expire in 5 minutes
            raise Throttled(detail=("Maximum comments made within 2 minutes"))

        #save comment to database
        comment = Comment.objects.create(username=username,
                                         comment=comment_str,
                                         url=url,
                                         ip=ip)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

