from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import *

def index(request):
    return render(request, 'index.html')

# --- Auth Views ---
def login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            auth_login(request, user)
            request.session['role'] = user.usertype
            if user.usertype == 'admin':
                return redirect('/admin_home/')
            elif user.usertype == 'user':
                try:
                    profile = user.user_profile
                    request.session['profile_id'] = profile.id
                    return redirect('/user_home/')
                except UserProfile.DoesNotExist:
                    messages.error(request, "User profile not found.")
            elif user.usertype == 'rescueTeam':
                try:
                    team = user.rescue_profile
                    if team.status != 'Approved':
                        messages.error(request, f"Your registration is {team.status}.")
                        auth_logout(request)
                        return redirect('/login/')
                    request.session['profile_id'] = team.id
                    return redirect('/rescue_home/')
                except RescueTeam.DoesNotExist:
                    messages.error(request, "Rescue team profile not found.")
            elif user.usertype == 'vet':
                try:
                    vet = user.vet_profile
                    if vet.status != 'Approved':
                        messages.error(request, f"Your registration is {vet.status}.")
                        auth_logout(request)
                        return redirect('/login/')
                    request.session['profile_id'] = vet.id
                    return redirect('/vet_home/')
                except Veterinarian.DoesNotExist:
                    messages.error(request, "Veterinarian profile not found.")
            elif user.usertype == 'careCenter':
                try:
                    center = user.care_profile
                    if center.status != 'Approved':
                        messages.error(request, "Care center not approved or blocked")
                        auth_logout(request)
                        return redirect('/login/')
                    request.session['profile_id'] = center.id
                    return redirect('/care_home/')
                except CareCenter.DoesNotExist:
                    messages.error(request, "Care center profile not found.")
        else:
            messages.error(request, "Invalid username or password")
            return redirect('/login/')
    return render(request, 'login.html')

