from django.db import models

# Create your models here.
class User(models.Model):
    class Meta:
        db_table = 'user'

    # 名称
    user_name = models.CharField(max_length=50, db_column='user_name')
    # 密码
    pass_word = models.CharField(max_length=50, db_column='pass_word')
    # 备注
    remark = models.CharField(max_length=64, db_column='remark')
    # 邮件
    email = models.CharField(max_length=50, db_column='email')

    def __str__(self):
        return self.user_num.encode('utf-8')
