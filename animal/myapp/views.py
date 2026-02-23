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
        animal = RescuedAnimal.objects.get(id=aid)
        vet = Veterinarian.objects.get(id=request.session['profile_id'])
        if request.method == 'POST':
            diag = request.POST.get('diagnosis')
            treat = request.POST.get('treatment')
            cond = request.POST.get('condition')
            
            MedicalRecord.objects.create(
                animal=animal,
                vet=vet,
                diagnosis=diag,
                treatment=treat,
                condition_after=cond
            )
            
            animal.condition = cond
            animal.save()
            
            messages.success(request, "Medical record added")
            return redirect(f'/vet_treatment/?id={aid}')
        return render(request, 'VET/vet_add_medical_record.html', {'animal': animal})
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
            v_id = request.POST.get('vet_id')
            msg = request.POST.get('message')
            Chat.objects.create(care_center=center, vet_id=v_id, sender_type='care', message=msg)
            messages.success(request, "Message sent")
        vets = Veterinarian.objects.filter(status='Approved')
        return render(request, 'CARE/care_chat_vet.html', {'vets': vets})
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

