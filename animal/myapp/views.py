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
        cert = request.FILES.get('certificate')
        if not Login.objects.filter(username=u).exists():
            user = Login.objects.create_user(username=u, password=p, usertype='vet', view_password=p)
            Veterinarian.objects.create(user=user, name=n, email=e, phone=ph, qualification=ql, experience=ex, image=img, certificate=cert)
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

def admin_view_rescue_teams(request):
    teams = RescueTeam.objects.all()
    return render(request, 'ADMIN/admin_view_rescue_teams.html', {'teams': teams})

def admin_view_vets(request):
    vets = Veterinarian.objects.all()
    return render(request, 'ADMIN/admin_view_vets.html', {'vets': vets})

def admin_view_users(request):
    users = UserProfile.objects.all()
    return render(request, 'ADMIN/admin_view_users.html', {'users': users})

def admin_approve_team(request):
    tid = request.GET.get('id')
    team = RescueTeam.objects.filter(id=tid).first()
    if team:
        team.status = 'Approved'
        team.save()
        messages.success(request, f"Approved {team.name}")
    
    referer = request.META.get('HTTP_REFERER')
    if referer and 'admin_view_rescue_teams' in referer:
        return redirect(referer)
    return redirect('/admin_manage_users/')

def admin_reject_team(request):
    tid = request.GET.get('id')
    team = RescueTeam.objects.filter(id=tid).first()
    if team:
        team.status = 'Rejected'
        team.save()
        messages.info(request, f"Rejected {team.name}")
    
    referer = request.META.get('HTTP_REFERER')
    if referer and 'admin_view_rescue_teams' in referer:
        return redirect(referer)
    return redirect('/admin_manage_users/')

def admin_approve_vet(request):
    vid = request.GET.get('id')
    vet = Veterinarian.objects.filter(id=vid).first()
    if vet:
        vet.status = 'Approved'
        vet.save()
        messages.success(request, f"Medical credentials authorized for {vet.name}")
    
    referer = request.META.get('HTTP_REFERER')
    if referer and 'admin_view_vets' in referer:
        return redirect(referer)
    return redirect('/admin_manage_users/')

def admin_reject_vet(request):
    vid = request.GET.get('id')
    vet = Veterinarian.objects.filter(id=vid).first()
    if vet:
        vet.status = 'Rejected'
        vet.save()
        messages.info(request, f"Application rejected for {vet.name}")
    
    referer = request.META.get('HTTP_REFERER')
    if referer and 'admin_view_vets' in referer:
        return redirect(referer)
    return redirect('/admin_manage_users/')

def admin_block_user(request):
    uid = request.GET.get('id')
    user = Login.objects.filter(id=uid).first()
    if user:
        user.is_active = False
        user.save()
        # Sync status on linked profile
        if hasattr(user, 'vet_profile'):
            user.vet_profile.status = 'Blocked'
            user.vet_profile.save()
        elif hasattr(user, 'rescue_profile'):
            user.rescue_profile.status = 'Blocked'
            user.rescue_profile.save()
        elif hasattr(user, 'care_profile'):
            user.care_profile.status = 'Blocked'
            user.care_profile.save()
        messages.info(request, f"Blocked account for {user.username}")
    
    # Redirect back to referring page or default
    referer = request.META.get('HTTP_REFERER')
    valid_referers = ['admin_manage_users', 'admin_manage_care_centers', 'admin_view_rescue_teams', 'admin_view_vets', 'admin_view_users']
    if referer and any(ref in referer for ref in valid_referers):
        return redirect(referer)
    return redirect('/admin_manage_users/')

