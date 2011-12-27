from django.db import models

class ApiKey(models.Model):
    key = models.CharField(max_length=32,unique=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        inactiveText = ""
        if not self.active:
            inactiveText = "(Deactivated)"
        return "%s %s" % (self.key,inactiveText)

    def hasPrivilege(self,privilege):
        if not self.active:
            return False

        if privilege == '__ACTIVE__':
            return True

        return self.apiprivilege_set.filter(privilege=privilege).count() > 0

class ApiPrivilege(models.Model):
    privilege = models.CharField(max_length=32)
    key = models.ForeignKey(ApiKey)

    def __unicode__(self):
        return "%s... for %s" % (self.key.key[:10],self.privilege)

    class Meta:
        unique_together = ('privilege','key')