def user_reg(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        n = request.POST.get('name')
        e = request.POST.get('email')
        ph = request.POST.get('phone')
        ad = request.POST.get('address')
        img = request.FILES.get('image')
        if not Login.objects.filter(username=u).exists():
            user = Login.objects.create_user(username=u, password=p, usertype='user', view_password=p)
            UserProfile.objects.create(user=user, name=n, email=e, phone=ph, address=ad, image=img)
            messages.success(request, "Registration successful. Please login.")
            return redirect('/login/')
        else:
            messages.error(request, "Username already exists")
    return render(request, 'userreg.html')

def rescue_reg(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        n = request.POST.get('team_name')
        e = request.POST.get('email')
        ph = request.POST.get('phone')
        ad = request.POST.get('address')
        vh = request.POST.get('vehicle')
        img = request.FILES.get('image')
        if not Login.objects.filter(username=u).exists():
            user = Login.objects.create_user(username=u, password=p, usertype='rescueTeam', view_password=p)
            RescueTeam.objects.create(user=user, name=n, email=e, phone=ph, address=ad, vehicle=vh, image=img)
            messages.success(request, "Registration successful. Wait for admin approval.")
            return redirect('/login/')
        else:
            messages.error(request, "Username already exists")
    return render(request, 'rescuereg.html')

def vet_reg(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        n = request.POST.get('name')
        e = request.POST.get('email')
        ph = request.POST.get('phone')
        ql = request.POST.get('qualification')
        ex = request.POST.get('experience')
        img = request.FILES.get('image')
        if not Login.objects.filter(username=u).exists():
            user = Login.objects.create_user(username=u, password=p, usertype='vet', view_password=p)
            Veterinarian.objects.create(user=user, name=n, email=e, phone=ph, qualification=ql, experience=ex, image=img)
            messages.success(request, "Registration successful. Wait for admin approval.")
            return redirect('/login/')
        else:
            messages.error(request, "Username already exists")
    return render(request, 'vetreg.html')

def care_registration(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        n = request.POST.get('name')
        e = request.POST.get('email')
        ph = request.POST.get('phone')
        ad = request.POST.get('address')
        li = request.POST.get('license')
        img = request.FILES.get('image')
        if not Login.objects.filter(username=u).exists():
            user = Login.objects.create_user(username=u, password=p, usertype='careCenter', view_password=p)
            CareCenter.objects.create(user=user, name=n, email=e, phone=ph, address=ad, license_number=li, image=img)
            messages.success(request, "Registration successful. Wait for admin approval.")
            return redirect('/login/')
        else:
            messages.error(request, "Username already exists")
    return render(request, 'carereg.html')

def logout(request):
    auth_logout(request)
    return redirect('/')

# --- Admin Views ---
def admin_home(request):
    return render(request, 'ADMIN/admin_home.html')

def admin_manage_users(request):
    vets = Veterinarian.objects.all()
    teams = RescueTeam.objects.all()
    users = UserProfile.objects.all()
    return render(request, 'ADMIN/admin_manage_users.html', {'vets': vets, 'teams': teams, 'users': users})

def admin_approve_team(request):
    tid = request.GET.get('id')
    team = RescueTeam.objects.filter(id=tid).first()
    if team:
        team.status = 'Approved'
        team.save()
        messages.success(request, f"Approved {team.name}")
    return redirect('/admin_manage_users/')

def admin_reject_team(request):
    tid = request.GET.get('id')
    team = RescueTeam.objects.filter(id=tid).first()
    if team:
        team.status = 'Rejected'
        team.save()
        messages.info(request, f"Rejected {team.name}")
    return redirect('/admin_manage_users/')

def admin_block_user(request):
    uid = request.GET.get('id')
    user = Login.objects.filter(id=uid).first()
    if user:
        user.is_active = False
        user.save()
        messages.info(request, f"Blocked {user.username}")
    return redirect('/admin_manage_users/')

def admin_unblock_user(request):
    uid = request.GET.get('id')
    user = Login.objects.filter(id=uid).first()
    if user:
        user.is_active = True
        user.save()
        messages.success(request, f"Unblocked {user.username}")
    return redirect('/admin_manage_users/')

def admin_manage_care_centers(request):
    centers = CareCenter.objects.all()
    return render(request, 'ADMIN/admin_manage_care_centers.html', {'centers': centers})

def admin_add_care_center(request):
    if request.method == 'POST':
        # ... (logic remains same)
        user = Login.objects.create_user(username=u, password=p, usertype='careCenter', view_password=p)
        CareCenter.objects.create(user=user, name=n, email=e, phone=ph, address=ad, license_number=li, image=img, status='Approved')
        messages.success(request, "Care Center added successfully")
        return redirect('/admin_manage_care_centers/')
    return render(request, 'ADMIN/admin_add_care_center.html')

def admin_edit_care_center(request):
    cid = request.GET.get('id')
    center = CareCenter.objects.get(id=cid)
    if request.method == 'POST':
        # ... (logic remains same)
        center.save()
        messages.success(request, "Care Center updated")
        return redirect('/admin_manage_care_centers/')
    return render(request, 'ADMIN/admin_edit_care_center.html', {'center': center})

def admin_delete_care_center(request):
    cid = request.GET.get('id')
    center = CareCenter.objects.filter(id=cid).first()
    if center:
        center.user.delete()
        messages.info(request, "Care Center deleted")
    return redirect('/admin_manage_care_centers/')

def admin_assign_rescue(request):
    reports = RescueReport.objects.filter(status='Pending')
    teams = RescueTeam.objects.filter(status='Approved')
    return render(request, 'ADMIN/admin_assign_rescue.html', {'reports': reports, 'teams': teams})

def admin_assign_to_team(request):
    rid = request.GET.get('rid')
    tid = request.GET.get('tid')
    report = RescueReport.objects.filter(id=rid).first()
    team = RescueTeam.objects.filter(id=tid).first()
    if report and team:
        report.assigned_team = team
        report.status = 'Assigned'
        report.save()
        messages.success(request, f"Assigned to {team.name}")
    return redirect('/admin_assign_rescue/')

def admin_monitor_all(request):
    reports = RescueReport.objects.all()
    animals = RescuedAnimal.objects.all()
    adoptions = AdoptionRequest.objects.all()
    return render(request, 'ADMIN/admin_monitor_all.html', {'reports': reports, 'animals': animals, 'adoptions': adoptions})

def admin_report(request):
    rescued_count = RescuedAnimal.objects.count()
    treated_count = MedicalRecord.objects.count()
    adopted_count = AdoptionRequest.objects.filter(status='Approved').count()
    return render(request, 'ADMIN/admin_report.html', {
        'rescued': rescued_count,
        'treated': treated_count,
        'adopted': adopted_count
    })

# --- User Views ---
def user_home(request):
    return render(request, 'USER/user_home.html')

def user_report_animal(request):
    if 'profile_id' in request.session:
        if request.method == 'POST':
            # ... (logic remains same)
            messages.success(request, "Report submitted.")
            return redirect('/user_home/')
        return render(request, 'USER/report_animal.html')
    return redirect('/login/')

def user_track_rescue(request):
    if 'profile_id' in request.session:
        profile = UserProfile.objects.get(id=request.session['profile_id'])
        reports = RescueReport.objects.filter(reported_by=profile)
        return render(request, 'USER/user_track_rescue.html', {'reports': reports})
    return redirect('/login/')

def user_request_adoption(request):
    animals = RescuedAnimal.objects.filter(listed_for_adoption=True)
    return render(request, 'USER/user_request_adoption.html', {'animals': animals})

def user_submit_adoption(request):
    if 'profile_id' in request.session:
        aid = request.GET.get('id')
        profile = UserProfile.objects.get(id=request.session['profile_id'])
        animal = RescuedAnimal.objects.get(id=aid)
        AdoptionRequest.objects.get_or_create(user=profile, animal=animal)
        messages.success(request, "Adoption request sent.")
        return redirect('/user_request_adoption/')
    return redirect('/login/')

# --- Rescue Team Views ---
def rescue_home(request):
    return render(request, 'RESCUE/rescue_home.html')

def rescue_view_alerts(request):
    if 'profile_id' in request.session:
        team = RescueTeam.objects.get(id=request.session['profile_id'])
        reports = RescueReport.objects.filter(assigned_team=team)
        return render(request, 'RESCUE/rescue_view_alerts.html', {'reports': reports})
    return redirect('/login/')

def rescue_respond(request):
    rid = request.GET.get('id')
    report = RescueReport.objects.filter(id=rid).first()
    if report:
        report.status = 'Rescued'
        report.save()
        messages.success(request, "Status updated to Rescued")
    return redirect('/rescue_view_alerts/')

def rescue_update_status(request):
    rid = request.GET.get('id')
    report = RescueReport.objects.filter(id=rid).first()
    if report and report.status == 'Rescued':
        report.status = 'AtVet'
        report.save()
        messages.success(request, "Status updated to At Vet")
    return redirect('/rescue_view_alerts/')

def rescue_transport(request):
    rid = request.GET.get('id')
    report = RescueReport.objects.get(id=rid)
    vets = Veterinarian.objects.filter(status='Approved')
    centers = CareCenter.objects.filter(status='Approved')
    if request.method == 'POST':
        # ... (logic remains same)
        messages.success(request, "Animal transported.")
        return redirect('/rescue_view_alerts/')
    return render(request, 'RESCUE/rescue_transport.html', {'report': report, 'vets': vets, 'centers': centers})

# --- Vet Views ---
def vet_home(request):
    return render(request, 'VET/vet_home.html')

def vet_view_animals(request):
    if 'profile_id' in request.session:
        vet = Veterinarian.objects.get(id=request.session['profile_id'])
        animals = RescuedAnimal.objects.filter(assigned_vet=vet)
        return render(request, 'VET/vet_view_animals.html', {'animals': animals})
    return redirect('/login/')

def vet_treatment(request):
    aid = request.GET.get('id')
    animal = RescuedAnimal.objects.get(id=aid)
    records = animal.medical_records.all()
    return render(request, 'VET/vet_treatment.html', {'animal': animal, 'records': records})

def vet_add_medical_record(request):
    if 'profile_id' in request.session:
        aid = request.GET.get('id')
        animal = RescuedAnimal.objects.get(id=aid)
        vet = Veterinarian.objects.get(id=request.session['profile_id'])
        if request.method == 'POST':
            # ... (logic remains same)
            messages.success(request, "Medical record added")
            return redirect(f'/vet_treatment/?id={aid}')
        return render(request, 'VET/vet_add_medical_record.html', {'animal': animal})
    return redirect('/login/')

def vet_prescribe(request):
    if 'profile_id' in request.session:
        aid = request.GET.get('id')
        animal = RescuedAnimal.objects.get(id=aid)
        vet = Veterinarian.objects.get(id=request.session['profile_id'])
        if request.method == 'POST':
            # ... (logic remains same)
            messages.success(request, f"{ptype} prescribed")
            return redirect(f'/vet_treatment/?id={aid}')
        return render(request, 'VET/vet_prescribe.html', {'animal': animal})
    return redirect('/login/')

def vet_mark_adoption(request):
    aid = request.GET.get('id')
    animal = RescuedAnimal.objects.filter(id=aid).first()
    if animal:
        animal.marked_for_adoption_by_vet = True
        animal.status = 'ReadyForAdoption'
        animal.save()
        messages.success(request, "Marked as ready for adoption")
    return redirect('/vet_view_animals/')

# --- Care Center Views ---
def care_home(request):
    return render(request, 'CARE/care_home.html')

def care_view_pets(request):
    if 'profile_id' in request.session:
        center = CareCenter.objects.get(id=request.session['profile_id'])
        animals = RescuedAnimal.objects.filter(care_center=center)
        return render(request, 'CARE/care_view_pets.html', {'animals': animals})
    return redirect('/login/')

def care_log_activity(request):
    if 'profile_id' in request.session:
        aid = request.GET.get('id')
        animal = RescuedAnimal.objects.get(id=aid)
        center = CareCenter.objects.get(id=request.session['profile_id'])
        if request.method == 'POST':
            # ... (logic remains same)
            messages.success(request, f"{ltype} log added")
            return redirect('/care_view_pets/')
        meds = animal.medicines.all()
        foods = animal.food_prescriptions.all()
        logs = animal.care_logs.all()
        return render(request, 'CARE/care_log_activity.html', {'animal': animal, 'meds': meds, 'foods': foods, 'logs': logs})
    return redirect('/login/')

def care_list_adoption(request):
    aid = request.GET.get('id')
    animal = RescuedAnimal.objects.filter(id=aid).first()
    if animal:
        if animal.marked_for_adoption_by_vet:
            animal.listed_for_adoption = True
            animal.save()
            messages.success(request, "Listed for adoption")
        else:
            messages.error(request, "Need vet approval first")
    return redirect('/care_view_pets/')

def care_chat_vet(request):
    if 'profile_id' in request.session:
        center = CareCenter.objects.get(id=request.session['profile_id'])
        if request.method == 'POST':
            # ... (logic remains same)
            Chat.objects.create(care_center=center, vet_id=v_id, sender_type='care', message=msg)
        vets = Veterinarian.objects.filter(status='Approved')
        return render(request, 'CARE/care_chat_vet.html', {'vets': vets})
    return redirect('/login/')
