import stripe
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from typing import Optional, Dict, Tuple
import logging

from .models import Payment, PaymentAttempt, WebhookEvent
from apps.subscribe.models import Subscription, SubscriptionPlan, SubscriptionHistory

logger = logging.getLogger(__name__)

# Stripe settings
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Сервис для работы с Stripe"""

    @staticmethod
    def create_customer(user) -> Optional[str]:
        """Создает клиента в Stripe"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.username,
                metadata= {
                    'user_id': user.id,
                    'username': user.username
                }
            )
            return customer.id
        except stripe.error.StripeError as e: # type: ignore
            logger.error(f"Error creating Stripe customer: {e}")
            return None
        except stripe.error.CardError as e: # type: ignore
            logger.error(f"Error with a card : {e}")
            return None
        except stripe.error.RateLimitError as e: # type: ignore
            logger.error(f"Authentication with Stripe's API failed: {e}")
            return None
        except stripe.error.InvalidRequestError as e: # type: ignore
            logger.error(f"Invalid parameters were supplied to Stripe's API: {e}")
            return None
        except stripe.error.AuthenticationError as e: # type: ignore
            logger.error(f"Authentication with Stripe's API failed: {e}")
            return None
        except stripe.error.APIConnectionError as e: # type: ignore
            logger.error(f"Network communication with Stripe failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Not related to Stripe error: {e}")
            return None
        
    @staticmethod
    def create_checkout_session(payment: Payment, success_url: str, cancel_url:str) -> Optional[dict]:
        """Создает сессию Stripe Checkout"""
        try:
            # Получаем / создаем клиента
            if not payment.stripe_customer_id:
                customer_id = StripeService.create_customer(payment.user)
                if customer_id:
                    payment.stripe_customer_id = customer_id
                    payment.save()
            
            session = stripe.checkout.Session.create(
                customer=payment.stripe_customer_id,    #type: ignore
                payment_method_types=['card'],
                line_items=[{
                    'price_data':{
                        'currency':payment.currency.lower(),
                        'product_data': {
                            'name': f"Subscriprion - {payment.subscription.plan.name}", #type: ignore
                            'description': payment.description, # type: ignore
                        },
                        'unit_amount': int(payment.amount * 100), # в центах
                    },
                    'quantity':1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'payment_id': payment.id, #type: ignore
                    'user_id': payment.user.id,
                    'subscription_id': payment.subscription.id if payment.subscription else None #type: ignore
                }
            )

            # Update payment
            payment.stripe_session_id = session.id
            payment.status = 'processing'
            payment.save()

            return {
                'checkout_url': session.url,
                'session_id': session.id,
                'payment_id': payment.id #type: ignore
            }
        except stripe.error.StripeError as e: #type: ignore
            logger.error(f'Error creating checkout session: {e}')
            payment.mark_as_failed(str(e))
            return None
    

    @staticmethod
    def create_payment_intent(payment:Payment) -> Optional[str]:
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount*100), # В центах
                currency=payment.currency.lower(),
                customer=payment.stripe_customer_id, # type: ignore
                metadata={
                    'payment_id': payment.id, #type:ignore
                    'user_id': payment.user.id,
                    'subscription_id': payment.subscription.id if payment.subscription else None #type: ignore
                }
            )
        
            payment.stripe_payment_intent_id = intent.id
            payment.save()

            return intent.client_secret
        
        except stripe.error.StripeError as e: #type: ignore
            logger.error(f'Error creating payment intent: {e}')
            payment.mark_as_failed(str(e))
            return None
        
    @staticmethod
    def refund_payment(payment:Payment, amount: Optional[Decimal] = None, reason:str = '') -> bool:
        """ Возвращает платеж через Stripe"""
        try:
            if not payment.stripe_payment_intent_id:
                return False
            refund_data = {
                'payment_intent': payment.stripe_payment_intent_id,
                'metadata': {
                    'payment_id': payment.id, #type: ignore
                    'reason': reason
                }
            }

            if amount:
                refund_data['amount'] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_data)

            return refund.status == "succeeded"
        
        except stripe.error.StripeError as e: #type: ignore
            logger.error(f'Error proccessing refund: {e}')
            return False
    
    @staticmethod
    def retrieve_session(session_id:str)-> Optional[Dict]:
        """Получает информацию о сессии"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'status': session.payment_status,
                'payment_intent': session.payment_intent,
                'customer': session.customer,
                'metadata': session.metadata
            }
        except stripe.error.StripeError as e: #type: ignore
            logger.error(f'Error retrieving session: {e}')
            return None
        


class PaymentService:
    """Основной сервис для работы с платежами"""