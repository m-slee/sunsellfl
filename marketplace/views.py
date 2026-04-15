from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator
from django.views.generic.edit import CreateView
from .models import Listing, ForSaleSubCategory, FL_CITIES, ListingCategory, ForSaleSubCategory, Reply, ListingImage
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.contrib.messages.views import SuccessMessageMixin
from users.models import User
from .forms import ContactForm
from urllib.parse import urlencode
from django.contrib import messages
import stripe
import classifieds.settings as settings
from django.urls import reverse 
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
import json

class Tabs:
    INFO = 'info'
    LISTINGS = 'listings'
    MESSAGES = 'messages'

PRICE_RANGES = {
    "all": "all",
    "10-20": (10, 20),
    "20-50": (20, 50),
    "50-100": (50, 100),
    "over 100": (100, "+"),
    "free": "free"
}


class HomePageView(TemplateView):
    template_name = "marketplace/index.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the default context
        context = super().get_context_data(**kwargs)

        # categories = [choice[1] for choice in ForSaleSubCategory.choices]
        categories = ForSaleSubCategory.choices
        # print("Categories:", categories)
        # Add your own context variables
        context["categories"] = categories
        
        return context

class AboutPageView(TemplateView):
    template_name = "marketplace/about.html"

class LegalPageView(TemplateView):
    template_name = "marketplace/legal.html"

class ContactPageView(FormView):
    template_name = "marketplace/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy('marketplace:contact_success')

    def form_valid(self, form):
        # Called when valid data is submitted
        form.send_email()
        return super().form_valid(form)

class ContactSuccessView(TemplateView):
    template_name = "marketplace/contact_success.html"

class ListingsPageView(ListView):
    model = Listing
    template_name = "marketplace/listings.html"
    context_object_name = "listings"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = ForSaleSubCategory.choices
        # context["selected_category"] = self.kwargs.get('category', ForSaleSubCategory.GENERAL) 
        context["selected_category"] = self.kwargs.get('category', "all") 
        context["categories"] = categories
        context["price_ranges"] = PRICE_RANGES
        context["cities"] = ["All Cities"] + FL_CITIES

        search = self.request.GET.get('search', '')
        if search:
            context['search'] = search

        date_order = self.request.GET.get('date_order', '')
        if date_order:
            context['date_order'] = date_order

        price = self.request.GET.get('price', '')
        if price:
            context['price'] = price

        city = self.request.GET.get('city', '')
        if city:
            context['city'] = city
        return context

    def get_queryset(self):
        category_slug = self.kwargs.get('category')
        search = self.request.GET.get('search', '')
        date_order = self.request.GET.get('date_order', '')
        price = self.request.GET.get('price', '')
        city = self.request.GET.get('city', '')

        # listings =  Listing.objects.all().order_by('-date_posted')
        listings =  Listing.objects.filter(paid_for=True)
        if search:
            print("Filtering by search:", search)
            # listings = listings.filter(title__icontains=search).order_by('-date_posted')
            listings = listings.filter(title__icontains=search)

        if date_order == 'newest':
            print("Ordering by newest")
            listings = listings.order_by('-date_posted')
        elif date_order == 'oldest':
            print("Ordering by oldest")
            listings = listings.order_by('date_posted')
        else:
            listings = listings.order_by('-date_posted')

        if category_slug and category_slug != "all":
            print("Filtering by category:", category_slug)
            # return Listing.objects.filter(subcategory=category_slug).order_by('-date_posted')
            # return listings.filter(subcategory=category_slug).order_by('-date_posted')
            listings = listings.filter(subcategory=category_slug)
        
        if price and not price == "all":
            price_range = PRICE_RANGES[price]
            print("Filtering by price range:", price_range)
            if price == "over 100":
                listings = listings.filter(price__gt=price_range[0])
            elif price == "free":
                listings = listings.filter(price=0)
            else:
                min_price = price_range[0]
                max_price = price_range[1]
                listings = listings.filter(price__gte=min_price, price__lte=max_price)

        if city and city != "All Cities":
            print("Filtering by city:", category_slug)
            listings = listings.filter(city=city)

        return listings

class ListingDetailView(TemplateView):
    template_name = "marketplace/listing_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listing_id = self.kwargs.get('pk')
        context['listing'] = Listing.objects.get(id=listing_id)
        return context

