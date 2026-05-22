from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PasswordEntry
from .crypto import encrypt_password, decrypt_password, check_strength
import requests

# ── Auth Views ─────────────────────────────────────────────────

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm  = request.POST['confirm']
        if password != confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'vault/register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return render(request, 'vault/register.html')
        User.objects.create_user(username=username, password=password)
        messages.success(request, 'Account created! Please login.')
        return redirect('login')
    return render(request, 'vault/register.html')

def login_view(request):
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST['username'],
                            password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'vault/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ── Dashboard ──────────────────────────────────────────────────

@login_required
def dashboard(request):
    entries = PasswordEntry.objects.filter(user=request.user)
    decrypted = []
    for e in entries:
        try:
            pwd = decrypt_password(e.password)
            strength = check_strength(pwd)
        except Exception:
            pwd = '******'
            strength = {'label': 'Unknown', 'color': 'gray', 'percentage': 0}
        decrypted.append({
            'id':       e.id,
            'site':     e.site_name,
            'url':      e.site_url,
            'username': e.username,
            'password': pwd,
            'strength': strength,
            'notes':    e.notes,
        })
    weak_count   = sum(1 for d in decrypted if d['strength']['label'] in ['Weak','Very Weak'])
    strong_count = sum(1 for d in decrypted if d['strength']['label'] == 'Strong')
    return render(request, 'vault/dashboard.html', {
        'entries':      decrypted,
        'total':        len(decrypted),
        'weak_count':   weak_count,
        'strong_count': strong_count,
    })

# ── Add Password ───────────────────────────────────────────────

@login_required
def add_password(request):
    if request.method == 'POST':
        pwd = request.POST['password']
        PasswordEntry.objects.create(
            user      = request.user,
            site_name = request.POST['site_name'],
            site_url  = request.POST.get('site_url', ''),
            username  = request.POST['username'],
            password  = encrypt_password(pwd),
            notes     = request.POST.get('notes', ''),
        )
        messages.success(request, 'Password saved!')
        return redirect('dashboard')
    return render(request, 'vault/add_password.html')

# ── Delete Password ────────────────────────────────────────────

@login_required
def delete_password(request, pk):
    entry = get_object_or_404(PasswordEntry, pk=pk, user=request.user)
    entry.delete()
    messages.success(request, 'Entry deleted.')
    return redirect('dashboard')

# ── Password Generator ─────────────────────────────────────────

@login_required
def generate_password(request):
    import random, string
    length = int(request.GET.get('length', 16))
    chars  = string.ascii_letters + string.digits + "!@#$%^&*()"
    pwd    = ''.join(random.choices(chars, k=length))
    strength = check_strength(pwd)
    return render(request, 'vault/generate.html', {
        'password': pwd,
        'strength': strength,
    })

# ── Breach Check ───────────────────────────────────────────────

@login_required
def check_breach(request):
    result = None
    if request.method == 'POST':
        import hashlib
        pwd    = request.POST['password']
        sha1   = hashlib.sha1(pwd.encode()).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]
        resp   = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}')
        count  = 0
        for h in resp.text.splitlines():
            h_suffix, h_count = h.split(':')
            if h_suffix == suffix:
                count = int(h_count)
                break
        result = {
            'breached': count > 0,
            'count':    count,
            'password': pwd,
        }
    return render(request, 'vault/breach_check.html', {'result': result})  # ← return was missing
