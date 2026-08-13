from django.contrib.admin.utils import construct_change_message
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import title
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Comment


def product_detail(request, external_id, slug):
    product = get_object_or_404(Product, external_id=external_id)
    comments = product.comments.filter(is_visible=True).order_by('-date_added')
    return render(request, 'product/product_detail.html', {'product': product, 'comments': comments})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'product/shop.html', {'products': products})

@login_required()
@require_POST
def add_comment(request):
    external_id = request.POST.get('external_id')
    if not external_id:
        return JsonResponse({'success': False, 'error': 'Product ID is required!'}, status=400)

    product = Product.objects.filter(external_id=external_id).first()
    if not product:
        return JsonResponse({'success': False, 'error': 'Product not found!'}, status=404)

    text = request.POST.get('text')
    if not text:
        return JsonResponse({'success': False, 'error': 'Comment text is required!'}, status=400)

    comment = Comment.objects.create(product=product, user=request.user, text=text)

    return JsonResponse({
        'success': True,
        'id': comment.id,
        'text': comment.text,
        'date': comment.last_modified.strftime('%d %b %Y'),
        'comment_count': product.comments.count(),
    })


@login_required()
@require_POST
def delete_comment(request):
    comment_id = request.POST.get('comment_id')
    if not comment_id:
        return JsonResponse({'success': False, 'error': 'Comment ID is required!'}, status=400)

    comment = Comment.objects.filter(id=comment_id).first()
    if not comment:
        return JsonResponse({'success': False, 'error': 'Comment not found!'}, status=404)

    if request.user != comment.user:
        return JsonResponse({'success': False, 'error': 'You are not allowed to delete comment!'}, status=403)

    comment.is_visible = False
    comment.save()

    return JsonResponse({
        'success': True,
        'id': comment.id,
        'comment_count': comment.product.comments.filter(is_visible=True).count(),
    })


@require_POST
@login_required()
def edit_comment(request):
    comment_id = request.POST.get('comment_id')
    if not comment_id:
        return JsonResponse({'success': False, 'error': 'Comment ID is required!'}, status=400)

    comment_text = request.POST.get('text')
    if not comment_text:
        return JsonResponse({'success': False, 'error': 'Comment text is required!'}, status=400)

    comment = Comment.objects.filter(id=comment_id).first()
    if not comment:
        return JsonResponse({'success': False, 'error': 'Comment not found!'}, status=404)

    if request.user != comment.user:
        return JsonResponse({'success': False, 'error': 'You are not allowed to edit comment!'}, status=403)

    comment.text = comment_text
    comment.save()

    return JsonResponse({
        'success': True,
        'id': comment.id,
        'last_modified': comment.last_modified.strftime('%d %b %Y'),
        'text': comment.text,
    })