# class ListingPaymentSuccess(TemplateView):
#     template_name = "marketplace/payment_success.html"

def stripe_success(request):
    listing_id = request.GET.get('listing_id')
    if listing_id:
        # Redirect to the listing detail page (or account page)
        messages.success(request, "Listing created successfully. It is now live.")
        return redirect(reverse('marketplace:listing_detail', kwargs={'pk': listing_id}))
    # Fallback: go to account page
    return redirect(reverse('marketplace:account'))

# webhook view
@csrf_exempt
def stripe_webhook(request):
    print("Handling stipe webhook.")
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        return HttpResponseBadRequest("Invalid payload")
    except stripe.error.SignatureVerificationError:
        return HttpResponseForbidden("Invalid signature")
    print("Event constructed.")

    print(f"Event type: {event['type']}")
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        print("handling checkout completed.")
        session = event['data']['object']
        # Optional: retrieve full session if you need expanded fields
        # session = stripe.checkout.Session.retrieve(session['id'], expand=['payment_intent'])

        # listing_id = session.get('metadata', {}).get('listing_id')
        # if isinstance(session, dict):
        #     metadata = session.get('metadata') or {}
        # else:
        #     metadata = getattr(session, 'metadata', {}) or {}
        # listing_id = metadata.get('listing_id') if isinstance(metadata, dict) else None
        listing_id = session["metadata"]["listing_id"]
        # print(f"session: {session}")
        print(f"listing_id: {listing_id}")

        if listing_id:
            print(f"Setting listing {listing_id} as paid.")
            try:
                listing = Listing.objects.get(id=listing_id)
                listing.paid_for = True
                # listing.is_active = True
                listing.save()
                # Optionally: send notification email, decrement counters, etc.
            except Listing.DoesNotExist:
                pass

    # Return 200 to acknowledge receipt of the event
    return HttpResponse(status=200)

class CreateListingView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Listing
    template_name = "marketplace/create_listing.html"
    # fields = ['title', 'description', 'category', 'subcategory', 'price', 'city', 'image', 'email', 'phone']
    fields = ['title', 'description', 'category', 'subcategory', 'price', 'city', 'email', 'phone']
    success_url = '/account/'
    success_message = "Your listing was created successfully. It is now live and potential buyers may contact you."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = FL_CITIES
        context['subcategories'] = ForSaleSubCategory.choices
        return context

    def form_valid(self, form):
        print("Creating new listing.")
        user = User.objects.get(id=self.request.user.id)
        form.instance.user = user

        # If user has a free post, consume it and publish immediately
        if user.free_posts_remaining > 0:
            user.free_posts_remaining -= 1
            user.save()
            form.instance.paid_for = True
            form.instance.is_active = True
            new_listing = form.save()
            files = self.request.FILES.getlist('image')
            for i, new_image in enumerate(files):
                ListingImage.objects.create(listing=new_listing, image=new_image)
            return super().form_valid(form)

        # Paid flow: save listing as a draft/unpublished, persist images, then redirect to Stripe Checkout
        form.instance.paid_for = False
        form.instance.is_active = False
        new_listing = form.save()

        files = self.request.FILES.getlist('image')
        for i, new_image in enumerate(files):
            ListingImage.objects.create(listing=new_listing, image=new_image)

        # Create Stripe Checkout Session
        stripe.api_key = settings.STRIPE_SECRET_KEY
        success_url = self.request.build_absolute_uri(reverse('marketplace:stripe_success')) + f'?listing_id={new_listing.id}'
        cancel_url = self.request.build_absolute_uri(reverse('marketplace:create_listing'))

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Listing'},
                    'unit_amount': 499,  # cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={'listing_id': str(new_listing.id)},
        )

        return redirect(session.url, code=303)

    # def form_valid(self, form):
    #     # Here you can add any additional processing before saving the form
    #     print("Creating new listing.")
    #     user = User.objects.get(id=self.request.user.id)
    #     form.instance.user = user
    #     if user.free_posts_remaining > 0:
    #         user.free_posts_remaining -= 1
    #         user.save()
    #     else: 
    #         # want to add stripe payment processing here before allowing the listing to be created
    #         checkout_session = stripe.checkout.Session.create(
    #             payment_method_types=['card'],
    #             line_items=[{
    #                 'price_data': {
    #                     'currency': 'usd',
    #                     'product_data': {
    #                         'name': 'Listing',
    #                     },
    #                     'unit_amount': 499,  # Amount in cents ($1.00)
    #                 },
    #                 'quantity': 1,
    #             }],
    #             mode='payment',
    #         )

    #     new_listing = form.save()

    #     files = self.request.FILES.getlist('image')  # Matches the 'name' in your form/HTML

    #     print(f"files: {files}")
    #     if form.is_valid():
    #         for i, new_image in enumerate(files):
    #             print(f"image {i}: {new_image}")
    #             ListingImage.objects.create(listing=new_listing, image=new_image)

    #     # if p_form.is_valid():
    #     #     product_instance = p_form.save()
    #     #     for f in files:
    #     #         ProductImage.objects.create(product=product_instance, image=f)
    #     return super().form_valid(form)