def admin_unblock_user(request):
    uid = request.GET.get('id')
    user = Login.objects.filter(id=uid).first()
    if user:
        user.is_active = True
        user.save()
        # Sync status on linked profile
        if hasattr(user, 'vet_profile'):
            user.vet_profile.status = 'Approved'
            user.vet_profile.save()
        elif hasattr(user, 'rescue_profile'):
            user.rescue_profile.status = 'Approved'
            user.rescue_profile.save()
        elif hasattr(user, 'care_profile'):
            user.care_profile.status = 'Approved'
            user.care_profile.save()
        messages.success(request, f"Activated account for {user.username}")
    
    # Redirect back to referring page or default
    referer = request.META.get('HTTP_REFERER')
    valid_referers = ['admin_manage_users', 'admin_manage_care_centers', 'admin_view_rescue_teams', 'admin_view_vets', 'admin_view_users']
    if referer and any(ref in referer for ref in valid_referers):
        return redirect(referer)
    return redirect('/admin_manage_users/')

def admin_manage_care_centers(request):
    centers = CareCenter.objects.all()
    return render(request, 'ADMIN/admin_manage_care_centers.html', {'centers': centers})

def admin_add_care_center(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        n = request.POST.get('name')
        e = request.POST.get('email')
        ph = request.POST.get('phone')
        ad = request.POST.get('address')
        li = request.POST.get('license')
        img = request.FILES.get('image')
        
        user = Login.objects.create_user(username=u, password=p, usertype='careCenter', view_password=p)
        CareCenter.objects.create(user=user, name=n, email=e, phone=ph, address=ad, license_number=li, image=img, status='Approved')
        messages.success(request, "Care Center added successfully")
        return redirect('/admin_manage_care_centers/')
    return render(request, 'ADMIN/admin_add_care_center.html')

def admin_edit_care_center(request):
    cid = request.GET.get('id')
    center = CareCenter.objects.get(id=cid)
    if request.method == 'POST':
        center.name = request.POST.get('name')
        center.email = request.POST.get('email')
        center.phone = request.POST.get('phone')
        center.address = request.POST.get('address')
        center.license_number = request.POST.get('license')
        if request.FILES.get('image'):
            center.image = request.FILES.get('image')
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

def admin_reassign_vet(request):
    if 'role' in request.session and request.session['role'] == 'admin':
        aid = request.GET.get('id')
        animal = RescuedAnimal.objects.get(id=aid)
        vets = Veterinarian.objects.filter(status='Approved')
        if request.method == 'POST':
            v_id = request.POST.get('vet')
            vet = Veterinarian.objects.get(id=v_id)
            animal.assigned_vet = vet
            animal.save()
            messages.success(request, f"Medical oversight re-assigned to {vet.name}")
            return redirect('/admin_monitor_all/')
        return render(request, 'ADMIN/admin_reassign_vet.html', {'animal': animal, 'vets': vets})
    return redirect('/login/')

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
            category = request.POST.get('animal_type')
            desc = request.POST.get('description')
            loc = request.POST.get('location')
            img = request.FILES.get('image')
            profile = UserProfile.objects.get(id=request.session['profile_id'])
            
            RescueReport.objects.create(
                reported_by=profile,
                animal_type=category,
                description=desc,
                location_text=loc,
                photo=img
            )
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
    user_requests = {}
    if 'profile_id' in request.session:
        profile = UserProfile.objects.get(id=request.session['profile_id'])
        reqs = AdoptionRequest.objects.filter(user=profile)
        for r in reqs:
            user_requests[r.animal_id] = r
    return render(request, 'USER/user_request_adoption.html', {'animals': animals, 'user_requests': user_requests})

def user_animal_detail(request):
    aid = request.GET.get('id')
    animal = RescuedAnimal.objects.get(id=aid)
    records = animal.medical_records.all().order_by('-date')
    meds = animal.medicines.all()
    foods = animal.food_prescriptions.all()
    logs = animal.care_logs.all().order_by('-given_at')
    user_req = None
    if 'profile_id' in request.session:
        profile = UserProfile.objects.get(id=request.session['profile_id'])
        user_req = AdoptionRequest.objects.filter(user=profile, animal=animal).first()
    return render(request, 'USER/user_animal_detail.html', {
        'animal': animal, 
        'records': records, 
        'meds': meds, 
        'foods': foods, 
        'logs': logs,
        'user_req': user_req
    })

def user_submit_adoption(request):
    if 'profile_id' in request.session:
        aid = request.GET.get('id')
        profile = UserProfile.objects.get(id=request.session['profile_id'])
        animal = RescuedAnimal.objects.get(id=aid)
        existing = AdoptionRequest.objects.filter(user=profile, animal=animal).first()
        if existing:
            messages.warning(request, "You have already submitted an adoption request for this animal.")
        else:
            AdoptionRequest.objects.create(user=profile, animal=animal)
            messages.success(request, "Adoption request sent successfully!")
        return redirect('/user_request_adoption/')
    return redirect('/login/')

def user_cancel_adoption(request):
    if 'profile_id' in request.session:
        rid = request.GET.get('id')
        profile = UserProfile.objects.get(id=request.session['profile_id'])
        req = AdoptionRequest.objects.filter(id=rid, user=profile, status='Pending').first()
        if req:
            req.delete()
            messages.info(request, "Adoption request cancelled.")
        else:
            messages.error(request, "Request not found or already processed.")
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
        v_id = request.POST.get('vet')
        c_id = request.POST.get('care')
        
        vet = Veterinarian.objects.get(id=v_id)
        center = CareCenter.objects.get(id=c_id)
        
        # Safely create or update RescuedAnimal record
        RescuedAnimal.objects.update_or_create(
            rescue_report=report,
            defaults={
                'species': report.animal_type,
                'photo': report.photo,
                'assigned_vet': vet,
                'care_center': center,
                'status': 'UnderTreatment'
            }
        )
        
        report.status = 'Treated'
        report.save()
        
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
    records = animal.medical_records.all().order_by('-id')
    return render(request, 'VET/vet_treatment.html', {'animal': animal, 'records': records})

def vet_add_medical_record(request):
    if 'profile_id' in request.session:
        aid = request.GET.get('id')
        rid = request.GET.get('rid')
        animal = RescuedAnimal.objects.get(id=aid)
        vet = Veterinarian.objects.get(id=request.session['profile_id'])
        
        existing_record = None
        if rid:
            existing_record = MedicalRecord.objects.filter(id=rid).first()

        if request.method == 'POST':
            diag = request.POST.get('diagnosis')
            treat = request.POST.get('treatment')
            cond = request.POST.get('condition')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            
            if existing_record:
                existing_record.diagnosis = diag
                existing_record.treatment = treat
                existing_record.condition_after = cond
                existing_record.save()
                msg = "Medical record updated"
            else:
                MedicalRecord.objects.create(
                    animal=animal,
                    vet=vet,
                    diagnosis=diag,
                    treatment=treat,
                    condition_after=cond
                )
                msg = "Medical record added"
            
            animal.condition = cond
            if gender:
                animal.gender = gender
            if age:
                animal.age = age
            animal.save()
            
            messages.success(request, f"{msg} and bio data updated")
            return redirect(f'/vet_treatment/?id={aid}')
        return render(request, 'VET/vet_add_medical_record.html', {
            'animal': animal,
            'record': existing_record
        })
    return redirect('/login/')

def vet_prescribe(request):
    if 'profile_id' in request.session:
        aid = request.GET.get('id')
        animal = RescuedAnimal.objects.get(id=aid)
        vet = Veterinarian.objects.get(id=request.session['profile_id'])
        
        # Get existing protocols to allow editing
        existing_medicine = animal.medicines.first()
        existing_food = animal.food_prescriptions.first()
        
        if request.method == 'POST':
            ptype = request.POST.get('type')
            item = request.POST.get('item')
            freq = request.POST.get('freq')
            notes = request.POST.get('notes', '')
            
            if ptype == 'Medicine':
                dos = request.POST.get('dosage')
                dur = request.POST.get('duration')
                
                if existing_medicine:
                    existing_medicine.medicine_name = item
                    existing_medicine.dosage = dos
                    existing_medicine.frequency = freq
                    existing_medicine.duration = dur
                    existing_medicine.notes = notes
                    existing_medicine.vet = vet
                    existing_medicine.save()
                    msg = "Medication protocol updated"
                else:
                    PrescribedMedicine.objects.create(
                        animal=animal,
                        vet=vet,
                        medicine_name=item,
                        dosage=dos,
                        frequency=freq,
                        duration=dur,
                        notes=notes
                    )
                    msg = "Medication protocol established"
            else:
                qty = request.POST.get('quantity')
                
                if existing_food:
                    existing_food.food_type = item
                    existing_food.quantity = qty
                    existing_food.frequency = freq
                    existing_food.notes = notes
                    existing_food.vet = vet
                    existing_food.save()
                    msg = "Nutritional protocol updated"
                else:
                    PrescribedFood.objects.create(
                        animal=animal,
                        vet=vet,
                        food_type=item,
                        quantity=qty,
                        frequency=freq,
                        notes=notes
                    )
                    msg = "Nutritional protocol established"
            
            messages.success(request, msg)
            return redirect(f'/vet_treatment/?id={aid}')
            
        return render(request, 'VET/vet_prescribe.html', {
            'animal': animal,
            'existing_medicine': existing_medicine,
            'existing_food': existing_food
        })
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
            ltype = request.POST.get('log_type')
            desc = request.POST.get('description')
            
            from datetime import date
            CareLog.objects.create(
                animal=animal,
                care_center=center,
                log_type=ltype,
                description=desc,
                date=date.today()
            )
            
            messages.success(request, f"{ltype} log added")
            return redirect('/care_view_pets/')
        meds = animal.medicines.all()
        foods = animal.food_prescriptions.all()
        logs = animal.care_logs.all()
        return render(request, 'CARE/care_log_activity.html', {'animal': animal, 'meds': meds, 'foods': foods, 'logs': logs})
    return redirect('/login/')

def care_update_photo(request):
    if 'profile_id' in request.session:
        if request.method == 'POST':
            aid = request.POST.get('animal_id')
            animal = RescuedAnimal.objects.get(id=aid)
            center = CareCenter.objects.get(id=request.session['profile_id'])
            if animal.care_center == center:
                if 'photo' in request.FILES:
                    animal.photo = request.FILES['photo']
                    animal.save()
                    messages.success(request, f"Photo updated for {animal.name or animal.species}")
                else:
                    messages.error(request, "No photo was selected.")
            else:
                messages.error(request, "You do not have permission to update this animal.")
        return redirect('/care_view_pets/')
    return redirect('/login/')

def care_view_user_details(request):
    if 'profile_id' in request.session:
        uid = request.GET.get('id')
        user_profile = UserProfile.objects.get(id=uid)
        return render(request, 'CARE/care_view_user.html', {'applicant': user_profile})
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

def care_manage_adoptions(request):
    if 'profile_id' in request.session:
        center = CareCenter.objects.get(id=request.session['profile_id'])
        requests = AdoptionRequest.objects.filter(animal__care_center=center).order_by('-requested_at')
        return render(request, 'CARE/care_manage_adoptions.html', {'requests': requests})
    return redirect('/login/')

def care_approve_adoption(request):
    rid = request.GET.get('id')
    req = AdoptionRequest.objects.get(id=rid)
    req.status = 'Approved'
    req.save()
    
    animal = req.animal
    animal.status = 'Adopted'
    animal.save()
    
    # Reject other requests for the same animal
    AdoptionRequest.objects.filter(animal=animal, status='Pending').update(status='Rejected')
    
    messages.success(request, f"Adoption approved for {animal.name}")
    return redirect('/care_manage_adoptions/')

def care_reject_adoption(request):
    rid = request.GET.get('id')
    req = AdoptionRequest.objects.get(id=rid)
    req.status = 'Rejected'
    req.save()
    messages.info(request, "Adoption request rejected")
    return redirect('/care_manage_adoptions/')

def care_adoption_history(request):
    if 'profile_id' in request.session:
        center = CareCenter.objects.get(id=request.session['profile_id'])
        animals = RescuedAnimal.objects.filter(care_center=center, status='Adopted').order_by('-admitted_at')
        return render(request, 'CARE/care_history.html', {'animals': animals})
    return redirect('/login/')

def care_chat_vet(request):
    if 'profile_id' in request.session:
        center = CareCenter.objects.get(id=request.session['profile_id'])
        v_id = request.GET.get('id')
        
        if request.method == 'POST':
            target_v_id = request.POST.get('vet_id')
            msg = request.POST.get('message')
            Chat.objects.create(care_center=center, vet_id=target_v_id, sender_type='care', message=msg)
            return redirect(f'/care_chat_vet/?id={target_v_id}')
            
        vets = Veterinarian.objects.filter(status='Approved')
        chats = []
        selected_vet = None
        if v_id:
            selected_vet = Veterinarian.objects.filter(id=v_id).first()
            if selected_vet:
                chats = Chat.objects.filter(care_center=center, vet=selected_vet).order_by('sent_at')
            
        return render(request, 'CARE/care_chat_vet.html', {
            'vets': vets, 
            'chats': chats, 
            'selected_vet': selected_vet
        })
    return redirect('/login/')

def vet_chat_care(request):
    if 'profile_id' in request.session:
        vet = Veterinarian.objects.get(id=request.session['profile_id'])
        c_id = request.GET.get('id')
        
        if request.method == 'POST':
            target_c_id = request.POST.get('care_id')
            msg = request.POST.get('message')
            Chat.objects.create(vet=vet, care_center_id=target_c_id, sender_type='vet', message=msg)
            return redirect(f'/vet_chat_care/?id={target_c_id}')
            
        centers = CareCenter.objects.filter(status='Approved')
        chats = []
        selected_center = None
        if c_id:
            selected_center = CareCenter.objects.filter(id=c_id).first()
            if selected_center:
                chats = Chat.objects.filter(vet=vet, care_center=selected_center).order_by('sent_at')
            
        return render(request, 'VET/vet_chat_care.html', {
            'centers': centers, 
            'chats': chats, 
            'selected_center': selected_center
        })
    return redirect('/login/')

def admin_report(request):
    rescued = RescueReport.objects.filter(status__in=['Rescued', 'Closed']).count()
    treated = MedicalRecord.objects.count()
    adopted = RescuedAnimal.objects.filter(status='Adopted').count()
    return render(request, 'ADMIN/admin_report.html', {
        'rescued': rescued,
        'treated': treated,
        'adopted': adopted,
    })


# --- Profile Views ---

def user_profile(request):
    if 'profile_id' in request.session:
        profile = UserProfile.objects.get(id=request.session['profile_id'])
        if request.method == 'POST':
            profile.name = request.POST.get('name')
            profile.email = request.POST.get('email')
            profile.phone = request.POST.get('phone')
            profile.address = request.POST.get('address')
            if 'image' in request.FILES:
                profile.image = request.FILES['image']
            profile.save()
            messages.success(request, "Profile updated successfully")
            return redirect('/user_profile/')
        return render(request, 'USER/user_profile.html', {'profile': profile})
    return redirect('/login/')

def rescue_profile(request):
    if 'profile_id' in request.session:
        profile = RescueTeam.objects.get(id=request.session['profile_id'])
        if request.method == 'POST':
            profile.name = request.POST.get('name')
            profile.phone = request.POST.get('phone')
            profile.vehicle = request.POST.get('vehicle')
            profile.address = request.POST.get('address')
            if 'image' in request.FILES:
                profile.image = request.FILES['image']
            profile.save()
            messages.success(request, "Profile updated successfully")
            return redirect('/rescue_profile/')
        return render(request, 'RESCUE/rescue_profile.html', {'profile': profile})
    return redirect('/login/')

def vet_profile(request):
    if 'profile_id' in request.session:
        profile = Veterinarian.objects.get(id=request.session['profile_id'])
        if request.method == 'POST':
            profile.name = request.POST.get('name')
            profile.phone = request.POST.get('phone')
            profile.qualification = request.POST.get('qualification')
            profile.experience = request.POST.get('experience')
            if 'image' in request.FILES:
                profile.image = request.FILES['image']
            profile.save()
            messages.success(request, "Profile updated successfully")
            return redirect('/vet_profile/')
        return render(request, 'VET/vet_profile.html', {'profile': profile})
    return redirect('/login/')

def care_profile(request):
    if 'profile_id' in request.session:
        profile = CareCenter.objects.get(id=request.session['profile_id'])
        if request.method == 'POST':
            profile.name = request.POST.get('name')
            profile.phone = request.POST.get('phone')
            profile.address = request.POST.get('address')
            profile.license_number = request.POST.get('license_number')
            if 'image' in request.FILES:
                profile.image = request.FILES['image']
            profile.save()
            messages.success(request, "Profile updated successfully")
            return redirect('/care_profile/')
        return render(request, 'CARE/care_profile.html', {'profile': profile})
    return redirect('/login/')


# --- Appointment Views ---

def user_view_vets(request):
    """User browses approved vets to book an appointment."""
    if 'profile_id' not in request.session:
        return redirect('/login/')
    vets = Veterinarian.objects.filter(status='Approved')
    return render(request, 'USER/user_view_vets.html', {'vets': vets})


def user_book_appointment(request):
    """User fills in pet details and books an appointment with a chosen vet."""
    if 'profile_id' not in request.session:
        return redirect('/login/')

    vid = request.GET.get('vet_id') or request.POST.get('vet_id')
    vet = Veterinarian.objects.filter(id=vid, status='Approved').first()
    if not vet:
        messages.error(request, "Veterinarian not found.")
        return redirect('/user_view_vets/')

    if request.method == 'POST':
        profile = UserProfile.objects.get(id=request.session['profile_id'])
        pet_name    = request.POST.get('pet_name', '').strip()
        pet_species = request.POST.get('pet_species', '').strip()
        pet_breed   = request.POST.get('pet_breed', '').strip()
        pet_age     = request.POST.get('pet_age', '').strip()
        pet_gender  = request.POST.get('pet_gender', '').strip()
        pet_weight  = request.POST.get('pet_weight', '').strip()
        pet_symptoms = request.POST.get('pet_symptoms', '').strip()
        reason      = request.POST.get('reason', '').strip()
        pet_photo   = request.FILES.get('pet_photo')

        if not all([pet_name, pet_species, pet_age, pet_gender, pet_symptoms, reason]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'USER/user_book_appointment.html', {'vet': vet})

        VetAppointment.objects.create(
            user=profile,
            vet=vet,
            pet_name=pet_name,
            pet_species=pet_species,
            pet_breed=pet_breed,
            pet_age=pet_age,
            pet_gender=pet_gender,
            pet_weight=pet_weight,
            pet_symptoms=pet_symptoms,
            reason=reason,
            pet_photo=pet_photo,
        )
        messages.success(request, "Appointment request sent! Wait for the vet to confirm a date & time.")
        return redirect('/user_my_appointments/')

    return render(request, 'USER/user_book_appointment.html', {'vet': vet})


def user_my_appointments(request):
    """User views all their appointment requests and statuses."""
    if 'profile_id' not in request.session:
        return redirect('/login/')
    profile = UserProfile.objects.get(id=request.session['profile_id'])
    appointments = VetAppointment.objects.filter(user=profile).order_by('-requested_at')
    return render(request, 'USER/user_my_appointments.html', {'appointments': appointments})


def user_appointment_payment(request):
    """User makes payment for an accepted appointment."""
    if 'profile_id' not in request.session:
        return redirect('/login/')
    appt_id = request.GET.get('id')
    profile = UserProfile.objects.get(id=request.session['profile_id'])
    appt = VetAppointment.objects.filter(id=appt_id, user=profile, status='Accepted').first()
    if not appt:
        messages.error(request, "Appointment not found or not eligible for payment.")
        return redirect('/user_my_appointments/')

    if request.method == 'POST':
        card_name   = request.POST.get('card_name', '').strip()
        card_number = request.POST.get('card_number', '').strip()
        expiry      = request.POST.get('expiry', '').strip()
        cvv         = request.POST.get('cvv', '').strip()

        if not all([card_name, card_number, expiry, cvv]):
            messages.error(request, "Please fill in all payment details.")
            return render(request, 'USER/user_appointment_payment.html', {'appt': appt})

        # Simulate payment — generate a reference
        import uuid
        appt.payment_done = True
        appt.status = 'PaymentDone'
        appt.payment_reference = str(uuid.uuid4()).upper()[:12]
        appt.save()
        messages.success(request, f"Payment successful! Booking confirmed. Reference: {appt.payment_reference}")
        return redirect('/user_my_appointments/')

    return render(request, 'USER/user_appointment_payment.html', {'appt': appt})


# --- Vet appointment views ---

def vet_appointment_requests(request):
    """Vet views all appointment requests made to them."""
    if 'profile_id' not in request.session:
        return redirect('/login/')
    vet = Veterinarian.objects.get(id=request.session['profile_id'])
    appointments = VetAppointment.objects.filter(vet=vet).order_by('-requested_at')
    return render(request, 'VET/vet_appointment_requests.html', {'appointments': appointments})


def vet_accept_appointment(request):
    """Vet accepts an appointment and sets date, time, and fee."""
    if 'profile_id' not in request.session:
        return redirect('/login/')
    vet = Veterinarian.objects.get(id=request.session['profile_id'])
    appt_id = request.GET.get('id')
    appt = VetAppointment.objects.filter(id=appt_id, vet=vet, status='Pending').first()
    if not appt:
        messages.error(request, "Appointment not found.")
        return redirect('/vet_appointment_requests/')

    if request.method == 'POST':
        from datetime import date as dt_date, datetime
        appt_date_str = request.POST.get('appointment_date', '').strip()
        appt_time_str = request.POST.get('appointment_time', '').strip()
        fee_str       = request.POST.get('consultation_fee', '').strip()
        vet_notes     = request.POST.get('vet_notes', '').strip()

        if not appt_date_str or not appt_time_str or not fee_str:
            messages.error(request, "Please fill in date, time, and consultation fee.")
            return render(request, 'VET/vet_accept_appointment.html', {'appt': appt})

        try:
            appt_date = datetime.strptime(appt_date_str, '%Y-%m-%d').date()
            if appt_date < dt_date.today():
                messages.error(request, "Appointment date cannot be in the past.")
                return render(request, 'VET/vet_accept_appointment.html', {'appt': appt})
        except ValueError:
            messages.error(request, "Invalid date format.")
            return render(request, 'VET/vet_accept_appointment.html', {'appt': appt})

        try:
            fee = float(fee_str)
            if fee <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Please enter a valid consultation fee.")
            return render(request, 'VET/vet_accept_appointment.html', {'appt': appt})

        appt.appointment_date = appt_date
        appt.appointment_time = appt_time_str
        appt.consultation_fee = fee
        appt.vet_notes = vet_notes
        appt.status = 'Accepted'
        appt.save()
        messages.success(request, f"Appointment accepted for {appt.pet_name} on {appt_date}.")
        return redirect('/vet_appointment_requests/')

    return render(request, 'VET/vet_accept_appointment.html', {'appt': appt})


def vet_reject_appointment(request):
    """Vet rejects an appointment request."""
    if 'profile_id' not in request.session:
        return redirect('/login/')
    vet = Veterinarian.objects.get(id=request.session['profile_id'])
    appt_id = request.GET.get('id')
    appt = VetAppointment.objects.filter(id=appt_id, vet=vet, status='Pending').first()
    if not appt:
        messages.error(request, "Appointment not found.")
        return redirect('/vet_appointment_requests/')

    if request.method == 'POST':
        reason = request.POST.get('rejection_reason', '').strip()
        appt.rejection_reason = reason
        appt.status = 'Rejected'
        appt.save()
        messages.info(request, "Appointment request rejected.")
        return redirect('/vet_appointment_requests/')

    return render(request, 'VET/vet_reject_appointment.html', {'appt': appt})
