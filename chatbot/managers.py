from django.db import models

class botManager(models.Manager):
    def user(self, request):
        """ Returns only results owned by the current user, or all if super admin """
        return super(botManager, self).get_queryset().filter(author=request.user)

class cbotManager(models.Manager):
    def user(self, request):
        """ Returns only results owned by the current user, or all if super admin """
        return super(cbotManager, self).get_queryset().filter(author=request.user).filter(twit_capable = False)
    
class tbotManager(models.Manager):
    def get_twitter_capable(self,request):
        """ Returns only bots that have been twitter enabled """
        return super(tbotManager, self).get_queryset().filter(author=request.user).filter(twit_capable = True)

class configManager(models.Manager):
    def user(self, request):
        """ Returns only results owned by the current user, or all if super admin """
        #return super(configManager, self).get_queryset().filter(models.Q(author=request.user) | models.Q(is_public=True))  ## For public showing, temporarily disabled
        return super(configManager, self).get_queryset().filter(author=request.user)

class fileManager(models.Manager):
    def user(self, request):
        """ Returns only results owned by the current user, or all if super admin """
        return super(fileManager, self).get_queryset().filter(author=request.user)