from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Event, EventParticipant, ActivityParticipant
from .forms import EventForm, EventParticipantForm, ActivityParticipantForm


@login_required
def event_list(request):
    """
    Menampilkan daftar semua event dengan filter dan search.
    """
    events = Event.objects.all().order_by('-created_at')
    
    # Filter berdasarkan tipe
    tipe = request.GET.get('tipe')
    if tipe:
        events = events.filter(tipe=tipe)
    
    # Filter berdasarkan status
    status = request.GET.get('status')
    if status:
        events = events.filter(status=status)
    
    # Search berdasarkan nama atau lokasi
    search = request.GET.get('search')
    if search:
        events = events.filter(
            Q(name__icontains=search) | Q(lokasi__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'events': page_obj.object_list,
        'total_events': paginator.count,
    }
    return render(request, "activity/index.html", context)


@login_required
def event_detail(request, pk):
    """
    Menampilkan detail event dan mengelola peserta.
    """
    event = get_object_or_404(Event, pk=pk)
    
    # Update status event otomatis
    event.update_status()
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Detail event berhasil diperbarui.')
            return redirect('event_detail', pk=event.pk)
        else:
            messages.error(request, 'Ada kesalahan. Periksa kembali data Anda.')
    else:
        form = EventForm(instance=event)
    
    # Ambil peserta event
    if event.tipe == 'acara':
        # Untuk Acara: tampilkan panitia
        participants = EventParticipant.objects.filter(event=event).select_related('user', 'role')
        participant_type = 'panitia'
    else:
        # Untuk Kegiatan: tampilkan peserta
        participants = ActivityParticipant.objects.filter(event=event).select_related('user', 'unit')
        participant_type = 'peserta'
    
    context = {
        'event': event,
        'form': form,
        'participants': participants,
        'participant_type': participant_type,
    }
    return render(request, "activity/detail.html", context)


@login_required
def event_add(request):
    """
    Membuat event baru.
    """
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f"Event '{event.name}' berhasil ditambahkan.")
            return redirect('event_detail', pk=event.pk)
        else:
            messages.error(request, 'Ada kesalahan. Periksa kembali data Anda.')
    else:
        form = EventForm()
    
    context = {'form': form}
    return render(request, 'activity/event_add.html', context)


@login_required
def event_edit(request, pk):
    """
    Mengedit event yang sudah ada.
    """
    event = get_object_or_404(Event, pk=pk)
    
    # Cek permission: hanya created_by yang bisa edit
    if request.user != event.created_by and not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki izin untuk mengedit event ini.')
        return redirect('event_detail', pk=event.pk)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event berhasil diperbarui.')
            return redirect('event_detail', pk=event.pk)
        else:
            messages.error(request, 'Ada kesalahan. Periksa kembali data Anda.')
    else:
        form = EventForm(instance=event)
    
    context = {'event': event, 'form': form}
    return render(request, 'activity/edit.html', context)


@login_required
def event_delete(request, pk):
    """
    Menghapus event dan semua data terkait.
    """
    event = get_object_or_404(Event, pk=pk)
    
    # Cek permission: hanya created_by yang bisa delete
    if request.user != event.created_by and not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki izin untuk menghapus event ini.')
        return redirect('event_detail', pk=event.pk)
    
    if request.method == 'POST':
        event_name = event.name
        
        # Hapus semua peserta/panitia terkait
        EventParticipant.objects.filter(event=event).delete()
        ActivityParticipant.objects.filter(event=event).delete()
        
        # Hapus event
        event.delete()
        
        messages.success(request, f"Event '{event_name}' berhasil dihapus.")
        return redirect('event_list')
    
    context = {'event': event}
    return render(request, 'activity/delete_confirm.html', context)


# ============================================================
# Views untuk EventParticipant (Panitia Acara)
# ============================================================

@login_required
def event_participant_add(request, event_pk):
    """
    Menambah peserta/panitia ke event (untuk Acara).
    """
    event = get_object_or_404(Event, pk=event_pk)
    
    # Validasi: event harus tipe 'acara'
    if event.tipe != 'acara':
        messages.error(request, 'Event ini bukan tipe Acara.')
        return redirect('event_detail', pk=event.pk)
    
    if request.method == 'POST':
        form = EventParticipantForm(request.POST, event=event)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.event = event
            participant.save()
            messages.success(request, f"'{participant.user}' berhasil ditambahkan sebagai panitia.")
            return redirect('event_detail', pk=event.pk)
        else:
            messages.error(request, 'Ada kesalahan. Periksa kembali data Anda.')
    else:
        form = EventParticipantForm(event=event)
    
    context = {'event': event, 'form': form}
    return render(request, 'activity/participant_add.html', context)


@login_required
def event_participant_delete(request, pk):
    """
    Menghapus peserta/panitia dari event.
    """
    participant = get_object_or_404(EventParticipant, pk=pk)
    event_pk = participant.event.pk
    user_name = participant.user.username
    
    if request.method == 'POST':
        participant.delete()
        messages.success(request, f"'{user_name}' berhasil dihapus dari panitia.")
        return redirect('event_detail', pk=event_pk)
    
    context = {'participant': participant}
    return render(request, 'activity/participant_delete_confirm.html', context)


# ============================================================
# Views untuk ActivityParticipant (Peserta Kegiatan)
# ============================================================

@login_required
def activity_participant_add(request, event_pk):
    """
    Menambah peserta ke kegiatan (untuk Kegiatan).
    """
    event = get_object_or_404(Event, pk=event_pk)
    
    # Validasi: event harus tipe 'kegiatan'
    if event.tipe != 'kegiatan':
        messages.error(request, 'Event ini bukan tipe Kegiatan.')
        return redirect('event_detail', pk=event.pk)
    
    if request.method == 'POST':
        form = ActivityParticipantForm(request.POST, event=event)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.event = event
            participant.save()
            
            participant_name = participant.user.username if participant.user else f"Unit: {participant.unit.name}"
            messages.success(request, f"'{participant_name}' berhasil ditambahkan sebagai peserta.")
            return redirect('event_detail', pk=event.pk)
        else:
            messages.error(request, 'Ada kesalahan. Periksa kembali data Anda.')
    else:
        form = ActivityParticipantForm(event=event)
    
    context = {'event': event, 'form': form}
    return render(request, 'activity/participant_add.html', context)


@login_required
def activity_participant_edit(request, pk):
    """
    Mengedit status kehadiran peserta.
    """
    participant = get_object_or_404(ActivityParticipant, pk=pk)
    event_pk = participant.event.pk
    
    if request.method == 'POST':
        form = ActivityParticipantForm(request.POST, instance=participant, event=participant.event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Status peserta berhasil diperbarui.')
            return redirect('event_detail', pk=event_pk)
        else:
            messages.error(request, 'Ada kesalahan. Periksa kembali data Anda.')
    else:
        form = ActivityParticipantForm(instance=participant, event=participant.event)
    
    context = {'participant': participant, 'form': form, 'event_pk': event_pk}
    return render(request, 'activity/participant_edit.html', context)


@login_required
def activity_participant_delete(request, pk):
    """
    Menghapus peserta dari kegiatan.
    """
    participant = get_object_or_404(ActivityParticipant, pk=pk)
    event_pk = participant.event.pk
    participant_name = participant.user.username if participant.user else f"Unit: {participant.unit.name}"
    
    if request.method == 'POST':
        participant.delete()
        messages.success(request, f"'{participant_name}' berhasil dihapus dari peserta.")
        return redirect('event_detail', pk=event_pk)
    
    context = {'participant': participant}
    return render(request, 'activity/participant_delete_confirm.html', context)