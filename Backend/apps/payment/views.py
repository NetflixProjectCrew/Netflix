import stripe
import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Payment, PaymentAttempt, Refund, WebhookEvent
from .serializers import (
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentAttemptSerializer,
    RefundSerializer,
    RefundCreateSerializer,
    StripeCheckoutSessionSerializer,
    PaymentStatusSerializer
)
from .services import StripeService, PaymentService, WebhookService
from apps.subscribe.models import SubscriptionPlan


class PaymentListView(generics.ListAPIView):
    """Список платежей пользователя"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает платежи текущего пользователя"""
        return Payment.objects.filter(
            user=self.request.user
        ).select_related('subscription', 'subscription__plan').order_by('-created_at')


class PaymentDetailView(generics.RetrieveAPIView):
    """Детальная информация о платеже"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает платежи текущего пользователя"""
        return Payment.objects.filter(
            user=self.request.user
        ).select_related('subscription', 'subscription__plan')
    

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_checkout_session(request):
    serializer = PaymentCreateSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    plan_id = serializer.validated_data['subscription_plan_id']  # type: ignore
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)

    success_url = serializer.validated_data.get(  # type: ignore
        'success_url', f"{settings.FRONTEND_URL}/subscribe?success=1&session_id={{CHECKOUT_SESSION_ID}}"
    )
    cancel_url = serializer.validated_data.get(  # type: ignore
        'cancel_url', f"{settings.FRONTEND_URL}/subscribe?canceled=1"
    )

    # 1) ищем «висящий» платёж (pending/processing)
    pending = Payment.objects.filter(
        user=user, status__in=['pending', 'processing']
    ).order_by('-created_at').first()

    if pending and pending.stripe_session_id:
        # Проверим сессию в Stripe: если она ещё "open" — вернём её URL с 409
        try:
            sess = stripe.checkout.Session.retrieve(pending.stripe_session_id)
            if sess.get('status') == 'open':
                return Response({
                    "detail": "User has pending payments. Please complete or cancel them first.",
                    "checkout_url": getattr(pending, 'checkout_url', None),  # если ты это поле хранишь
                    "session_id": pending.stripe_session_id,
                }, status=status.HTTP_409_CONFLICT)
        except Exception:
            pass
        # иначе снимем блокировку локально
        pending.status = 'canceled'
        pending.save(update_fields=['status'])

    # 2) создаём Payment + Subscription (ТОЛЬКО локально) — без внешних вызовов
    with transaction.atomic():
        payment, subscription = PaymentService.create_subscription_payment(user, plan)

    # 3) создаём Stripe-сессию (вне atomic)
    session_data = StripeService.create_checkout_session(payment, success_url, cancel_url)
    if not session_data:
        payment.status = 'failed'
        payment.save(update_fields=['status'])
        return Response({"error": "Failed to create checkout session"}, status=status.HTTP_400_BAD_REQUEST)

    # 4) сохраним данные сессии и отдадим фронту
    payment.stripe_session_id = session_data['session_id']
    # если хочешь хранить URL:
    # payment.checkout_url = session_data['checkout_url']
    payment.status = 'processing'
    payment.save(update_fields=['stripe_session_id', 'status'])

    return Response(session_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_pending_payment(request):
    """
    Отменяет последний pending/processing платёж текущего пользователя
    и истекает Stripe Checkout Session (если была).
    """
    p = (Payment.objects
         .filter(user=request.user, status__in=['pending', 'processing'])
         .order_by('-created_at')
         .first())

    if not p:
        # Нечего отменять — это ок
        return Response({"detail": "No pending payment."}, status=status.HTTP_200_OK)

    # Попробуем истечь checkout-сессию (без падений, если уже истекла)
    if p.stripe_session_id:
        try:
            stripe.checkout.Session.expire(p.stripe_session_id)
        except Exception:
            pass

    p.status = 'canceled'
    p.save(update_fields=['status'])
    return Response({"detail": "Pending payment canceled."}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_status(request, payment_id):
    """Проверяет статус платежа"""
    try:
        payment = get_object_or_404(
            Payment, 
            id=payment_id, 
            user=request.user
        )
        
        # Если есть session_id, проверяем статус в Stripe
        if payment.stripe_session_id and payment.status in ['pending', 'processing']:
            session_info = StripeService.retrieve_session(payment.stripe_session_id)
            
        if session_info:
            sess_status = session_info.get('status')           # open|complete|expired
            pay_status  = session_info.get('payment_status')   # paid|unpaid|no_payment_required

            if pay_status == 'paid':
                PaymentService.process_successful_payment(payment)
            elif sess_status == 'expired':
                PaymentService.process_failed_payment(payment, "Session expired")
        
        response_data = {
            'payment_id': payment.id, # type:ignore
            'status': payment.status,
            'message': f'Payment is {payment.status}',
            'subscription_activated': False
        }
        
        if payment.is_successful and payment.subscription:
            response_data['subscription_activated'] = payment.subscription.is_active
            response_data['message'] = 'Payment successful and subscription activated'
        
        serializer = PaymentStatusSerializer(response_data)
        return Response(serializer.data)
        
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_payment(request, payment_id):
    """Отменяет платеж"""
    try:
        payment = get_object_or_404(
            Payment, 
            id=payment_id, 
            user=request.user
        )
        
        if not payment.is_pending:
            return Response({
                'error': 'Can only cancel pending payments'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment.status = 'canceled'
        payment.save()
        
        # Отменяем подписку
        if payment.subscription:
            payment.subscription.cancel()
        
        return Response({
            'message': 'Payment canceled successfully'
        })
        
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_checkout(request):
    session_id = request.data.get('session_id')
    if not session_id:
        return Response({"detail": "session_id required"}, status=400)

    session = StripeService.retrieve_session(session_id)
    if not session:
        return Response({"detail": "Cannot retrieve session"}, status=400)

    # Нормализуем поля
    sess_status = session.get('status')                 # open|complete|expired
    pay_status  = session.get('payment_status') or session.get('paymentStatus')  # paid|unpaid|...

    if pay_status != 'paid':
        return Response({"detail": f"Payment not completed (status={pay_status}, session={sess_status})"}, status=400)

    # Достаём payment_id из metadata (смотри StripeService.create_checkout_session)
    meta = session.get('metadata') or {}
    payment_id = meta.get('payment_id')
    if not payment_id:
        return Response({"detail": "No payment_id in session metadata"}, status=400)

    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    ok = PaymentService.process_successful_payment(payment)
    return Response(
        {"detail": "Subscription activated" if ok else "Finalize failed"},
        status=200 if ok else 500
    )


class RefundListView(generics.ListAPIView):
    """Список возвратов для администраторов"""
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return Refund.objects.all().select_related(
            'payment', 'payment__user', 'created_by'
        ).order_by('-created_at')


class RefundDetailView(generics.RetrieveAPIView):
    """Детальная информация о возврате"""
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Refund.objects.all().select_related(
        'payment', 'payment__user', 'created_by'
    )


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def create_refund(request, payment_id):
    """Создает возврат для платежа"""
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        
        if not payment.can_be_refunded:
            return Response({
                'error': 'This payment cannot be refunded'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RefundCreateSerializer(
            data=request.data,
            context={'payment_id': payment_id}
        )
        
        if serializer.is_valid():
            with transaction.atomic():
                # Создаем возврат
                refund = serializer.save(
                    payment=payment,
                    created_by=request.user
                )
                
                # Обрабатываем возврат через Stripe
                success = StripeService.refund_payment(
                    payment, 
                    refund.amount, # type:ignore
                    refund.reason # type:ignore
                )
                
                if success:
                    refund.process_refund() # type:ignore
                    
                    # Если это полный возврат, отменяем подписку
                    if refund.amount == payment.amount and payment.subscription: # type:ignore
                        PaymentService.cancel_subscription(payment.subscription)
                    
                    response_serializer = RefundSerializer(refund)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    refund.status = 'failed' # type:ignore
                    refund.save() # type:ignore
                    return Response({
                        'error': 'Failed to process refund'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Webhook endpoint для Stripe"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # Верифицируем webhook
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Неверный payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError: # type:ignore
        # Неверная подпись
        return HttpResponse(status=400)
    
    # Обрабатываем событие
    success = WebhookService.process_stripe_webhook(event)
    
    if success:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)
    

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def payment_analytics(request):
    """Аналитика по платежам для администраторов"""
    from django.db.models import Count, Sum, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    # Общая статистика
    total_payments = Payment.objects.count()
    successful_payments = Payment.objects.filter(status='succeeded').count()
    total_revenue = Payment.objects.filter(
        status='succeeded'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Статистика за последний месяц
    last_month = timezone.now() - timedelta(days=30)
    monthly_payments = Payment.objects.filter(
        created_at__gte=last_month,
        status='succeeded'
    )
    monthly_revenue = monthly_payments.aggregate(
        total=Sum('amount')
    )['total'] or 0
    monthly_count = monthly_payments.count()
    
    # Средний чек
    avg_payment = Payment.objects.filter(
        status='succeeded'
    ).aggregate(avg=Avg('amount'))['avg'] or 0
    
    # Статистика по подпискам
    active_subscriptions = Payment.objects.filter(
        status='succeeded',
        subscription__status='active'
    ).count()
    
    return Response({
        'total_payments': total_payments,
        'successful_payments': successful_payments,
        'success_rate': (successful_payments / total_payments * 100) if total_payments > 0 else 0,
        'total_revenue': float(total_revenue),
        'monthly_revenue': float(monthly_revenue),
        'monthly_payments': monthly_count,
        'average_payment': float(avg_payment),
        'active_subscriptions': active_subscriptions,
        'period': {
            'from': last_month.isoformat(),
            'to': timezone.now().isoformat()
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_payment_history(request):
    """История платежей пользователя"""
    payments = Payment.objects.filter(
        user=request.user
    ).select_related('subscription', 'subscription__plan').order_by('-created_at')
    
    serializer = PaymentSerializer(payments, many=True)
    return Response({
        'count': payments.count(),
        'results': serializer.data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def retry_payment(request, payment_id):
    """Повторная попытка оплаты"""
    try:
        payment = get_object_or_404(
            Payment, 
            id=payment_id, 
            user=request.user,
            status='failed'
        )
        
        # Создаем новую сессию для повторной оплаты
        success_url = request.data.get(
            'success_url', 
            f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        )
        cancel_url = request.data.get(
            'cancel_url', 
            f"{settings.FRONTEND_URL}/payment/cancel"
        )
        
        session_data = StripeService.create_checkout_session(
            payment, success_url, cancel_url
        )
        
        if session_data:
            # Обновляем статус платежа
            payment.status = 'processing'
            payment.save()
            
            response_serializer = StripeCheckoutSessionSerializer(session_data)
            return Response(response_serializer.data)
        else:
            return Response({
                'error': 'Failed to create checkout session'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found or cannot be retried'
        }, status=status.HTTP_404_NOT_FOUND)    