class AccountListingsView(LoginRequiredMixin, TemplateView):
    template_name = "marketplace/account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(id=self.request.user.id)
        context['user'] = user
        context['tab'] = Tabs.LISTINGS
        # context['listings'] = Listing.objects.filter(user=user).order_by('-date_posted')
        listings = Listing.objects.filter(user=user, paid_for=True).order_by('-date_posted')

        # add pagination
        paginator = Paginator(listings, 12)  # 10 items per page
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context

class EditListingView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Listing
    template_name = "marketplace/edit_listing.html"
    # fields = ['title', 'description', 'category', 'subcategory', 'price', 'city', 'image']
    fields = ['title', 'description', 'category', 'subcategory', 'price', 'city', 'email', 'phone']
    success_url = '/account/'
    success_message = "Your listing was updated successfully. The changes are now live."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = FL_CITIES
        context['categories'] = ListingCategory.choices
        context["tab"] = Tabs.LISTINGS 
        
        # will need to change this to be dynamic based on the category of the listing
        context['subcategories'] = ForSaleSubCategory.choices
        return context

    def form_valid(self, form):
        print("Updating listing.")
        user = User.objects.get(id=self.request.user.id)
        form.instance.user = user

        new_listing = form.save()

        files = self.request.FILES.getlist('image')  # Matches the 'name' in your form/HTML

        print(f"files: {files}")
        existing_images = ListingImage.objects.filter(listing=new_listing)
        if form.is_valid():
            for i, new_image in enumerate(files):
                # want to update existing images if they exist, otherwise create new ones
                if i < len(existing_images):
                    existing_image = existing_images[i]
                    existing_image.image = new_image
                    existing_image.save()
                else:
                    print(f"image {i}: {new_image}")
                    ListingImage.objects.create(listing=new_listing, image=new_image)

        return super().form_valid(form)
        # # Here you can add any additional processing before saving the form
        # print("form submitted.")
        # user = User.objects.get(id=self.request.user.id)
        # form.instance.user = user
        # return super().form_valid(form)

class DeleteListingView(LoginRequiredMixin, DeleteView):
    model = Listing
    template_name = "marketplace/delete_listing.html"
    success_url = '/account/'

class ReplyCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Reply
    fields = ['message']
    template_name = "marketplace/reply_form.html"
    success_message = "Your message has been sent to the seller. You can see this message and send more to negotiate with the seller in your account messages."

    def get_success_url(self):
        # Access the newly created or updated object via self.object
        # Use reverse_lazy for URL reversing in get_success_url

        # url = reverse_lazy('marketplace:listing_detail', kwargs={'pk': self.kwargs.get('listing_id')})
        # params = urlencode({'notification': 'success'})
        # return f"{url}?{params}"
        return reverse_lazy('marketplace:listing_detail', kwargs={'pk': self.kwargs.get('listing_id')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listing = Listing.objects.get(id=self.kwargs.get('listing_id'))
        context['listing'] = listing
        return context

    def form_valid(self, form):
        listing_id = self.kwargs.get('listing_id')
        listing = Listing.objects.get(id=listing_id)
        form.instance.listing = listing
        form.instance.sender = self.request.user
        form.instance.recipient = listing.user
        # messages.success(self.request, self.success_message)
        # new_conversation = Conversation.objects.create(listing=listing, user1=listing.user, user2=self.request.user)
        # form.instance.conversation = new_conversation
        # new_conversation.save()

        return super().form_valid(form)

class RepliesListView(LoginRequiredMixin, ListView):
    model = Reply
    template_name = "marketplace/replies_list.html"
    context_object_name = "replies"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listing_id = self.kwargs.get('listing_id')
        listing = Listing.objects.get(id=listing_id)
        context["tab"] = Tabs.MESSAGES 
        context["listing"] = listing
        return context


    def get_queryset(self):
        # this will be viewed only by the seller,
        # so should only show messages from other users,
        # clicking on a reply should show the whole conversation,
        # including messages from the seller in response
        listing_id = self.kwargs.get('listing_id')
        user = self.request.user
        return Reply.objects.filter(listing__id=listing_id).exclude(sender=user).order_by('-date_sent')

class ConversationDetailView(LoginRequiredMixin, TemplateView):
    # model = Conversation
    template_name = "marketplace/conversation_detail.html"
    context_object_name = "conversation"

    def get_context_data(self, **kwargs):
        user = self.request.user
        listing_id = self.kwargs.get('listing_id')
        sender_id = self.kwargs.get('sender_id')
        sender = User.objects.get(id=sender_id)
        # gets all messages in the conversation between the sender and recipient for the specific listing, ordered by date sent
        replies = Reply.objects.filter(listing__id=listing_id).filter(sender__in=[user, sender]).filter(recipient__in=[user, sender]).order_by('-date_sent')
        context = super().get_context_data(**kwargs)
        context["replies"] = replies 

        # want to mark as read by either the sender or recipient, 
        # depending on the user that clicked it
        reply_id = self.request.GET.get('reply_id', '')

        if reply_id:
            reply = Reply.objects.get(id=reply_id)
            reply.mark_read_by_user(user)

        listing = Listing.objects.get(id=listing_id)

        context["listing"] = listing
        context["tab"] = Tabs.MESSAGES 
        context["sender_id"] = sender_id
        return context

class ConversationReplyCreate(LoginRequiredMixin, CreateView):
    model = Reply
    fields = ['message']

    def get_success_url(self):
        listing_id = self.kwargs.get('listing_id')
        sender_id = self.kwargs.get('sender_id')
        return reverse_lazy('marketplace:conversation_detail', kwargs={'listing_id': listing_id, "sender_id": sender_id})

    def form_valid(self, form):
        listing_id = self.kwargs.get('listing_id')
        recipient_id = self.kwargs.get('sender_id')
        listing = Listing.objects.get(id=listing_id)
        form.instance.listing = listing
        form.instance.sender = self.request.user
        form.instance.recipient = User.objects.get(id=recipient_id)
        return super().form_valid(form)


class AccountInfoView(LoginRequiredMixin, TemplateView):
    template_name = "marketplace/account_info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tab"] = Tabs.INFO 
        user = User.objects.get(id=self.request.user.id)
        context["user"] = user
        return context

class AccountMessagesView(LoginRequiredMixin, TemplateView):
    template_name = "marketplace/account_messages.html"

    def get_context_data(self, **kwargs):
        # get all replies that have been sent to the 
        # current user in all conversations, excluding
        # those sent by the user (show current user's inbox)
        context = super().get_context_data(**kwargs)
        context["tab"] = Tabs.MESSAGES 
        user = self.request.user


        filter_by_sent = self.request.GET.get('filter', '')

        if filter_by_sent:
            context["message_tab"] = "sent"
            messages = user.sent.all().order_by('-date_sent')
            # add pagination
            paginator = Paginator(messages, 30)  # 30 items per page
            page_number = self.request.GET.get('page')
            context['page_obj'] = paginator.get_page(page_number)
            # context["messages"] = user.sent.all().order_by('-date_sent')
        else:
            context["message_tab"] = "received"
            # context["messages"] = user.received.all().order_by('-date_sent')
            messages = user.received.all().order_by('-date_sent')
            # add pagination
            paginator = Paginator(messages, 30)  # 30 items per page
            page_number = self.request.GET.get('page')
            context['page_obj'] = paginator.get_page(page_number)

        return context