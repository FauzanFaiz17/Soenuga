from django.shortcuts import render, redirect, get_object_or_404
from .models import Inventory, FotoInventory
from .forms import InventoryForm, MultiFotoForm

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.core.paginator import Paginator
from django.db.models import Q


# =========================
# List + Search + Pagination
# =========================
def inventaris_list(request):

    query = request.GET.get('search', '')

    inventory_list = Inventory.objects.all().order_by('-tanggal')

    if query:
        inventory_list = inventory_list.filter(
            Q(nama__icontains=query) |
            Q(keterangan__icontains=query) |
            Q(tipe__icontains=query)
        )

    paginator = Paginator(inventory_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventory/index.html', {
        'inventories': page_obj,
        'search_query': query,
    })


# =========================
# Add Inventory
# =========================
def inventaris_add(request):

    inventory_form = InventoryForm(request.POST or None)
    foto_form = MultiFotoForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':

        if inventory_form.is_valid():

            inventory = inventory_form.save()

            # simpan foto
            files = request.FILES.getlist('foto')

            for f in files:
                FotoInventory.objects.create(
                    inventory=inventory,
                    foto=f
                )

            messages.success(request, 'Inventaris berhasil disimpan.')
            return redirect('inventory')


    context = {
        'inventory_form': inventory_form,
        'foto_form': foto_form,
    }

    return render(request, 'inventory/add_inventory.html', context)


# =========================
# Update Inventory
# =========================
def inventory_update(request, pk):

    inventory = get_object_or_404(Inventory, pk=pk)

    inventory_form = InventoryForm(
        request.POST or None,
        instance=inventory
    )

    foto_form = MultiFotoForm(
        request.POST or None,
        request.FILES or None
    )


    if request.method == 'POST':

        if inventory_form.is_valid():

            inventory = inventory_form.save()

            # simpan foto baru (jika ada)
            files = request.FILES.getlist('foto')

            for f in files:
                FotoInventory.objects.create(
                    inventory=inventory,
                    foto=f
                )

            messages.success(request, 'Inventaris berhasil diperbarui.')
            return redirect('inventory')


    context = {
        'inventory_form': inventory_form,
        'foto_form': foto_form,
        'inventory': inventory,
    }

    return render(request, 'inventory/update_inventory.html', context)


# =========================
# Delete Foto (AJAX)
# =========================
@csrf_exempt
def delete_foto(request, pk):

    if (
        request.method == 'POST'
        and request.headers.get('x-requested-with') == 'XMLHttpRequest'
    ):
        try:
            foto = FotoInventory.objects.get(pk=pk)
            foto.delete()

            return JsonResponse({'success': True})

        except FotoInventory.DoesNotExist:

            return JsonResponse({
                'success': False,
                'error': 'Foto tidak ditemukan'
            })

    return JsonResponse({
        'success': False,
        'error': 'Permintaan tidak valid'
    })


# =========================
# Delete Inventory
# =========================
def delete_inventory(request, pk):

    inventory = get_object_or_404(Inventory, pk=pk)

    if request.method == 'POST':

        inventory.delete()

        messages.success(request, 'Inventaris berhasil dihapus.')

        return redirect('inventory')


    messages.error(request, 'Metode tidak diizinkan.')
    return redirect('inventory')
