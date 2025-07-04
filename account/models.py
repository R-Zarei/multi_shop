import uuid

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, phone, full_name, password=None):
        """
        Creates and saves a User with the given email
        and password.
        """
        if not phone:
            raise ValueError("Users must have an email address")

        user = self.model(
            phone=phone,
            full_name=full_name
            # email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None):
        """
        Creates and saves a superuser with the given email
        and password.
        """
        user = self.create_user(
            phone=phone,
            password=password,
            full_name='Superuser'
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True, null=True, blank=True)
    phone = models.CharField(unique=True, max_length=12, verbose_name='phone number')
    full_name = models.CharField(verbose_name="full name", max_length=100)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone"   # The field with which the user authenticates.
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Province(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class City(models.Model):
    name = models.CharField(max_length=50)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return f'{self.name}'


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=300)
    zipcode = models.CharField(max_length=10)

    def __str__(self):
        return self.address


'''
class Otp(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone = models.CharField(max_length=11)
    rand_code = models.CharField(max_length=10)
    password = models.CharField(max_length=30)
    full_name = models.CharField(max_length=100)
    expiration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone
'''

province_choices = [
        ('tehran', 'Tehran'),
        ('khorasan-razavi', 'Khorasan Razavi'),
        ('isfahan', 'Isfahan'),
        ('fars', 'Fars'),
        ('alborz', 'Alborz'),
        ('ardabil', 'Ardabil'),
        ('bushehr', 'Bushehr'),
        ('chaharmahal-bakhtiari', 'Chaharmahal and Bakhtiari'),
        ('gilan', 'Gilan'),
        ('golestan', 'Golestan'),
        ('hamadan', 'Hamadan'),
        ('hormozgan', 'Hormozgan'),
        ('ilam', 'Ilam'),
        ('kerman', 'Kerman'),
        ('kermanshah', 'Kermanshah'),
        ('khuzestan', 'Khuzestan'),
        ('kohgiluyeh-boyer-ahmad', 'Kohgiluyeh and Boyer-Ahmad'),
        ('kurdistan', 'Kurdistan'),
        ('lorestan', 'Lorestan'),
        ('markazi', 'Markazi'),
        ('mazandaran', 'Mazandaran'),
        ('north-khorasan', 'North Khorasan'),
        ('qazvin', 'Qazvin'),
        ('qom', 'Qom'),
        ('semnan', 'Semnan'),
        ('sistan-baluchestan', 'Sistan and Baluchestan'),
        ('south-khorasan', 'South Khorasan'),
        ('west-azarbaijan', 'West Azerbaijan'),
        ('yazd', 'Yazd'),
        ('zanjan', 'Zanjan'),
    ]