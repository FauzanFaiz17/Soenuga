from django.shortcuts import render, redirect, get_object_or_404
from .models import Correspondence
from django.contrib import messages
from .forms import CorrespondenceForm
from django.core.paginator import Paginator
from django.db.models import Q


def surat(request):
    query = request.GET.get('search', '')
    surats = Correspondence.objects.all().order_by('-tanggal')

    if query:
        surats = surats.filter(
            Q(nomor__icontains=query) |
            Q(perihal__icontains=query) |
            Q(jenis__icontains=query) |
            Q(keterangan__icontains=query) |
            Q(pengirim__icontains=query) |
            Q(tanggal__icontains=query) 
        )

    paginator = Paginator(surats, 10)  # 10 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'correspondence/index.html', {
        'surats': page_obj,
        'search_query': query,
        })

def correspondence_create(request):
    if request.method == 'POST':
        form = CorrespondenceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Surat berhasil ditambahkan.")
            return redirect('surat')
    else:
        form = CorrespondenceForm()
    return render(request, 'correspondence/add.html', {'form': form})

def update_correspondence(request, pk):
    surat = get_object_or_404(Correspondence, pk=pk)

    if request.method == 'POST':
        form = CorrespondenceForm(request.POST, request.FILES, instance=surat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data surat berhasil diperbarui.')
            return redirect('surat') 
        else:
            messages.error(request, 'Terjadi kesalahan saat memperbarui data surat.')
    else:
        form = CorrespondenceForm(instance=surat)

    context = {
        'form': form,
        'title': 'Perbarui Surat',
        'submit_text': 'Update Surat'
    }

    return render(request, 'correspondence/update.html', context)


def delete_correspondence(request, pk):
    correspondence = get_object_or_404(Correspondence, pk=pk)

    if request.method == 'POST':
        correspondence.delete()  # Ini akan otomatis menghapus foto terkait jika pakai on_delete=CASCADE
        messages.success(request, 'Data Surat berhasil dihapus.')
        return redirect('surat')  

    messages.error(request, 'Metode tidak diizinkan.')
    return redirect('surat')


def tambah_surat_keluar(request):
    if request.method == 'POST':
        form = CorrespondenceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('daftar_surat')
    else:
        form = CorrespondenceForm()
    return render(request, 'surat/tambah.html', {'form': form})
