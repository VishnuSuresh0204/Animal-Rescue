from django.db import models
from django.contrib.auth.models import AbstractUser

# Extended User for authentication
class Login(AbstractUser):
    USERTYPE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('rescueTeam', 'Rescue Team'),
        ('vet', 'Veterinarian'),
        ('careCenter', 'Care Center'),
    ]
    usertype = models.CharField(max_length=50, null=True, choices=USERTYPE_CHOICES)
    view_password = models.CharField(max_length=50, null=True)


# User Profile
class UserProfile(models.Model):
    user = models.OneToOneField(Login, on_delete=models.CASCADE, related_name='user_profile')
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to='users/', null=True, blank=True)

    def __str__(self):
        return self.name or str(self.user)


# Rescue Team Profile
class RescueTeam(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Blocked', 'Blocked')]
    user = models.OneToOneField(Login, on_delete=models.CASCADE, related_name='rescue_profile')
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)
    vehicle = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to='rescue_team/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return self.name or str(self.user)


# Veterinarian Profile
class Veterinarian(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Blocked', 'Blocked')]
    user = models.OneToOneField(Login, on_delete=models.CASCADE, related_name='vet_profile')
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)
    qualification = models.CharField(max_length=100, null=True)
    experience = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to='vets/', null=True, blank=True)
    certificate = models.FileField(upload_to='vet_certificates/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return self.name or str(self.user)


# Care Center Profile
class CareCenter(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Blocked', 'Blocked')]
    user = models.OneToOneField(Login, on_delete=models.CASCADE, related_name='care_profile')
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=200, null=True)
    license_number = models.CharField(max_length=100, null=True)
    image = models.ImageField(upload_to='care_centers/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return self.name or str(self.user)


# User reports an injured/sick animal
class RescueReport(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('Rescued', 'Rescued'),
        ('AtVet', 'At Vet'),
        ('Treated', 'Treated'),
        ('Closed', 'Closed'),
    ]
    reported_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reports')
    description = models.TextField()
    animal_type = models.CharField(max_length=50, null=True)  # dog, cat, etc.
    location_text = models.CharField(max_length=300, null=True)
    photo = models.ImageField(upload_to='rescue_reports/', null=True, blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_team = models.ForeignKey(RescueTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_reports')

    def __str__(self):
        return f"Report #{self.id} by {self.reported_by.name} - {self.status}"


# Rescued Animal record
class RescuedAnimal(models.Model):
    CONDITION_CHOICES = [
        ('Critical', 'Critical'),
        ('Serious', 'Serious'),
        ('Stable', 'Stable'),
        ('Recovering', 'Recovering'),
        ('Healthy', 'Healthy'),
    ]
    STATUS_CHOICES = [
        ('UnderTreatment', 'Under Treatment'),
        ('ReadyForAdoption', 'Ready For Adoption'),
        ('Adopted', 'Adopted'),
    ]
    rescue_report = models.OneToOneField(RescueReport, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    species = models.CharField(max_length=50, null=True)
    breed = models.CharField(max_length=100, null=True, blank=True)
    age = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='Stable')
    photo = models.ImageField(upload_to='animals/', null=True, blank=True)
    admitted_at = models.DateTimeField(auto_now_add=True)
    assigned_vet = models.ForeignKey(Veterinarian, on_delete=models.SET_NULL, null=True, blank=True, related_name='animals')
    care_center = models.ForeignKey(CareCenter, on_delete=models.SET_NULL, null=True, blank=True, related_name='animals')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='UnderTreatment')
    marked_for_adoption_by_vet = models.BooleanField(default=False)
    listed_for_adoption = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name or 'Animal'} ({self.species}) - {self.status}"


# Medical Record
class MedicalRecord(models.Model):
    animal = models.ForeignKey(RescuedAnimal, on_delete=models.CASCADE, related_name='medical_records')
    vet = models.ForeignKey(Veterinarian, on_delete=models.SET_NULL, null=True)
    diagnosis = models.TextField()
    treatment = models.TextField()
    notes = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    condition_after = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Record for {self.animal} on {self.date}"


# Prescribed Medicine
class PrescribedMedicine(models.Model):
    animal = models.ForeignKey(RescuedAnimal, on_delete=models.CASCADE, related_name='medicines')
    vet = models.ForeignKey(Veterinarian, on_delete=models.SET_NULL, null=True)
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)  # e.g. "Twice a day"
    duration = models.CharField(max_length=100)   # e.g. "7 days"
    prescribed_on = models.DateField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.medicine_name} for {self.animal}"


# Prescribed Food
class PrescribedFood(models.Model):
    animal = models.ForeignKey(RescuedAnimal, on_delete=models.CASCADE, related_name='food_prescriptions')
    vet = models.ForeignKey(Veterinarian, on_delete=models.SET_NULL, null=True)
    food_type = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)  # e.g. "3 times a day"
    prescribed_on = models.DateField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.food_type} for {self.animal}"


# Care Center logs food/medicine given
class CareLog(models.Model):
    LOG_TYPE_CHOICES = [('Food', 'Food'), ('Medicine', 'Medicine')]
    animal = models.ForeignKey(RescuedAnimal, on_delete=models.CASCADE, related_name='care_logs')
    care_center = models.ForeignKey(CareCenter, on_delete=models.CASCADE)
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES)
    description = models.CharField(max_length=200)
    given_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    done = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.log_type} log for {self.animal} on {self.date}"


# Adoption Request
class AdoptionRequest(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='adoption_requests')
    animal = models.ForeignKey(RescuedAnimal, on_delete=models.CASCADE, related_name='adoption_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Adoption request by {self.user.name} for {self.animal}"


# Chat between Vet and Care Center
class Chat(models.Model):
    SENDER_TYPE_CHOICES = [('vet', 'Veterinarian'), ('care', 'Care Center')]
    vet = models.ForeignKey(Veterinarian, on_delete=models.CASCADE, related_name='chats')
    care_center = models.ForeignKey(CareCenter, on_delete=models.CASCADE, related_name='chats')
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPE_CHOICES)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat: {self.sender_type} - {self.sent_at}"
