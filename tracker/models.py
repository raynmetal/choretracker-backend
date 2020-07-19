import jwt
import datetime 

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db.models.signals import pre_delete 
from django.dispatch import receiver 

from common.util.simplecfs import _next_user_get, _order_project

from tracker.managers import CustomUserManager

# Create your models here.
class User(AbstractUser, PermissionsMixin):
    username = None
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField('email address', unique=True, db_index=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()
    def __str__(self):
        return self.email
    @property 
    def token(self):
        return self._generate_jwt_token() 
    
    def _generate_jwt_token(self):
        dt = datetime.datetime.now() + datetime.timedelta(days=60)
        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')
    
    def get_calendar(self):
        """
        Returns a dictionary where
            key: timestamp of days on which tasks are scheduled 
            dictionary: A list of tuples whose first element is a User and second a Chore
        """
        date_wise = {}
        chores = self.chores.all()
        today = datetime.datetime.today()

        # Get calendars for each individual chore associated with this user
        for chore in chores:
            chore_calendar = chore.get_task_calendar()

            # Build a dictionary where the key is the timestamp of when the chore 
            # is scheduled, and value is a tuple containing a user and a chore
            for user_id, offset in chore_calendar:
                date = today + datetime.timedelta(days=offset)
                date = date.timestamp()
                date_present = date_wise.get(date)
                # Append to existing list of users
                if date_present:
                    date_wise[date].append((User.objects.get(pk=user_id), chore))
                    continue 
                date_wise[date] = [(User.objects.get(pk=user_id), chore)]
        return date_wise



class Space(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(User, related_name='spaces')
    parent = models.ForeignKey(
        'self', 
        null=True, 
        related_name='child',
        on_delete=models.CASCADE)
    
    @property
    def full_name (self):
        # Recursively return the full name of this space
        if not(self.parent):
            return self.name 
        return self.parent.full_name + "/" + self.name
    
    def initialize_members(self):
        for member in self.parent.members.all():
            self.members.add(member)

    

class Chore(models.Model):
    name = models.CharField(max_length=200)
    parent_space = models.ForeignKey(
        Space,
        related_name="chores",
        on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='chores', through='UserChore')
    min_vwork = models.FloatField(default=-1.0)
    interval = models.PositiveIntegerField(default=1)
    next_date = models.DateField(default=datetime.date.today() + datetime.timedelta(days=1))
    last_date = models.DateField(null=True)
    next_user = models.ForeignKey(User, null=True, related_name='upcoming_%(class)s', on_delete=models.SET_NULL)
    last_user = models.ForeignKey(User, null=True, related_name='completed_%(class)s', on_delete=models.SET_NULL)

    def schedule_chore(self, date): 
        """
        Schedules chore for date, which is a datetime.date object. Also updates 
        min_vwork
        """
        self.next_date = date
        self.get_next_user()
        if self.next_user:
            self.min_vwork = self.userchore_set.filter(chore_id=self.pk).get(user_id=self.next_user.id).vwork
            self.save()

    def get_next_user(self):
        """ 
        Uses _next_user_get to retrieve next user to be scheduled on a chore.
        """
        vworks = self._generate_vworks()
        next_user_id = _next_user_get(vworks, self.last_user_id)
        if(next_user_id != None):
            try:
                self.next_user = self.users.get(pk=next_user_id)
                self.save()
                return

            except:
                self.next_user = None
                self.save()
                return

    def postpone(self):
        """
        Postpones a chore for the day after today or next_date, whichever is greater
        """
        self.schedule_chore(
            (datetime.date.today()  if datetime.date.today() > self.next_date else self.next_date)
            + datetime.timedelta(days=1))
    
    def complete_chore(self, user_id):
        """
        Mark chore complete by user id, update their work score and 
        schedule the next round of this chore.
        """
        # Get and update userchore with least vwork value 
        userchore = self.userchore_set.filter(chore=self.pk).get(user=user_id)
        userchore.increment_work()
        userchore.save()

        # Update last_date
        self.last_date = datetime.date.today()

        # Schedule next round of this chore
        self.schedule_chore(datetime.date.today() + datetime.timedelta(days=self.interval))
    
    def get_task_calendar(self):
        vworks = self._generate_vworks()
        vdeltas = self._generate_vdeltas()
        today = datetime.date.today()
        initial_offset = ((today if today > self.last_date else self.last_date) - today)
        return _order_project(vworks, vdeltas, self.interval, initial_offset.days, self.last_user, 30)

    def _generate_vworks(self):
        """
        Generates a list of tuples with two elements
            1. user_id
            2. vwork values
        """
        vworks = []

        # Retrieve all users that are responsible for this chore, excluding users who aren't 
        # available
        userchores = self.userchore_set.filter(chore=self.pk).exclude(available=False)
        print("userchores")
        print(userchores)

        # Build vworks 
        for userchore in userchores:
            vworks.append((userchore.user_id, userchore.vwork))
        
        # Update last_date field 
        self.last_date = datetime.date.today()

        print("vworks")
        print(vworks)
        return vworks

    def _generate_vdeltas(self):
        """
        Generates a list of tuples with two elements
            1. user_id
            2. vdelta value
        """
        vdeltas = []

        # Retrieve all users that are responsible for this chore, excluding users who aren't 
        # available
        userchores = self.userchore_set.filter(chore=self.pk).exclude(available=False)
        print("userchores")
        print(userchores)

        # Build vworks 
        for userchore in userchores:
            vdeltas.append((userchore.user_id, userchore.vdelta))
        
        # Update last_date field 
        self.last_date = datetime.date.today()

        print("vdeltas")
        print(vdeltas)
        return vdeltas

    def _initialize_users(self):
        for user in self.parent_space.members.all():
            self.users.add(user, through_defaults={
                'vwork':0.0,
                'vdelta':1.0,
                'work':0,
                'delta_src':100
            })



class UserChore(models.Model):
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    vwork = models.FloatField(default=0)
    vdelta = models.FloatField(default=1.0)
    work = models.IntegerField(default=0)
    delta_src = models.FloatField(default=100.0)
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ['vwork'] 
    
    def increment_work(self):
        self.vwork += self.vdelta 
        self.work += 1

    def update_delta(self, delta_src):
        self.delta_src = delta_src 
        self.vdelta = delta_src/100.0
    
    def mark_unavailable(self):
        self.available = False 
    
    def mark_available(self):
        """
        Marks user available after a period of their absence. Also has the 
        effect of resetting their vwork value
        """
        self.available = True 
        self.vwork = self.chore.min_vwork



@receiver(pre_delete, sender=User)
def cascade_delete_space(sender, instance, **kwargs):
    for space in instance.spaces.all():
        if space.members.count() == 1:
            space.delete()