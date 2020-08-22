from django.test import TestCase

from tracker.models import User, Chore, Space

# Create your tests here.
class ModelTestCase(TestCase):
    def setUp(self):
        root_space = Space.objects.create(name="root space")
        rootchild_space = Space.objects.create(name="rootchild space", parent=root_space)
        #print("Root space = " + str(root_space))
        #print("Root's child space = " + str(rootchild_space))
        
        for i in range(5):
            user = User.objects.create(email="user"+str(i)+"@gmail.com", password="1234234Zo")
            space = Space.objects.create(name="space"+str(i), parent=rootchild_space)
            root_space.members.add(user)
            
            #print("user " + str(i) + " = " + str(user))
            #print("space " + str(i) + " = " + str(space))

            for j in range(i+1):
                Chore.objects.create(name="chore"+str(j), interval=(j+1)*(i+1), parent_space=space)

                #print("chore " + str(i) + ", " + str(j) + " = " + str(chore))

        rootchild_space.initialize_members_from_parent_space()
        for i in range(5):
            Space.objects.get(name="space"+str(i)).initialize_members_from_parent_space()
        
        for user in User.objects.all():
            root_space.assign_member_to_chores(user)
    
    def test_members_inheritance(self):
        """
        Root_space and all its supspaces must contain an equal number of
        members as all the subspaces inherit members from the root space
        """
        root_space = Space.objects.get(name="root space")
        rootchild_space = Space.objects.get(name="rootchild space")

        self.assertEqual(root_space.members.count(), 5)
        self.assertEqual(rootchild_space.members.count(), 5)

        for i in range(5):
            space = Space.objects.get(name="space"+str(i))
            self.assertEqual(space.members.count(), 5)
    
    def test_chore_assignment(self):
        """
        Each chore should have users assigned to it from its parent 
        space 
        """
        for chore in Chore.objects.all():
            self.assertEqual(chore.users.count(), 5)

    def test_chore_completion(self):
        """
        Each time a chore is marked complete, vwork and work should
        both be incremented by vdelta and 1 respectively
        """
        user = User.objects.first()
        userchore = user.userchore_set.first()
        userchore.increment_work()
        self.assertEqual(userchore.work, 1)
        self.assertEqual(userchore.vwork, 1.0)

        userchore.delta_src = 200 
        userchore.increment_work()
        self.assertEqual(userchore.work, 2)
        self.assertEqual(userchore.vwork, 3.0)
    
    def test_chore_frequency(self):
        """
        Chores with greater intervals should appear less frequently 
        in the calendar than chores with smaller intervals
        """

        user = User.objects.first()
        user_calendar = user.get_calendar()

        count = {'chore0':0, 'chore1':0, 'chore2':0, 'chore3':0,'chore4':0}
        for day in user_calendar.values():
            for user,chore in day:
                count[chore.name] += 1
        self.assertGreater(count['chore0'], count['chore1'])
        self.assertGreater(count['chore3'], count['chore4'])
        self.assertGreater(count['chore1'], count['chore3'])
        
    def test_availability(self):
        """
        Tests relationship between user availability and other fields
        """
        chore = Chore.objects.first()
        userchore = chore.userchore_set.first()
        space = Space.objects.get(name='root space')
        userspace = space.userspace_set.get(user_id=userchore.user_id)

        userchore.increment_work()
        userchore.increment_work()
        
        userchore.mark_unavailable()
        self.assertEqual(userchore.available, False)
        
        userchore.mark_available()
        self.assertEqual(userchore.available, True)
        # vwork should not have been reset to 0.0
        self.assertEqual(userchore.vwork, 2.0)

        userspace.mark_unavailable()
        userchore.refresh_from_db()
        self.assertEqual(userchore.available, False)

        userspace.mark_available()
        userchore.refresh_from_db()
        self.assertEqual(userchore.available, True)

        userchore.mark_unavailable()
        # Increase min_vwork of a chore to 3.0
        for a_userchore in chore.userchore_set.filter(available=True):
            chore.mark_complete(a_userchore.user)
            chore.mark_complete(a_userchore.user)  
            chore.mark_complete(a_userchore.user)     

        userchore.mark_available()
        self.assertEqual(userchore.vwork, 3.0)

        userspace.mark_unavailable()
        # Increase min_vwork of a chore to 6.0
        for a_userchore in chore.userchore_set.filter(available=True):
            chore.mark_complete(a_userchore.user)
            chore.mark_complete(a_userchore.user)  
            chore.mark_complete(a_userchore.user)     

        userspace.mark_available()
        userchore.refresh_from_db()

        self.assertEqual(userchore.chore.min_vwork, 6.0)
        self.assertEqual(userchore.vwork, 6.0)

